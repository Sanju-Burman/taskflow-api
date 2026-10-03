# TaskFlow API — Production-Ready Task Management Backend

[![Python](https://img.shields.io/badge/Python-3.11%2B%20%7C%203.13-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%20(Async)-D71F00?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![JWT](https://img.shields.io/badge/Authentication-JWT%20Bearer-black?style=flat&logo=jsonwebtokens)](https://jwt.io/)
[![Tests](https://img.shields.io/badge/Tests-100%25%20Passing-brightgreen?style=flat&logo=pytest)](https://docs.pytest.org/)

**TaskFlow API** is a high-performance, asynchronous RESTful backend service for task lifecycle and workflow management. Built following clean layered architecture principles, it offers secure user authentication, robust data validation, user data isolation, advanced task search/filter/pagination, and containerized deployment.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [Architecture & Design](#-architecture--design)
- [Tech Stack](#-tech-stack)
- [API Endpoints Overview](#-api-endpoints-overview)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Local Setup (Virtualenv)](#local-setup-virtualenv)
  - [Docker Compose Setup](#docker-compose-setup)
- [Database Migrations (Alembic)](#-database-migrations-alembic)
- [Running Automated Tests](#-running-automated-tests)
- [API Documentation](#-api-documentation)

---

## 🚀 Key Features

- 🔐 **JWT-Based Authentication**: Secure registration, login, and user profile management with password hashing via `bcrypt` and signed JWT Bearer tokens.
- 🛡️ **Multi-User Isolation**: Strict row-level ownership enforcement ensuring users can only read, update, or delete their own tasks.
- 📋 **Complete Task CRUD Operations**: Full lifecycle task management including title, description, priority levels (`low`, `medium`, `high`, `urgent`), status progression (`pending`, `in_progress`, `completed`, `cancelled`), and due dates.
- 🔍 **Advanced Filtering & Pagination**: Multi-parameter querying supporting status filters, priority filters, keyword search on title/description, configurable sorting, and paginated response envelopes with full metadata.
- ⚡ **Asynchronous DB Engine**: Async SQLAlchemy 2.0 with connection pooling and PostgreSQL (`asyncpg`).
- 📦 **Standardized JSON Envelope**: Structured response wrappers (`DataResponse`, `PaginatedResponse`, `BaseResponse`) and centralized RFC 7807 exception handling.
- 🐳 **Dockerized Deployment**: Fully containerized environment with healthchecks and compose orchestration.

---

## 🏗 Architecture & Design

The codebase enforces a **Layered Clean Architecture** for clear separation of concerns, maintainability, and testability:

```
taskflow-api/
├── app/
│   ├── api/
│   │   ├── deps.py             # Dependency injection (DB session, auth user extraction)
│   │   └── v1/
│   │       ├── api.py          # V1 Router aggregator
│   │       └── endpoints/      # Controllers / REST route handlers
│   │           ├── auth.py     # /api/v1/auth (register, login, me)
│   │           ├── tasks.py    # /api/v1/tasks (CRUD, filter, search, pagination)
│   │           └── health.py   # /api/v1/health (diagnostics & DB check)
│   ├── core/
│   │   ├── config.py           # Pydantic Settings & environment variables
│   │   ├── database.py         # Async engine & sessionmaker
│   │   ├── exceptions.py       # Domain exceptions & global exception handlers
│   │   ├── middleware.py       # Request logging & performance timing headers
│   │   └── security.py         # Password hashing & JWT generation/decoding
│   ├── models/                 # SQLAlchemy 2.0 ORM models
│   │   ├── base.py             # Declarative Base & TimestampMixin
│   │   ├── user.py             # User DB model
│   │   └── task.py             # Task DB model with status/priority enums
│   ├── repositories/           # Repository layer (Data access / DB queries)
│   │   ├── base.py             # Generic async CRUD repository
│   │   ├── user_repo.py        # User query operations
│   │   └── task_repo.py        # Task query operations with filters & search
│   ├── schemas/                # Pydantic v2 schemas (DTOs & response models)
│   │   ├── base.py             # Standard API envelopes & pagination metadata
│   │   ├── user.py             # User DTOs, Login, and Tokens
│   │   └── task.py             # Task DTOs, updates, filters
│   ├── services/               # Business logic layer
│   │   ├── user_service.py     # Auth & user management logic
│   │   └── task_service.py     # Task orchestration & ownership logic
│   └── main.py                 # FastAPI application factory
├── alembic/                    # Database migrations
├── tests/                      # Pytest automated test suite
├── docker-compose.yml          # Local container orchestration
├── Dockerfile                  # Application container definition
├── requirements.txt            # Python dependencies
└── pytest.ini                  # Pytest configuration
```

---

## 🔌 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **Database**: [PostgreSQL 16](https://www.postgresql.org/)
- **Async ORM**: [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/) with `asyncpg`
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Validation & Serialization**: [Pydantic v2](https://docs.pydantic.dev/) & `pydantic-settings`
- **Security**: `PyJWT`, `bcrypt`
- **Testing**: `pytest`, `pytest-asyncio`, `httpx`, `aiosqlite`
- **Server**: `uvicorn[standard]`

---

## 📡 API Endpoints Overview

### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `POST` | `/api/v1/auth/register` | Register a new user | No |
| `POST` | `/api/v1/auth/login` | Login with email/password (JSON) | No |
| `POST` | `/api/v1/auth/login/oauth` | OAuth2 form login for Swagger UI | No |
| `GET` | `/api/v1/auth/me` | Retrieve authenticated user profile | Yes (Bearer) |

### Task Management (`/api/v1/tasks`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/tasks` | List user tasks (filter, search, sort, paginate) | Yes (Bearer) |
| `POST` | `/api/v1/tasks` | Create a new task | Yes (Bearer) |
| `GET` | `/api/v1/tasks/{task_id}` | Get single task details | Yes (Bearer) |
| `PUT` | `/api/v1/tasks/{task_id}` | Full update of a task | Yes (Bearer) |
| `PATCH` | `/api/v1/tasks/{task_id}` | Partial update (e.g. status/priority) | Yes (Bearer) |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete task | Yes (Bearer) |

### Diagnostics (`/api/v1/health`)
| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/v1/health` | Healthcheck & Database connection test | No |

---

## 🛠 Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL (or Docker)

### Local Setup (Virtualenv)

1. **Clone the repository and enter directory**:
   ```bash
   git clone <repository_url>
   cd taskflow-api
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your PostgreSQL credentials if necessary
   ```

5. **Run Database Migrations**:
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

---

### Docker Compose Setup

To start both the FastAPI application and PostgreSQL 16 with a single command:

```bash
docker-compose up --build -d
```

- API Server: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`

---

## 🧪 Running Automated Tests

The test suite runs with `pytest` against an in-memory async SQLite engine with 100% test isolation:

```bash
pytest -v
```

---

## 📖 API Documentation

Once the server is running, navigate to:
- **Interactive Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema**: [http://127.0.0.1:8000/api/v1/openapi.json](http://127.0.0.1:8000/api/v1/openapi.json)
