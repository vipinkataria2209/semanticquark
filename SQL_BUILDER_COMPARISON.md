# SQL Query Builder Comparison: Cube.js vs SemanticQuark

## Executive Summary

This document compares the SQL Query Builder implementations in **Cube.js** and **SemanticQuark** to identify missing features and capabilities.

**Cube.js BaseQuery.js:** ~5,240 lines of comprehensive SQL generation logic  
**SemanticQuark SQLBuilder:** ~394 lines of basic SQL generation

---

## Feature Comparison Matrix

| Feature | Cube.js | SemanticQuark | Status |
|---------|---------|---------------|--------|
| **Basic SQL Generation** |
| SELECT clause | ✅ | ✅ | ✅ Implemented |
| FROM clause | ✅ | ✅ | ✅ Implemented |
| WHERE clause | ✅ | ✅ | ✅ Implemented |
| GROUP BY clause | ✅ | ✅ | ✅ Implemented |
| ORDER BY clause | ✅ | ✅ | ✅ Implemented |
| LIMIT/OFFSET | ✅ | ✅ | ✅ Implemented |
| JOINs (multi-cube) | ✅ | ✅ | ✅ Implemented |
| **Advanced SQL Features** |
| HAVING clause | ✅ | ❌ | ❌ **MISSING** |
| CTEs (WITH clauses) | ✅ | ❌ | ❌ **MISSING** |
| Subqueries | ✅ | ❌ | ❌ **MISSING** |
| Window functions | ✅ | ❌ | ❌ **MISSING** |
| GROUPING SETS | ✅ | ❌ | ❌ **MISSING** |
| ROLLUP | ✅ | ❌ | ❌ **MISSING** |
| CUBE | ✅ | ❌ | ❌ **MISSING** |
| **Query Types** |
| Time series queries | ✅ | ❌ | ❌ **MISSING** |
| Rolling window joins | ✅ | ❌ | ❌ **MISSING** |
| Multi-stage queries | ✅ | ❌ | ❌ **MISSING** |
| Ungrouped queries | ✅ | ❌ | ❌ **MISSING** |
| **Filter Support** |
| Dimension filters (WHERE) | ✅ | ✅ | ✅ Implemented |
| Measure filters (HAVING) | ✅ | ❌ | ❌ **MISSING** |
| Logical operators (AND/OR) | ✅ | ✅ | ✅ Implemented |
| Segment filters | ✅ | ❌ | ❌ **MISSING** |
| **Pre-Aggregation Integration** |
| Pre-aggregation routing | ✅ | ⚠️ | ⚠️ Basic |
| Rollup matching | ✅ | ❌ | ❌ **MISSING** |
| Pre-aggregation SQL generation | ✅ | ❌ | ❌ **MISSING** |
| **Database Dialects** |
| PostgreSQL | ✅ | ✅ | ✅ Implemented |
| MySQL | ✅ | ✅ | ✅ Implemented |
| Snowflake | ✅ | ❌ | ❌ **MISSING** |
| BigQuery | ✅ | ❌ | ❌ **MISSING** |
| Redshift | ✅ | ❌ | ❌ **MISSING** |
| SQL Server | ✅ | ❌ | ❌ **MISSING** |
| Oracle | ✅ | ❌ | ❌ **MISSING** |
| PrestoDB | ✅ | ❌ | ❌ **MISSING** |
| ClickHouse | ✅ | ❌ | ❌ **MISSING** |
| **Query Optimization** |
| Filter selectivity | ✅ | ❌ | ❌ **MISSING** |
| JOIN order optimization | ✅ | ❌ | ❌ **MISSING** |
| Predicate pushdown | ✅ | ❌ | ❌ **MISSING** |
| Query rewriting | ✅ | ❌ | ❌ **MISSING** |
| **Advanced Features** |
| Parameter allocation | ✅ | ❌ | ❌ **MISSING** |
| SQL injection protection | ✅ | ⚠️ | ⚠️ Basic |
| Join hints | ✅ | ❌ | ❌ **MISSING** |
| Custom SQL expressions | ✅ | ⚠️ | ⚠️ Limited |
| Timezone handling | ✅ | ⚠️ | ⚠️ Basic |
| Date series generation | ✅ | ❌ | ❌ **MISSING** |

---

## Detailed Feature Analysis

### 1. HAVING Clause Support ❌ **CRITICAL MISSING**

