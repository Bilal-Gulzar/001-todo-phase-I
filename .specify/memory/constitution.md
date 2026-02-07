<!-- SYNC IMPACT REPORT:
Version change: 2.0.0 -> 3.0.0
Modified principles: All backend principles updated to include frontend considerations
Added sections: All sections for Phase 3 frontend (Next.js, Tailwind, Shadcn/ui)
Removed sections: None
Templates requiring updates: ⚠ pending (plan-template.md, spec-template.md)
Follow-up TODOs: None
-->

# Todo Full-Stack Application Constitution

## Core Principles

### Component-Based Architecture
<!-- All features are designed as reusable components; Components must be self-contained and testable; Clear props interfaces required -->
All frontend functionality begins as modular, reusable components; Components follow the atomic design pattern; Props interfaces are strictly typed with TypeScript.

### Type Safety with TypeScript
<!-- All code is strictly typed with TypeScript; Interfaces and types defined for all data structures; Strict type checking enabled -->
All frontend code uses TypeScript with strict mode enabled; All API responses and request bodies are typed using shared interfaces; Type checking catches errors at compile time.

### Test-First (NON-NEGOTIABLE)
<!-- TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->
All components include unit tests before implementation; Integration tests cover API interactions; Coverage threshold of 80% required.

### UI Consistency with Tailwind CSS
<!-- All styling done with Tailwind utility classes; Consistent design system enforced; Responsive design patterns required -->
All styling uses Tailwind CSS utility classes; Components follow a consistent design system; Responsive design is implemented for all screen sizes.

### Next.js Ecosystem Compliance
<!-- Follow Next.js best practices; App Router used for navigation; Server and Client components used appropriately -->
Use Next.js App Router for route management and layouts; Leverage Server Components for data fetching where appropriate; Client Components used when interactivity is required.

### Shadcn/ui Integration
<!-- Leverage Shadcn/ui component library for standard UI elements; Custom components extend from base styles; Accessibility standards maintained -->
UI components utilize the Shadcn/ui library for standard elements; Custom components follow accessibility standards (WCAG AA); Theme consistency maintained across the application.

## Technology Stack Requirements
<!-- Technology stack requirements, compliance standards, deployment policies, etc. -->
Stack: Next.js 15 + React 19 + TypeScript + Tailwind CSS + Shadcn/ui
Testing: Jest + React Testing Library for components, Playwright for E2E tests
API Integration: Fetch API or SWR for backend communication
Environment: Node.js 18+, npm for dependency management

## Development Workflow
<!-- Code review requirements, testing gates, deployment approval process, etc. -->
All changes require test coverage before merge; Component documentation maintained in Storybook; Code follows accessibility standards; Pre-commit hooks enforce code formatting and linting

## Governance
<!-- Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

All PRs must verify compliance with these principles; Code reviews check for adherence to component architecture, type safety, testing requirements, and accessibility standards; Use .specify/templates/plan-template.md for runtime development guidance

**Version**: 3.0.0 | **Ratified**: 2026-02-06 | **Last Amended**: 2026-02-06
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
