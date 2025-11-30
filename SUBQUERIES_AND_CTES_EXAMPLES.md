# Subqueries and CTEs: Cube.js vs SemanticQuark

## Overview

This document shows concrete examples of how **Cube.js** implements subqueries and CTEs (Common Table Expressions), and what's missing in **SemanticQuark**.

---

## 1. CTEs (Common Table Expressions / WITH Clauses)

### Cube.js Implementation

**Code Location:** `BaseQuery.js:1458-1464`

```javascript
withQueries(select, withQueries) {
  if (!withQueries || !withQueries.length) {
    return select;
  }
  // TODO escape alias
  return `WITH\n${withQueries.map(q => `${q.alias} AS (${q.query})`).join(',\n')}\n${select}`;
}
```

**SQL Template:** `BaseQuery.js:4321-4336`

```javascript
select: '{% if ctes %} WITH \n' +
  '{{ ctes | join(\',\n\') }}\n' +
  '{% endif %}' +
  'SELECT {% if distinct %}DISTINCT {% endif %}' +
  '{{ select_concat | map(attribute=\'aliased\') | join(\', \') }} ...'
```

### Example: Multi-Stage Query with CTEs

**Cube.js Query:**
```javascript
{
  measures: ['orders.total_revenue', 'orders.count'],
  dimensions: ['orders.status'],
  timeDimensions: [{
    dimension: 'orders.created_at',
    granularity: 'month'
  }]
}
```

**Generated SQL (with CTEs):**
```sql
WITH
  main AS (
    SELECT 
      DATE_TRUNC('month', orders.created_at) AS orders_created_at_month,
      orders.status,
      SUM(orders.total_amount) AS orders_total_revenue,
      COUNT(orders.id) AS orders_count
    FROM orders
    WHERE orders.created_at >= '2024-01-01'
      AND orders.created_at <= '2024-12-31'
    GROUP BY 
      DATE_TRUNC('month', orders.created_at),
      orders.status
  ),
  aggregated AS (
    SELECT 
      orders_created_at_month,
      orders_status,
      SUM(orders_total_revenue) AS total_revenue,
      SUM(orders_count) AS total_count
    FROM main
    GROUP BY orders_created_at_month, orders_status
  )
SELECT 
  orders_created_at_month,
  orders_status,
  total_revenue,
  total_count
FROM aggregated
ORDER BY orders_created_at_month DESC
```

### Use Cases for CTEs

1. **Multi-Stage Aggregations:**
   - First CTE: Aggregate by day
   - Second CTE: Aggregate by month from day-level data
   - Final SELECT: Query from month-level CTE

2. **Complex Joins:**
   - CTE 1: Filter and aggregate orders
   - CTE 2: Filter and aggregate customers
   - Final: Join both CTEs

3. **Pre-Aggregation Matching:**
   - CTE: Query from pre-aggregation table
   - Final: Apply additional filters/aggregations

---

## 2. Subqueries

### Cube.js Implementation

**Code Location:** `BaseQuery.js:1803-1820`

```javascript
newSubQuery(subQueryOptions) {
  const subQuery = this.newSubQuery(subQueryOptions);
  
  return {
    query: subQuery.evaluateSymbolSqlWithContext(
      () => subQuery.buildParamAnnotatedSql(),
      renderedReferenceContext,
    ),
    alias: withQuery.alias
  };
}
```

**Subquery Join:** `BaseQuery.js:2323-2339`

```javascript
subQueryJoin(dimension) {
  const { prefix, subQuery, cubeName } = this.subQueryDescription(dimension);
  const primaryKeys = this.cubeEvaluator.primaryKeys[cubeName];
  const subQueryAlias = this.escapeColumnName(this.aliasName(prefix));

  const sql = subQuery.evaluateSymbolSqlWithContext(
    () => subQuery.buildParamAnnotatedSql(),
    { collectOriginalSqlPreAggregations }
  );
  const onCondition = primaryKeys.map((pk) => 
    `${subQueryAlias}.${this.newDimension(this.primaryKeyName(cubeName, pk)).aliasName()} = ${this.primaryKeySql(pk, cubeName)}`
  );

  return {
    sql: `(${sql})`,
    alias: subQueryAlias,
    on: onCondition.join(' AND ')
  };
}
```

