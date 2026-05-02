# Workflow Management API

A **multi-tenant workflow automation SaaS backend** built with FastAPI and PostgreSQL. The platform supports secure authentication, role-aware tenant access control, workflow task lifecycle management, and service-oriented backend architecture.

## Table of Contents
- [Architecture](#architecture)
- [Multi-tenant Security Model](#multi-tenant-security-model)
- [Workflow Engine](#workflow-engine)
- [Eventing & Integrations](#eventing--integrations)
- [Scalability/Observability](#scalabilityobservability)
- [Current API Surface](#current-api-surface)
- [Tech Stack](#tech-stack)
- [Installation](#installation)




## Architecture
The system is organized into modular backend layers:
- **Routers (`app/router/v1`)** define HTTP contract and request/response boundaries.
- **Services (`app/services`)** centralize business logic such as auth, RBAC checks, and workflow task operations.
- **Models (`app/models`)** define tenant, user, credentials, and workflow entities.
- **Core (`app/core`)** handles config, dependency wiring, and role enforcement.
- **DB (`app/db`)** provides async SQLAlchemy session management for PostgreSQL.

This layered structure keeps business logic decoupled from transport and persistence concerns, enabling clean extensibility for enterprise use cases.

## Multi-tenant Security Model
The platform is designed for organization-level tenancy:
- **Company entity** represents an isolated tenant boundary.
- **User-to-company mapping** enforces tenant ownership.
- **Role model** (`normal`, `admin`, `superuser`) drives authorization behavior.
- **Tenant-scoped task access** allows:
  - normal users to access only their own tasks.
  - admin/superuser to access tasks within the same company.

Authentication and session security:
- JWT-protected routes for workflow actions.
- Refresh token lifecycle management for long-lived sessions.
- Role-aware dependencies at route level.

## Workflow Engine
Current workflow domain capabilities:
- Task lifecycle with status and priority.
- User-owned task creation, updates, retrieval, and deletion.
- Company-level task visibility for elevated roles.
- Due date support for deadline-driven execution.

### Workflow Evolution Roadmap
To expand from task management into true workflow orchestration:
- Configurable state-transition rules.
- Stage-level approvals and validation gates.
- SLA timers and automated escalations.
- Workflow templates for repeatable business processes.

## Eventing & Integrations
The architecture is prepared to evolve into integration-friendly SaaS workflows:
- Service layer boundaries simplify event emission on domain actions.
- Recommended additions:
  - Domain events (`task.created`, `task.updated`, `task.completed`).
  - Outbox pattern for reliable async publishing.
  - Webhook subscriptions per tenant with retries.
  - External integrations (Slack/Email/CRM) via worker pipelines.

## Scalability/Observability
Production-oriented backend improvements are planned around:
- **Scalability:** pagination, filtered query APIs, task indexing, async workers.
- **Reliability:** idempotency keys, optimistic locking, retry policies.
- **Security:** per-tenant rate limiting and audit trails.
- **Observability:** structured logging, trace IDs, metrics, and health checks.

These capabilities position the project as a SaaS backend platform rather than a basic CRUD app.

## Current API Surface
### Auth Endpoints

| Method | Endpoint       | Description         |
| ------ | -------------- | ------------------- |
| POST   | /signup_user   | Register a new user |
| POST   | /login_user    | Login user          |
| POST   | /logout_user   | Logout user         |
| GET    | /get_user/{id} | Get user details    |


### Task Endpoints
| Method | Endpoint                | Description                                 |
| ------ | ----------------------- | ------------------------------------------  |
| POST   | /tasks/create_task      | Create workflow task for authenticated user |
| GET    | /tasks/get_tasks        | Get own tasks or tenant tasks by role       |
| PUT    | /tasks/update_task/{id} | Update task by role-based access control    |
| DELETE | /tasks/delete_task/{id} | Delete task by role-based access control    |


## Tech Stack
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **Authentication:** JWT + Refresh Tokens
- **ORM:** SQLAlchemy (async)
- **Server:** Uvicorn

## Installation
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Run the API:
```bash
uvicorn app.main:app --reload
```

Docs:
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs`