# nBank Python — Test Automation Learning Project

A hands-on project for learning API (and eventually UI) test automation in Python at three skill levels: **Junior**, **Middle**, and **Senior**. Each level tests the same nBank application but with a progressively more sophisticated framework.

## Purpose

The project is structured around a real banking REST API and demonstrates how the same test scenarios can be implemented at different levels of abstraction and framework maturity. The goal is to show what changes as you grow as a QA engineer — from writing raw HTTP calls to building a reusable, maintainable automation framework.

---

## Project Structure

```
nbank-python/
├── src/
│   ├── main/api/                   # Framework source code
│   │   ├── common/                 # Shared types (Role enum)
│   │   ├── middle/                 # Middle-level framework
│   │   └── senior/                 # Senior-level framework
│   └── tests/api/                  # Test suites
│       ├── junior/                 # Junior tests (no framework)
│       ├── middle/                 # Middle tests
│       └── senior/                 # Senior tests
├── docs/                           # In-depth guides (fixtures, etc.)
├── infra/
│   └── docker-compose.yml          # nBank backend + frontend
├── requests/                       # Manual HTTP request examples
├── resources/
│   ├── config.properties           # Base URL, credentials
│   └── dto_comparison.properties   # DTO comparison rules
├── conftest.py
├── pytest.ini
└── requirements.txt
```

---

## Skill Levels

### Junior — No Framework

Tests live in `src/tests/api/junior/`. There is no shared framework code.

- HTTP calls are made directly with the `requests` library
- URLs, headers, and tokens are constructed inline
- Assertions are written manually against raw response JSON
- Test data is hardcoded or generated ad hoc
- Cleanup is done manually inside each test

This level intentionally shows the pain points of working without abstractions: duplication, fragility, and noise.

---

### Middle — Basic Framework

Tests live in `src/tests/api/middle/`. The framework lives in `src/main/api/middle/`.

**Framework components:**

| Component | Description |
|---|---|
| `client/` | Typed HTTP clients per domain (`AdminClient`, `AuthClient`, `AccountsClient`, …) |
| `DTO/` | Pydantic models for request and response bodies |
| `specs/` | `RequestSpec` / `ResponseSpec` — reusable request/response definitions |
| `configs/` | Configuration loader from `config.properties` |
| `generator/` | `RandomData` — generates random values for test data |

Tests at this level use client classes and spec objects instead of raw `requests` calls. Data generation is centralised. Response validation is still mostly manual.

---

### Senior — Full Framework

Tests live in `src/tests/api/senior/`. The framework lives in `src/main/api/senior/`.

**Framework components:**

| Component | Description |
|---|---|
| `clients/skeleton/` | Generic `HttpClient`, `CrudClient`, `ValidatedCrudClient`; `Endpoint` enum |
| `classes/` | `ApiManager` — top-level orchestrator exposing admin and user step objects |
| `steps/` | `AdminSteps`, `UserSteps` — business-level operations used directly in tests |
| `DTO/comparison/` | `DtoAssertions`, `DtoComparator` — declarative request-to-response validation |
| `fixtures/` | Pytest fixtures with automatic teardown via `created_objects` list |
| `generator/` | `RandomDtoGenerator` — builds valid DTOs including regex-constrained fields |
| `specs/` | Validated request/response specs with built-in assertion logic |
| `utils/` | Domain helpers (money arithmetic, etc.) |

Tests at this level are the shortest and most readable. Everything is handled by fixtures and steps; tests express only the intent.

---

## Covered Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/admin/users` | Create a user (admin) |
| `DELETE` | `/admin/users/{id}` | Delete a user (admin) |
| `POST` | `/auth/login` | Log in |
| `POST` | `/accounts` | Create an account |
| `GET` | `/customer/accounts` | Get user accounts |
| `POST` | `/accounts/deposit` | Deposit money |
| `POST` | `/accounts/transfer` | Transfer money |
| `PUT` | `/customer/profile` | Update username |

---

## Technologies

- **Python 3.x**
- **pytest** — test runner, fixtures, parametrize
- **requests** — HTTP client
- **Pydantic** — DTO validation and serialisation
- **Faker** + **rstr** — realistic and regex-constrained test data
- **requests_toolbelt** — HTTP logging utilities
- **colorama** — coloured console output
- **Docker Compose** — local nBank environment

---

## Getting Started

### Prerequisites

- Python 3.10+
- Docker and Docker Compose

### 1. Start the Application

```bash
docker compose -f infra/docker-compose.yml up -d
```

The nBank backend will be available on `http://localhost:4111`.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Tests

Run all tests:
```bash
pytest
```

Run a specific level:
```bash
pytest src/tests/api/junior/
pytest src/tests/api/middle/
pytest src/tests/api/senior/
```

Run by marker:
```bash
pytest -m api
pytest -m "api and not debug"
```

Enable HTTP request/response logging:
```bash
pytest -m log_http
```

---

## Test Markers

| Marker | Description |
|---|---|
| `api` | API test |
| `ui` | UI test |
| `debug` | Temporary debug test, not part of main suite |
| `log_http` | Enables full HTTP request/response logging |

---

## Documentation

- [`docs/fixtures-explained.md`](docs/fixtures-explained.md) — deep dive into pytest fixtures: lifecycle, dependency injection, scoping, and the `created_objects` cleanup pattern used throughout the senior framework.