### Example 1: Subquery in FROM Clause

**Cube.js Query:**
```javascript
{
  measures: ['orders.total_revenue'],
  dimensions: ['customers.city'],
  filters: [{
    member: 'orders.total_revenue',
    operator: 'gt',
    values: [1000]
  }]
}
```

**Generated SQL:**
```sql
SELECT 
  customers.city,
  SUM(subquery_orders.total_revenue) AS orders_total_revenue
FROM customers
LEFT JOIN (
  SELECT 
    orders.customer_id,
    SUM(orders.total_amount) AS total_revenue
  FROM orders
  WHERE orders.created_at >= '2024-01-01'
  GROUP BY orders.customer_id
  HAVING SUM(orders.total_amount) > 1000
) AS subquery_orders ON customers.id = subquery_orders.customer_id
GROUP BY customers.city
```

### Example 2: Subquery for Complex Dimensions

**Cube.js Query:**
```javascript
{
  measures: ['orders.total_revenue'],
  dimensions: ['orders.customer_lifetime_value'],  // Complex calculated dimension
  timeDimensions: [{
    dimension: 'orders.created_at',
    granularity: 'month'
  }]
}
```

**Generated SQL:**
```sql
SELECT 
  DATE_TRUNC('month', orders.created_at) AS orders_created_at_month,
  customer_lifetime_value_subquery.lifetime_value AS orders_customer_lifetime_value,
  SUM(orders.total_amount) AS orders_total_revenue
FROM orders
LEFT JOIN (
  SELECT 
    customer_id,
    SUM(total_amount) AS lifetime_value
  FROM orders
  GROUP BY customer_id
) AS customer_lifetime_value_subquery 
  ON orders.customer_id = customer_lifetime_value_subquery.customer_id
WHERE orders.created_at >= '2024-01-01'
  AND orders.created_at <= '2024-12-31'
GROUP BY 
  DATE_TRUNC('month', orders.created_at),
  customer_lifetime_value_subquery.lifetime_value
```

### Example 3: Subquery for Measure Filters (HAVING)

**Cube.js Query:**
```javascript
{
  measures: ['orders.total_revenue'],
  dimensions: ['orders.status'],
  filters: [{
    member: 'orders.total_revenue',
    operator: 'gt',
    values: [5000]
  }]
}
```

**Generated SQL:**
```sql
SELECT 
  orders.status,
  SUM(orders.total_amount) AS orders_total_revenue
FROM orders
GROUP BY orders.status
HAVING SUM(orders.total_amount) > 5000
```

**Note:** This uses HAVING, but if the filter needs to be in WHERE (for drill-downs), Cube.js uses a subquery:

```sql
SELECT 
  orders.status,
  SUM(orders.total_amount) AS orders_total_revenue
FROM (
  SELECT 
    orders.status,
    orders.total_amount
  FROM orders
  WHERE orders.total_amount > 5000  -- Filter in subquery WHERE
) AS filtered_orders
GROUP BY orders.status
```

---

## 3. Regular Measures Subquery

**Code Location:** `BaseQuery.js:2409-2426`

```javascript
regularMeasuresSubQuery(measures, filters) {
  filters = filters || this.allFilters;

  const inlineWhereConditions = [];
  const query = this.rewriteInlineWhere(() => this.joinQuery(
    this.join,
    this.collectFrom(
      this.dimensionsForSelect().concat(measures).concat(this.allFilters),
      this.collectSubQueryDimensionsFor.bind(this),
      'collectSubQueryDimensionsFor'
    )
  ), inlineWhereConditions);

  return `SELECT ${this.selectAllDimensionsAndMeasures(measures)} FROM ${query
  } ${this.baseWhere(filters.concat(inlineWhereConditions))}` +
    (!this.safeEvaluateSymbolContext().ungrouped && this.groupByClause() || '');
}
```

**Example Generated SQL:**
```sql
SELECT 
  orders.status,
  SUM(orders.total_amount) AS orders_total_revenue,
  COUNT(orders.id) AS orders_count
FROM (
  SELECT 
    orders.status,
    orders.total_amount,
    orders.id
  FROM orders
  WHERE orders.created_at >= '2024-01-01'
) AS subquery
GROUP BY orders.status
```

