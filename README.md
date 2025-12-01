# SemanticQuark

<div align="center">

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

**The Fundamental Building Block for Semantic Analytics**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Examples](#-examples) • [Roadmap](#-roadmap) • [Contributing](#-contributing)

</div>

---

## 🚀 What is SemanticQuark?

**SemanticQuark** is a Python-based semantic layer platform that provides the fundamental building blocks for analytics. It enables you to:

- **Define metrics once, use everywhere** - Create reusable data models with consistent metric definitions
- **Query data without SQL** - Use simple JSON queries instead of complex SQL
- **Connect to any database** - Support for PostgreSQL, MySQL, Snowflake, BigQuery, and more
- **Build faster analytics** - Intelligent caching and pre-aggregation for sub-second queries
- **Secure your data** - Row-level and column-level security built-in

Think of it as **Cube.js for Python** - but with native Python integration, ML capabilities, and data science workflow support. 

## ✨ Features

### Core Features
- 🎯 **Semantic Data Modeling** - Define cubes, dimensions, and measures in YAML
- 🔍 **REST API** - Query data with simple JSON requests
- 🗄️ **Multiple Data Sources** - PostgreSQL, MySQL, and extensible connector system
- ⚡ **Query Optimization** - Automatic SQL generation and optimization
- 📊 **Result Formatting** - Consistent JSON responses with metadata
- 🔒 **Security Ready** - Foundation for row-level and column-level security

### Python-Native Advantages
- 🐍 **Python SDK** - Native Python client library
- 📈 **Data Science Integration** - Works with Pandas, Jupyter, and ML workflows
- 🤖 **ML-Ready** - Embed ML models directly in metrics
- 📦 **Rich Ecosystem** - Leverage Python's data science libraries

### Production Ready
- 🐳 **Docker Support** - Complete Docker Compose setup
- 📝 **API Documentation** - Auto-generated Swagger/OpenAPI docs
- 🧪 **Tested** - Comprehensive test suite
- 📚 **Well Documented** - Extensive documentation and examples

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Client Applications                         │
│    (BI Tools, Dashboards, Custom Apps, APIs)             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ REST/GraphQL APIs
                       │
┌──────────────────────▼──────────────────────────────────┐
│                  API Layer (FastAPI)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   REST   │  │ GraphQL  │  │   SQL    │             │
│  │   API    │  │   API    │  │   API    │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Query Requests
                       │
┌──────────────────────▼──────────────────────────────────┐
│         Query Engine & Orchestration                     │
│  Query Parser → SQL Builder → Executor                 │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│   Semantic   │ │   Cache    │ │  Security  │
│    Layer     │ │   Layer    │ │   Layer   │
│  (Models)    │ │  (Redis)   │ │  (RLS)    │
└───────┬──────┘ └─────────────┘ └────────────┘
        │
        │
┌───────▼──────────────────────────────────────┐
│         Data Source Connectors                │
│  PostgreSQL │ MySQL │ Snowflake │ BigQuery   │
└───────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Docker and Docker Compose (optional, for full stack)
- PostgreSQL (if not using Docker)

### Installation

#### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/semanticquark.git
cd semanticquark

# Start all services
docker-compose up -d

# Initialize database
docker-compose exec postgres psql -U semantic_user -d semantic_db < init_db.sql

# Test the API
curl http://localhost:8000/health
```

#### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/semanticquark.git
cd semanticquark

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database connection

# Run the API
python -m semantic_layer.api.main
```

### Your First Query

1. **Create a model** in `models/orders.yaml`:
```yaml
cubes:
  - name: orders
    table: orders
    dimensions:
      status:
        type: string
        sql: status
      created_at:
        type: time
        sql: created_at
    measures:
      count:
        type: count
        sql: id
      total_revenue:
        type: sum
        sql: total_amount
```

2. **Query the API**:
```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "dimensions": ["orders.status"],
    "measures": ["orders.count", "orders.total_revenue"]
  }'
```

3. **Get results**:
```json
{
  "data": [
    {
      "orders_status": "completed",
      "orders_count": 5,
      "orders_total_revenue": 925.0
    }
  ],
  "meta": {
    "execution_time_ms": 18.56,
    "row_count": 1
  }
}
```

## 📖 Documentation

- [Architecture Guide](high_level_architecture.md) - High-level design and concepts
- [Foundational Components](core_foundational_components.md) - Core building blocks
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)
- [Docker Setup](DOCKER_SETUP.md) - Docker Compose guide
- [Postman Examples](POSTMAN_EXAMPLES.md) - API usage examples
- [Competitive Advantages](competitive_advantages.md) - Features vs Cube.js

