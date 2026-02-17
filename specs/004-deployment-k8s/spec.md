# Feature Specification: Local Kubernetes Deployment

**Project**: Evolution of Todo
**Feature Branch**: `004-deployment-k8s`
**Created**: 2026-02-17
**Updated**: 2026-02-18
**Status**: Complete ✅
**Input**: Phase IV: Local Kubernetes Deployment - Containerize and orchestrate the full-stack Todo application for local Minikube deployment

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Backend Containerization (Priority: P1) 🎯 MVP

Deploy the FastAPI backend as a containerized service accessible within the Kubernetes cluster.

**Why this priority**: Backend must be containerized first as it's a dependency for frontend integration. Without a working backend container, the frontend cannot communicate with the API.

**Independent Test**: Backend container can be built, deployed to Minikube, and health check endpoint (`/docs`) returns 200 OK. API endpoints respond correctly to requests from within the cluster.

**Acceptance Scenarios**:

1. **Given** backend source code and dependencies, **When** Docker build is executed, **Then** a production-ready image is created with minimal size and security vulnerabilities
2. **Given** backend image is deployed to Minikube, **When** pods are created, **Then** all replicas start successfully and pass readiness probes
3. **Given** backend pods are running, **When** database connection is established, **Then** backend connects to Neon PostgreSQL using credentials from Kubernetes Secret
4. **Given** backend service is deployed, **When** API requests are made from within cluster, **Then** requests are load-balanced across backend replicas

---

### User Story 2 - Frontend Containerization (Priority: P2)

Deploy the Next.js frontend as a containerized service accessible externally via NodePort.

**Why this priority**: Frontend depends on backend being containerized and accessible. Once backend is working, frontend can be containerized to complete the full-stack deployment.

**Independent Test**: Frontend container can be built with correct API URL, deployed to Minikube, and accessible via browser at `http://<minikube-ip>:30080`. UI loads correctly and can communicate with backend service.

**Acceptance Scenarios**:

1. **Given** frontend source code, **When** multi-stage Docker build is executed with `NEXT_PUBLIC_API_URL` build arg, **Then** optimized production image is created
2. **Given** frontend image is deployed to Minikube, **When** pods are created, **Then** all replicas start successfully and serve the application
3. **Given** frontend pods are running, **When** user accesses the application via NodePort, **Then** UI loads and displays correctly
4. **Given** frontend is loaded in browser, **When** API calls are made, **Then** frontend successfully communicates with backend service using Kubernetes DNS

---

### User Story 3 - Secrets Management (Priority: P1) 🎯 MVP

Securely inject sensitive configuration (DATABASE_URL, OPENAI_API_KEY) into backend pods via Kubernetes Secrets.

**Why this priority**: Security is critical and must be implemented from the start. Hardcoding secrets is unacceptable in any environment.

**Independent Test**: Secrets can be created in Kubernetes, backend pods receive environment variables from secrets, and no plaintext secrets exist in code or images.

**Acceptance Scenarios**:

1. **Given** sensitive credentials, **When** Kubernetes Secret is created, **Then** values are base64 encoded and stored securely
2. **Given** Secret exists, **When** backend deployment references the secret, **Then** environment variables are injected into pods at runtime
3. **Given** backend pod is running, **When** application code reads environment variables, **Then** correct secret values are available
4. **Given** deployment is complete, **When** inspecting images and manifests, **Then** no plaintext secrets are found

---

### User Story 4 - Orchestration Automation (Priority: P3)

Provide automated deployment script for one-command Minikube deployment.

**Why this priority**: Automation improves developer experience but is not critical for initial deployment. Manual steps can work initially.

**Independent Test**: Running `./deploy_minikube.sh` successfully deploys the entire stack to Minikube without manual intervention.

**Acceptance Scenarios**:

1. **Given** clean Minikube cluster, **When** deployment script is executed, **Then** all resources are created in correct order
2. **Given** script completes, **When** checking cluster state, **Then** all pods are running and services are accessible
3. **Given** deployment fails at any step, **When** script encounters error, **Then** clear error message is displayed with remediation steps

---

### Edge Cases

- What happens when Minikube Docker environment is not configured? (Script should detect and configure automatically)
- How does system handle secret creation when secrets already exist? (Script should check and skip or update)
- What happens when backend cannot connect to Neon database? (Pod should fail readiness probe and not receive traffic)
- How does frontend handle backend service being unavailable? (Should show appropriate error message, not crash)
- What happens when image pull fails? (Kubernetes should retry and surface error in pod events)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST containerize FastAPI backend using production-ready Dockerfile with Python 3.12-slim base image
- **FR-002**: System MUST containerize Next.js frontend using multi-stage Dockerfile with Node 20-alpine base image
- **FR-003**: Backend container MUST expose port 8000 and include health check endpoint at `/docs`
- **FR-004**: Frontend container MUST expose port 3000 and accept `NEXT_PUBLIC_API_URL` as build argument
- **FR-005**: System MUST create Kubernetes Deployment for backend with 2 replicas and ClusterIP service
- **FR-006**: System MUST create Kubernetes Deployment for frontend with 2 replicas and NodePort service (port 30080)
- **FR-007**: System MUST create Kubernetes Secret containing `DATABASE_URL` and `OPENAI_API_KEY`
- **FR-008**: Backend pods MUST inject secret values as environment variables
- **FR-009**: Frontend MUST communicate with backend using Kubernetes DNS name `http://backend-service:8000`
- **FR-010**: System MUST implement liveness and readiness probes for both services
- **FR-011**: Deployment MUST support rolling updates with zero downtime
- **FR-012**: System MUST provide `.dockerignore` files to exclude unnecessary files from images

### Key Entities

- **Backend Deployment**: Kubernetes Deployment managing 2 FastAPI backend pods with resource limits and health checks
- **Frontend Deployment**: Kubernetes Deployment managing 2 Next.js frontend pods with resource limits and health checks
- **Backend Service**: ClusterIP service exposing backend internally on port 8000
- **Frontend Service**: NodePort service exposing frontend externally on port 30080
- **Secrets**: Kubernetes Secret object containing base64-encoded DATABASE_URL and OPENAI_API_KEY
- **Docker Images**: `todo-backend:latest` and `todo-frontend:latest` built locally for Minikube

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend and frontend Docker images build successfully in under 5 minutes combined
- **SC-002**: All 4 pods (2 backend, 2 frontend) reach Running state within 60 seconds of deployment
- **SC-003**: Frontend is accessible via browser at `http://<minikube-ip>:30080` and loads within 3 seconds
- **SC-004**: Backend API responds to requests from frontend with latency under 500ms for 95% of requests
- **SC-005**: Zero plaintext secrets found in Docker images, deployment manifests, or git repository
- **SC-006**: Rolling update of backend completes without any request failures (zero downtime)
- **SC-007**: System handles backend pod failure by automatically routing traffic to healthy replicas
- **SC-008**: Deployment script completes full stack deployment in under 10 minutes on clean Minikube cluster