**Cube.js:**
- Separates dimension filters (WHERE) from measure filters (HAVING)
- `baseHaving()` method generates HAVING clause for measure filters
- Filters are categorized: `filters` → WHERE, `measureFilters` → HAVING

**SemanticQuark:**
- All filters go to WHERE clause
- No distinction between dimension and measure filters
- Cannot filter on aggregated measures

**Impact:** Cannot filter query results based on aggregated measure values (e.g., "show only orders where total_revenue > 1000")

**Example Cube.js:**
```javascript
// Measure filter goes to HAVING
{
  measures: ['orders.total_revenue'],
  filters: [
    { member: 'orders.total_revenue', operator: 'gt', values: [1000] }
  ]
}
// Generates: SELECT ... HAVING SUM(orders.total_amount) > 1000
```

**SemanticQuark Current:**
```python
# All filters go to WHERE
# Cannot filter on aggregated measures
```

---

### 2. CTEs (Common Table Expressions) ❌ **MISSING**

**Cube.js:**
- Supports `WITH` clauses for CTEs
- `withQueries()` method generates CTE definitions
- Used for complex multi-stage queries

**SemanticQuark:**
- No CTE support
- Cannot break complex queries into reusable parts

**Impact:** Cannot write complex queries that need intermediate results

**Example Cube.js:**
```sql
WITH 
  base_query AS (SELECT ...),
  aggregated AS (SELECT ... FROM base_query)
SELECT ... FROM aggregated
```

---

### 3. Subqueries ❌ **MISSING**

**Cube.js:**
- `newSubQuery()` creates subquery instances
- `subQueryDimensions` for dimensions requiring subqueries
- Used for complex aggregations and joins

**SemanticQuark:**
- No subquery support
- Cannot nest queries

**Impact:** Limited query complexity

---

### 4. Window Functions ❌ **MISSING**

**Cube.js:**
- Supports window functions with `PARTITION BY`, `ORDER BY`, frame clauses
- `window_function` template in SQL templates
- Used for cumulative measures, running totals, etc.

**SemanticQuark:**
- No window function support

**Impact:** Cannot calculate running totals, moving averages, rankings

**Example Cube.js:**
```sql
SUM(revenue) OVER (PARTITION BY customer_id ORDER BY order_date)
```

---

### 5. Time Series Queries ❌ **MISSING**

**Cube.js:**
- `dateSeriesSql()` generates date series tables
- `seriesSql()` creates time series data
- `overTimeSeriesQuery()` for time-based aggregations
- Fills gaps in time series data

**SemanticQuark:**
- No time series generation
- Missing dates in time series are not filled

**Impact:** Time series charts may have gaps

---

### 6. Multi-Stage Queries ❌ **MISSING**

**Cube.js:**
- `multiStageQuery` option
- `multiStageDimensions` and `multiStageTimeDimensions`
- Allows complex query pipelines

**SemanticQuark:**
- Single-stage queries only

**Impact:** Cannot build complex analytical queries

---

### 7. Measure Filters (HAVING) ❌ **CRITICAL MISSING**

**Cube.js:**
- Separates `filters` (dimension filters → WHERE) from `measureFilters` (measure filters → HAVING)
- `extractDimensionsAndMeasures()` categorizes filters
- Prevents mixing dimension and measure filters in same logical operator

**SemanticQuark:**
- All filters treated as dimension filters
- No measure filter support

**Impact:** Cannot filter on aggregated results

---

### 8. Segment Support ❌ **MISSING**

**Cube.js:**
- `segments` array in query
- `segmentSql()` generates segment SQL
- Segments are pre-defined filter combinations

**SemanticQuark:**
- No segment support

**Impact:** Cannot reuse common filter combinations

---

### 9. GROUPING SETS / ROLLUP / CUBE ❌ **MISSING**

**Cube.js:**
- Supports `ROLLUP`, `CUBE`, `GROUPING SETS`
- SQL templates include these features
- Used for multi-level aggregations

**SemanticQuark:**
- Standard GROUP BY only

**Impact:** Cannot generate multi-level summary reports

---

### 10. Pre-Aggregation Integration ⚠️ **PARTIAL**

**Cube.js:**
- Deep integration with pre-aggregations
- `preAggregations.rollupPreAggregation()` matches queries to pre-aggregations
- Generates SQL from pre-aggregation definitions
- Handles pre-aggregation refresh

**SemanticQuark:**
- Basic pre-aggregation support
- No rollup matching
- No pre-aggregation SQL generation