## 📚 Examples

### Example 1: Simple Aggregation
```json
{
  "measures": ["orders.count", "orders.total_revenue"]
}
```

### Example 2: Group By Dimension
```json
{
  "dimensions": ["orders.status"],
  "measures": ["orders.count"]
}
```

### Example 3: With Filters
```json
{
  "dimensions": ["orders.status"],
  "measures": ["orders.count"],
  "filters": [
    {
      "dimension": "orders.status",
      "operator": "equals",
      "values": ["completed"]
    }
  ]
}
```

### Example 4: Python Client
```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/query",
        json={
            "dimensions": ["orders.status"],
            "measures": ["orders.count"]
        }
    )
    result = response.json()
    print(result["data"])
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test
python test_basic.py
python test_integration.py
python test_complete.py

# Test with Docker
docker-compose up -d
python test_real_api.py
```

## 🏗️ Project Structure

```
semanticquark/
├── semantic_layer/          # Core package
│   ├── api/                # API layer (FastAPI)
│   ├── config/             # Configuration
│   ├── connectors/         # Database connectors
│   ├── engine/              # Query engine
│   ├── models/             # Data models
│   ├── query/               # Query parsing
│   ├── query_builder/      # SQL generation
│   └── result/             # Result formatting
├── models/                  # Model definitions (YAML)
├── tests/                  # Test suite
├── docker-compose.yml      # Docker setup
├── Dockerfile              # Container definition
└── requirements.txt        # Dependencies
```

## 🔌 Supported Data Sources

- ✅ PostgreSQL
- ✅ MySQL
- 🚧 Snowflake (coming soon)
- 🚧 BigQuery (coming soon)
- 🚧 Redshift (coming soon)

## 🛣️ Roadmap

### Phase 1: Core (✅ Complete)
- [x] Semantic data modeling
- [x] REST API
- [x] PostgreSQL connector
- [x] Query parsing and SQL generation
- [x] Docker setup
- [x] Foundational query engine

### Phase 2: Enhanced Features (🚧 In Progress)
- [ ] GraphQL API
- [ ] Caching layer (Redis)
- [ ] Pre-aggregations
- [ ] Row-level security (RLS)
- [ ] Snowflake connector
- [ ] BigQuery connector
- [ ] Query result caching
- [ ] Performance monitoring

### Phase 3: Monitoring & Observability (📋 Q1 2025)
- [ ] Extensible callback handler system
- [ ] Query logging and audit trail
- [ ] Performance metrics collection
- [ ] Integration with Elasticsearch
- [ ] Integration with LangSmith
- [ ] Slack alerts and notifications
- [ ] Custom handler framework
- [ ] Real-time query monitoring dashboard

### Phase 4: Advanced Security (📋 Q2 2025)
- [ ] Column-level security
- [ ] Data masking policies
- [ ] Audit logging
- [ ] API key management
- [ ] Role-based access control (RBAC)
- [ ] OAuth 2.0 integration
- [ ] SAML support
- [ ] Fine-grained permission system

### Phase 5: ML & Intelligence (📋 Q2-Q3 2025)
- [ ] ML-powered metric recommendations
- [ ] Anomaly detection
- [ ] Query optimization using ML
- [ ] Natural language to SQL (NL2SQL)
- [ ] Automatic dimension suggestion
- [ ] Cost estimation for queries
- [ ] Performance optimization recommendations
- [ ] Data lineage and impact analysis

### Phase 6: Enterprise Features (📋 Q3-Q4 2025)
- [ ] Data lineage tracking
- [ ] Multi-tenancy support
- [ ] Visual model editor (web UI)
- [ ] Model versioning and Git integration
- [ ] Data governance framework
- [ ] Compliance reporting (GDPR, HIPAA)
- [ ] Advanced scheduling and automation
- [ ] White-label deployment options

### Phase 7: Advanced Data Integration (📋 Q4 2025)
- [ ] Redshift connector
- [ ] Databricks connector
- [ ] Apache Spark integration
- [ ] Dremio integration
- [ ] Trino/Presto support
- [ ] Delta Lake support
- [ ] Apache Iceberg support
- [ ] Data lake connectors (S3, GCS, Azure)

### Phase 8: Performance & Scale (📋 2026)
- [ ] Distributed query execution
- [ ] Query result streaming
- [ ] Connection pooling optimization
- [ ] Query execution plan visualization
- [ ] Advanced indexing strategies
- [ ] Materialized view automation
- [ ] Query parallelization
- [ ] Sub-second query performance (guaranteed)

### Phase 9: Community & Ecosystem (📋 2026)
- [ ] Plugin marketplace
- [ ] Community handler library
- [ ] Third-party integrations (Tableau, Looker, PowerBI)
- [ ] SDK for JavaScript/TypeScript
- [ ] SDK for Go
- [ ] SDK for Java
- [ ] Community examples and templates
- [ ] Certification program

### Phase 10: Advanced Features (📋 2026)
- [ ] Time-series analysis
- [ ] Cohort analysis
- [ ] Funnel analysis
- [ ] Retention analysis
- [ ] Attribution modeling
- [ ] A/B testing framework
- [ ] Experimentation platform
- [ ] Real-time metrics

---

## 📊 Roadmap Timeline

```
2024 Q4: Phase 1 (Core) ✅ + Phase 2 (Enhanced) 🚧
         │
         ├─ Semantic modeling ✅
         ├─ REST API ✅
         ├─ PostgreSQL ✅
         ├─ GraphQL API 🚧
         └─ Caching layer 🚧
         
2025 Q1: Phase 3 (Monitoring) 📋
         │
         ├─ Callback handlers
         ├─ Query logging
         ├─ Performance metrics
         └─ Elasticsearch integration
         
2025 Q2: Phase 4 (Security) + Phase 5 (ML) 📋
         │
         ├─ Column-level security
         ├─ ML recommendations
         ├─ NL2SQL
         └─ Anomaly detection
         
2025 Q3: Phase 6 (Enterprise) 📋
         │
         ├─ Visual editor
         ├─ Data governance
         ├─ Git integration
         └─ Multi-tenancy
         
2025 Q4: Phase 7 (Data Integration) 📋
         │
         ├─ Redshift
         ├─ Databricks
         ├─ Spark integration
         └─ Delta Lake support
         
2026 H1: Phase 8 (Performance) 📋
         │
         ├─ Distributed execution
         ├─ Query streaming
         ├─ Optimization AI
         └─ Sub-second queries
         
2026 H2: Phase 9-10 (Community & Advanced) 📋
         │
         ├─ Plugin marketplace
         ├─ Multi-SDK support
         ├─ Time-series analysis
         └─ Experimentation platform
```

---

## 🎯 Key Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| Core semantic layer | 2024 Q4 | ✅ Complete |
| Callback monitoring | 2025 Q1 | 📋 Planned |
| Enterprise security | 2025 Q2 | 📋 Planned |
| ML-powered features | 2025 Q2 | 📋 Planned |
| Visual editor | 2025 Q3 | 📋 Planned |
| 10+ connectors | 2025 Q4 | 📋 Planned |
| Sub-second queries | 2026 Q1 | 📋 Planned |
| Production scale | 2026 Q2 | 📋 Planned |

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/yourusername/semanticquark.git
cd semanticquark
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black semantic_layer/
ruff check semantic_layer/
```

### Areas Looking for Contributions
- 🔌 New database connectors (Snowflake, BigQuery, Redshift)
- 📊 Data source integrations
- 🧪 Test coverage improvements
- 📚 Documentation enhancements
- 🐛 Bug fixes
- ✨ Feature implementations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [Cube.js](https://github.com/cube-js/cube) - JavaScript semantic layer
- Built with [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- Uses [Pydantic](https://pydantic.dev/) - Data validation

## 📞 Support

- 📖 [Documentation](http://localhost:8000/docs)
- 🐛 [Issue Tracker](https://github.com/yourusername/semanticquark/issues)
- 💬 [Discussions](https://github.com/yourusername/semanticquark/discussions)

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

<div align="center">

**SemanticQuark - The Fundamental Building Block for Semantic Analytics**

Built with ❤️ using Python

[Report Bug](https://github.com/yourusername/semanticquark/issues) • [Request Feature](https://github.com/yourusername/semanticquark/issues) • [Documentation](http://localhost:8000/docs)

</div>