---

## 4. Aggregate Subquery

**Code Location:** `BaseQuery.js:2435-2508`

```javascript
aggregateSubQuery(keyCubeName, measures, filters) {
  filters = filters || this.allFilters;
  const primaryKeyDimensions = this.primaryKeyNames(keyCubeName).map((k) => this.newDimension(k));
  const shouldBuildJoinForMeasureSelect = this.checkShouldBuildJoinForMeasureSelect(measures, keyCubeName);

  // ... complex logic for building subquery with joins ...
  
  return `SELECT ${forSelect} FROM ${keyCubeSql} ${join} ${this.baseWhere(filters)}` +
    this.groupByClause() +
    this.baseHaving(this.measureFilters);
}
```

**Example: Multi-Cube Query with Subqueries**

**Cube.js Query:**
```javascript
{
  measures: [
    'orders.total_revenue',
    'customers.count'
  ],
  dimensions: ['orders.status'],
  timeDimensions: [{
    dimension: 'orders.created_at',
    granularity: 'month'
  }]
}
```

**Generated SQL:**
```sql
SELECT 
  orders.status,
  DATE_TRUNC('month', orders.created_at) AS orders_created_at_month,
  SUM(orders_subquery.total_revenue) AS orders_total_revenue,
  COUNT(customers_subquery.customer_id) AS customers_count
FROM orders
LEFT JOIN (
  SELECT 
    orders.id,
    SUM(orders.total_amount) AS total_revenue
  FROM orders
  GROUP BY orders.id
) AS orders_subquery ON orders.id = orders_subquery.id
LEFT JOIN (
  SELECT 
    customers.id AS customer_id,
    customers.id
  FROM customers
  GROUP BY customers.id
) AS customers_subquery ON orders.customer_id = customers_subquery.customer_id
WHERE orders.created_at >= '2024-01-01'
GROUP BY 
  orders.status,
  DATE_TRUNC('month', orders.created_at)
```

---

## 5. Current SemanticQuark Implementation

### What We Have

**File:** `semantic_layer/sql/builder.py`

```python
def build(self, query: Query, security_context: Optional[SecurityContext] = None) -> str:
    """Build SQL query from semantic query."""
    # ... basic SQL generation ...
    
    # Assemble SQL
    sql_parts = [
        "SELECT",
        ", ".join(select_parts),
        from_clause,
        join_clauses,
        where_clause,
        group_by_clause,
        order_by_clause,
        limit_clause,
    ]
    
    sql = " ".join(filter(None, sql_parts))
    return sql
```

**Current Output:**
```sql
SELECT 
  orders.status,
  SUM(orders.total_amount) AS orders_total_revenue
FROM orders AS t0
WHERE orders.created_at >= '2024-01-01'
GROUP BY orders.status
ORDER BY orders_total_revenue DESC
LIMIT 100
```

### What's Missing

1. **No CTE Support:**
   - Cannot generate `WITH` clauses
   - Cannot break complex queries into reusable parts

2. **No Subquery Support:**
   - Cannot nest queries
   - Cannot use subqueries in JOINs
   - Cannot use subqueries for complex dimensions

3. **No Multi-Stage Queries:**
   - Cannot build query pipelines
   - Cannot aggregate on top of aggregations

---

## 6. Implementation Examples for SemanticQuark

### Example 1: Adding CTE Support

**Proposed Implementation:**

```python
class SQLBuilder:
    def __init__(self, schema: Schema):
        self.schema = schema
        self.with_queries: List[Dict[str, str]] = []  # List of {alias: str, query: str}
    
    def add_with_query(self, alias: str, query: str) -> None:
        """Add a CTE to the query."""
        self.with_queries.append({"alias": alias, "query": query})
    
    def build_with_clause(self) -> str:
        """Build WITH clause from CTEs."""
        if not self.with_queries:
            return ""
        
        cte_definitions = [
            f"{cte['alias']} AS ({cte['query']})"
            for cte in self.with_queries
        ]
        return f"WITH\n{',\n'.join(cte_definitions)}\n"
    
    def build(self, query: Query, security_context: Optional[SecurityContext] = None) -> str:
        """Build SQL query from semantic query."""
        # ... existing code ...
        
        # Build WITH clause if CTEs exist
        with_clause = self.build_with_clause()
        
        # Assemble SQL
        sql_parts = [
            with_clause,  # Add WITH clause
            "SELECT",
            ", ".join(select_parts),
            from_clause,
            join_clauses,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause,
        ]
        
        sql = " ".join(filter(None, sql_parts))
        return sql
```

**Usage Example:**
```python
builder = SQLBuilder(schema)

# Add CTE for base aggregation
base_query = """
  SELECT 
    DATE_TRUNC('month', created_at) AS month,
    status,
    SUM(total_amount) AS revenue
  FROM orders
  GROUP BY month, status
"""
builder.add_with_query("monthly_orders", base_query)

# Build final query using CTE
query = Query(
    measures=["monthly_orders.revenue"],
    dimensions=["monthly_orders.status"]
)
sql = builder.build(query)
```

**Generated SQL:**
```sql
WITH
monthly_orders AS (
  SELECT 
    DATE_TRUNC('month', created_at) AS month,
    status,
    SUM(total_amount) AS revenue
  FROM orders
  GROUP BY month, status
)
SELECT 
  status,
  SUM(revenue) AS monthly_orders_revenue
FROM monthly_orders
GROUP BY status
```

### Example 2: Adding Subquery Support

**Proposed Implementation:**

```python
class SQLBuilder:
    def new_subquery(self, subquery_options: Dict[str, Any]) -> 'SQLBuilder':
        """Create a new subquery builder."""
        # Create a new SQLBuilder instance with subquery context
        subquery_builder = SQLBuilder(self.schema)
        subquery_builder.is_subquery = True
        subquery_builder.cube_alias_prefix = subquery_options.get('cube_alias_prefix', 'subquery')
        return subquery_builder
    
    def build_subquery_join(self, dimension: str) -> JoinInfo:
        """Build a subquery join for a complex dimension."""
        cube, dim_name = self.schema.get_cube_for_dimension(dimension)
        dimension_obj = cube.get_dimension(dim_name)
        
        # Check if dimension requires subquery (e.g., calculated dimension)
        if dimension_obj.requires_subquery:
            # Create subquery
            subquery_options = {
                'cube_alias_prefix': f"{cube.name}_{dim_name}_subquery",
                'measures': [dimension_obj.sql],  # Use dimension SQL as measure
                'dimensions': cube.primary_keys,
                'filters': self._extract_filters_for_subquery(dimension)
            }
            subquery_builder = self.new_subquery(subquery_options)
            subquery_sql = subquery_builder.build(Query(**subquery_options))
            
            # Build join condition
            primary_keys = cube.primary_keys
            join_conditions = [
                f"{self.cube_alias_prefix}.{pk} = {subquery_options['cube_alias_prefix']}.{pk}"
                for pk in primary_keys
            ]
            
            return JoinInfo(
                cube_name=cube.name,
                table_alias=subquery_options['cube_alias_prefix'],
                join_type="LEFT JOIN",
                join_condition=" AND ".join(join_conditions),
                sql=f"({subquery_sql})"  # Subquery SQL
            )
        
        return None
```

**Usage Example:**
```python
# Query with complex dimension requiring subquery
query = Query(
    measures=["orders.total_revenue"],
    dimensions=["orders.customer_lifetime_value"]  # Complex calculated dimension
)

builder = SQLBuilder(schema)
sql = builder.build(query)
```

**Generated SQL:**
```sql
SELECT 
  orders.status,
  customer_lifetime_value_subquery.lifetime_value AS orders_customer_lifetime_value,
  SUM(orders.total_amount) AS orders_total_revenue
FROM orders AS t0
LEFT JOIN (
  SELECT 
    customer_id,
    SUM(total_amount) AS lifetime_value
  FROM orders
  GROUP BY customer_id
) AS customer_lifetime_value_subquery 
  ON t0.customer_id = customer_lifetime_value_subquery.customer_id
GROUP BY 
  orders.status,
  customer_lifetime_value_subquery.lifetime_value
```

---

## 7. Real-World Use Cases

### Use Case 1: Multi-Level Aggregation

**Requirement:** Aggregate daily data, then aggregate by month

**With CTEs (Cube.js):**
```sql
WITH
  daily_orders AS (
    SELECT 
      DATE_TRUNC('day', created_at) AS day,
      status,
      SUM(total_amount) AS revenue
    FROM orders
    WHERE created_at >= '2024-01-01'
    GROUP BY day, status
  ),
  monthly_orders AS (
    SELECT 
      DATE_TRUNC('month', day) AS month,
      status,
      SUM(revenue) AS monthly_revenue,
      AVG(revenue) AS avg_daily_revenue
    FROM daily_orders
    GROUP BY month, status
  )
SELECT 
  month,
  status,
  monthly_revenue,
  avg_daily_revenue
FROM monthly_orders
ORDER BY month DESC
```

**Without CTEs (SemanticQuark - Current):**
```sql
-- Cannot do this - would need to run two separate queries
```

### Use Case 2: Complex Dimension with Subquery

**Requirement:** Calculate customer lifetime value in real-time

**With Subquery (Cube.js):**
```sql
SELECT 
  orders.status,
  customer_ltv.lifetime_value,
  SUM(orders.total_amount) AS revenue
FROM orders
LEFT JOIN (
  SELECT 
    customer_id,
    SUM(total_amount) AS lifetime_value
  FROM orders
  GROUP BY customer_id
) AS customer_ltv ON orders.customer_id = customer_ltv.customer_id
GROUP BY orders.status, customer_ltv.lifetime_value
```

**Without Subquery (SemanticQuark - Current):**
```sql
-- Cannot reference calculated dimension that requires aggregation
-- Would need pre-aggregation or separate query
```

### Use Case 3: Filtering on Aggregated Measures

**Requirement:** Show only customers with total revenue > $10,000

**With HAVING + Subquery (Cube.js):**
```sql
SELECT 
  customers.city,
  SUM(orders.total_amount) AS total_revenue
FROM customers
LEFT JOIN orders ON customers.id = orders.customer_id
GROUP BY customers.city
HAVING SUM(orders.total_amount) > 10000
```

**Without HAVING (SemanticQuark - Current):**
```sql
-- Cannot filter on aggregated results
-- Would need to filter in application layer (inefficient)
```

---

## 8. Impact Assessment

### Current Limitations in SemanticQuark

1. **Cannot build complex analytical queries:**
   - Multi-stage aggregations require multiple API calls
   - Application must handle intermediate results

2. **Cannot optimize query performance:**
   - No ability to break queries into optimized parts
   - Cannot use CTEs for query reuse

3. **Limited dimension support:**
   - Complex calculated dimensions require pre-aggregations
   - Cannot calculate on-the-fly with subqueries

4. **Inefficient filtering:**
   - Cannot filter on aggregated measures
   - Must filter in application (pulls all data first)

### Performance Impact

**Example: Monthly Revenue Report**

**With CTEs (Cube.js):**
- Single query execution
- Database optimizes entire query
- ~100ms execution time

**Without CTEs (SemanticQuark):**
- Multiple API calls (daily → monthly aggregation)
- Application-level aggregation
- ~500ms+ execution time (network + processing)

---

## 9. Implementation Priority

### 🔴 Critical
1. **Subquery Support** - Enables complex dimensions and measure filters
2. **CTE Support** - Enables multi-stage queries

### 🟡 High Priority
3. **Subquery Joins** - For complex dimension calculations
4. **Multi-Stage Query Builder** - For query pipelines

### 🟢 Medium Priority
5. **Query Optimization** - Using CTEs for performance
6. **Subquery Caching** - Reuse subquery results

---

## Conclusion

**Cube.js** provides comprehensive support for:
- ✅ CTEs (WITH clauses) for multi-stage queries
- ✅ Subqueries in FROM, JOIN, and WHERE clauses
- ✅ Complex dimension calculations via subqueries
- ✅ Query optimization through query decomposition

**SemanticQuark** currently lacks:
- ❌ CTE support
- ❌ Subquery support
- ❌ Multi-stage query capabilities

**Recommendation:** Implement subquery support first (enables complex dimensions), then CTE support (enables multi-stage queries).