**Impact:** Pre-aggregations not fully utilized

---

### 11. Parameter Allocation ❌ **MISSING**

**Cube.js:**
- `ParamAllocator` class for parameterized queries
- Prevents SQL injection
- Optimizes query caching

**SemanticQuark:**
- Direct string interpolation
- Basic SQL injection protection

**Impact:** Security and caching limitations

---

### 12. Query Optimization ❌ **MISSING**

**Cube.js:**
- Filter selectivity analysis
- JOIN order optimization
- Predicate pushdown
- Query rewriting

**SemanticQuark:**
- Basic duplicate removal
- No selectivity analysis
- No JOIN optimization

**Impact:** Suboptimal query performance

---

### 13. Database Dialects ❌ **LIMITED**

**Cube.js:**
- 20+ database dialects
- Dialect-specific SQL generation
- Handles database-specific features

**SemanticQuark:**
- PostgreSQL and MySQL only
- Basic dialect support

**Impact:** Limited database compatibility

---

### 14. Join Hints ❌ **MISSING**

**Cube.js:**
- `joinHints` for join optimization
- `collectJoinHints()` gathers join requirements
- Optimizes join order

**SemanticQuark:**
- Simple join pathfinding
- No join hints

**Impact:** Suboptimal join performance

---

### 15. Ungrouped Queries ❌ **MISSING**

**Cube.js:**
- `ungrouped` option for queries without GROUP BY
- Requires primary keys when ungrouped
- Used for detail queries

**SemanticQuark:**
- Always uses GROUP BY when measures present

**Impact:** Cannot query raw data without aggregation

---

## Priority Recommendations

### 🔴 **Critical (Must Have)**

1. **HAVING Clause Support**
   - Separate dimension filters (WHERE) from measure filters (HAVING)
   - Implement `measureFilters` in Query model
   - Add `baseHaving()` method to SQLBuilder

2. **Parameter Allocation**
   - Implement `ParamAllocator` class
   - Replace string interpolation with parameterized queries
   - Improve security and caching

### 🟡 **High Priority (Should Have)**

3. **Subqueries**
   - Add `newSubQuery()` method
   - Support nested queries
   - Enable complex aggregations

4. **CTEs (WITH Clauses)**
   - Add `withQueries()` method
   - Support multi-stage query building

5. **Time Series Queries**
   - Implement `dateSeriesSql()`
   - Fill gaps in time series data

### 🟢 **Medium Priority (Nice to Have)**

6. **Window Functions**
   - Add window function support
   - Enable cumulative measures

7. **Segment Support**
   - Add segments to Query model
   - Implement `segmentSql()` method

8. **Query Optimization**
   - Filter selectivity analysis
   - JOIN order optimization

---

## Implementation Roadmap

### Phase 1: Critical Features (2-3 weeks)
- [ ] HAVING clause support
- [ ] Parameter allocation
- [ ] Measure filters

### Phase 2: High Priority (4-6 weeks)
- [ ] Subqueries
- [ ] CTEs
- [ ] Time series queries

### Phase 3: Advanced Features (8-12 weeks)
- [ ] Window functions
- [ ] Segment support
- [ ] Query optimization
- [ ] Additional database dialects

---

## Code Examples

### Cube.js HAVING Clause Implementation

```javascript
baseHaving(measureFilters) {
  if (!measureFilters || !measureFilters.length) {
    return '';
  }
  const having = this.measureFiltersSql(measureFilters);
  return having ? ` HAVING ${having}` : '';
}

measureFiltersSql(measureFilters) {
  return measureFilters
    .map(f => this.newFilter(f).filterSql())
    .filter(f => !!f)
    .join(' AND ');
}
```

### SemanticQuark Missing Implementation

```python
# TODO: Implement HAVING clause support
def build_having_clause(self, query: Query) -> str:
    """Build HAVING clause for measure filters."""
    # Currently missing - all filters go to WHERE
    pass
```

---

## Conclusion

SemanticQuark's SQL Builder has **solid fundamentals** but is missing **critical advanced features** that Cube.js provides:

- ✅ **Good:** Basic SQL generation, JOINs, filters, logical operators
- ❌ **Missing:** HAVING clause, subqueries, CTEs, window functions, time series
- ⚠️ **Partial:** Pre-aggregations, optimization, dialects

**Recommendation:** Focus on implementing HAVING clause support and parameter allocation first, as these are critical for production use and security.

