<!-- SYNC IMPACT REPORT:
Version change: N/A -> 2.0.0
Modified principles: N/A (new constitution)
Added sections: All sections for Phase 2 backend
Removed sections: N/A
Templates requiring updates: N/A
Follow-up TODOs: None
-->

# Todo Backend API Constitution

## Core Principles

### API-First Design
<!-- All features are designed as API endpoints first; Endpoints must be documented with OpenAPI specs; Clear request/response contracts required -->
All backend functionality begins as API endpoints; APIs follow RESTful principles; Endpoints are versioned from inception to ensure backward compatibility.

### Type Safety with Pydantic
<!-- All request/response payloads validated with Pydantic models; Database models use SQLModel for consistency; Strict type checking required -->
All data models defined using Pydantic/SQLModel; Request validation happens at the API boundary; Response serialization is strongly typed.

### Test-First (NON-NEGOTIABLE)
<!-- TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->
All API endpoints include unit tests before implementation; Integration tests cover database operations; Coverage threshold of 80% required.

### Database-Centric Operations
<!-- All data operations go through SQLModel ORM; Direct SQL queries avoided; Connection pooling managed automatically -->
Database operations use SQLModel ORM exclusively; All models inherit from SQLModel base class; Transaction management follows ACID principles.

### FastAPI Ecosystem Compliance
<!-- Follow FastAPI best practices; Dependency injection used appropriately; Security implemented with OAuth2/password flows -->
Use FastAPI's built-in features like dependency injection and automatic documentation; Security middleware properly configured; Middleware stack follows recommended order.

### Neon Database Integration
<!-- Leverage Neon's branch/clone features for development; Connection pooling optimized for Neon; Environment-specific connection strings -->
Database connections use Neon PostgreSQL service; Environment-specific configurations managed via settings; Connection lifecycle managed by SQLModel.

## Technology Stack Requirements
<!-- Technology stack requirements, compliance standards, deployment policies, etc. -->
Stack: FastAPI + SQLModel + Neon PostgreSQL + Uvicorn server
Testing: PyTest for unit tests, TestClient for API tests, coverage reporting
Security: OAuth2 with password flow, JWT tokens, hashed passwords
Environment: Python 3.9+, Poetry for dependency management

## Development Workflow
<!-- Code review requirements, testing gates, deployment approval process, etc. -->
All changes require test coverage before merge; Database migrations managed via Alembic; API endpoints documented in OpenAPI format; Pre-commit hooks enforce code formatting and linting

## Governance
<!-- Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

All PRs must verify compliance with these principles; Code reviews check for adherence to type safety, testing requirements, and architectural patterns; Use .specify/templates/plan-template.md for runtime development guidance

**Version**: 2.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
