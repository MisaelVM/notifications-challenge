# Notifications Challenge

<p align="center">
  <a href="https://dl.circleci.com/status-badge/redirect/gh/MisaelVM/notifications-challenge/tree/main"><img src="https://dl.circleci.com/status-badge/img/gh/MisaelVM/notifications-challenge/tree/main.svg?style=svg" alt="CircleCI" /></a>
  <a href="https://coveralls.io/github/MisaelVM/notifications-challenge?branch=main"><img src="https://coveralls.io/repos/github/MisaelVM/notifications-challenge/badge.svg?branch=main" alt="Coverage Status" /></a>
</p>

This project is a basic notification management system for authenticated users. The system allows users to create, manage, and send notifications through various communication channels.

## Features

## Tech Stack

- **Language:** Python 3.14+
- **Framework:** [FastAPI](https://github.com/fastapi/fastapi) 0.139.0
- **Package Manager:** [uv](https://github.com/astral-sh/uv)
- **Database:** PostgreSQL (via [SQLAlchemy](https://pypi.org/project/SQLAlchemy/))
- **Testing:** [Pytest](https://pypi.org/project/pytest/)
- **CI/CD:** [CircleCI](https://circleci.com/)

## Environment Variables

Before running the application, you must configure the environment variables. Create `.env` and `.env.test` files in the root directory based on the provided templates:

```bash
cp .env.example .env
cp .env.test.example .env.test
```

### Configuration Summary

| Category | Key Variables | Description |
| :--- | :--- | :--- |
| **Database** | `DATABASE_PROTOCOL_DRIVER`, `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD` | Connection parameters used by the application and for initializing the PostgreSQL containers. |

## Getting Started

> [!IMPORTANT]
> **Make sure you set the proper variables for production and testing environments before running the application**

### Option 1: Docker (Recommended)

#### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
  - **Note:** It is strongly advised to run Docker in [rootless mode](https://docs.docker.com/engine/security/rootless/)
- **Ports:** By default, the API requires port `8000` and the Docker databases require ports `5432` and `5433`

#### Quick Start

Helper scripts have been provided for simplicity:

- **To run the application (Production Profile):**

```bash
chmod +x ./up_production.sh
./up_production.sh
```

> [!TIP]
> If you prefer running commands manually, you can use `docker compose --profile production --env-file .env up --build`

- **To run the test suite (Test Profile):**

```bash
chmod +x ./up_tests.sh
./up_tests.sh
```

> [!TIP]
> If you prefer running commands manually, you can use `docker compose --profile test --env-file .env.test up --build`

> [!CAUTION]
> Notice that if you're running the Docker daemon as root, you'll need to escalate to root privileges in order to run the scripts, e.g., `sudo ./up_production.sh` and `sudo ./up_tests.sh`

### Option 2: Manual Setup (Local Development)

#### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- A running PostgreSQL instance (you may use the containers provided in the Docker profiles for this: `production`, `test`)

#### Installation & Execution

Install dependencies:

```bash
uv sync
```

Run the server:

```bash
uv run fastapi dev
```

Run the test suite:

```bash
uv run pytest -v
```

## API Documentation

The API is self-documenting via Swagger UI. Once the server is running, visit:

- **Swagger UI:** <http://localhost:8000/docs>
- **ReDoc:** <http://localhost:8000/redoc>

## Technical Decisions

### Framework & Runtime

- **FastAPI:** Chosen for its high performance and native support for asynchronous programming, among other benefits such as:
  - **Asynchronous I/O:** Efficiently handles I/O-bound tasks without blocking.
  - **Type Safety:** Uses [Pydantic](https://pypi.org/project/pydantic/) for robust data validation and strict Python type enforcement.
  - **Dependency Injection:** Facilitates clean, testable, and decoupled code.
  - **Auto-Documentation:** Provides instant, interactive OpenAPI/Swagger documentation.
- **uv:** Utilized because of its fast dependency resolution and highly reproducible environment.

### Data Persistence

- **SQLAlchemy (Async):** Selected for its mature ecosystem, robust ORM, and support for asynchronous operations, as well as providing a more robust and well-documented patterns for managing asynchronous transactions compared to alternatives like SQLModel.
- **Alembic:** Utilized for versioned schema migrations, ensuring predictable and reproducible database evolutions across all environments, and its easy integration with SQLAlchemy.

### Testing Strategy

- **Pytest:** Utilized for its powerful fixture system and extensive plugin ecosystem.
- **E2E Focus:** Prioritized end-to-end integration tests to validate the complete request-response lifecycle and database integrity, ensuring that the interaction between the API layer, the business logic, and the actual database is validated, catching integration issues that unit tests with mocks would miss.

### Deployment

- **Docker:** Ensures environment parity and portability across different infrastructures.

## Known Limitations & Future Improvements
