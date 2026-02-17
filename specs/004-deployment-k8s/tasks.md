# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-deployment-k8s/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/`, `frontend/`, `k8s/`
- Backend source: `backend/app/`
- Frontend source: `frontend/src/`
- Kubernetes manifests: `k8s/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for Kubernetes deployment

- [ ] T001 Create `k8s/` directory at repository root for Kubernetes manifests
- [ ] T002 [P] Create `backend/.dockerignore` to exclude `__pycache__`, `.pytest_cache`, `.env`, `*.pyc`, `.git`, `venv/`, `*.md`
- [ ] T003 [P] Create `frontend/.dockerignore` to exclude `node_modules/`, `.next/`, `.git/`, `*.md`, `.env*`, `coverage/`, `dist/`

**Checkpoint**: Directory structure ready for containerization

---

## Phase 2: User Story 1 - Backend Containerization (Priority: P1) 🎯 MVP

**Goal**: Deploy FastAPI backend as containerized service accessible within Kubernetes cluster

**Independent Test**: Backend container builds, deploys to Minikube, and health check endpoint returns 200 OK

### Implementation for User Story 1

- [ ] T004 [US1] Create `backend/Dockerfile` with Python 3.12-slim base image, copy requirements.txt, install dependencies with `pip install --no-cache-dir`, copy app/ directory, expose port 8000, set CMD to `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] T005 [US1] Test backend Docker build locally: `docker build -t todo-backend:latest ./backend` and verify image size < 500MB
- [ ] T006 [US1] Test backend container locally: `docker run -p 8000:8000 -e DATABASE_URL=$DATABASE_URL -e OPENAI_API_KEY=$OPENAI_API_KEY todo-backend:latest` and verify `/docs` endpoint accessible
- [ ] T007 [US1] Create `k8s/backend-deployment.yaml` with Deployment spec: 2 replicas, image `todo-backend:latest`, imagePullPolicy Never, container port 8000, env vars from secret `todo-secrets` (DATABASE_URL, OPENAI_API_KEY), resources (requests: 256Mi/250m, limits: 512Mi/500m), livenessProbe on `/docs` (initialDelaySeconds: 30, periodSeconds: 10), readinessProbe on `/docs` (initialDelaySeconds: 10, periodSeconds: 5)
- [ ] T008 [US1] Create `k8s/backend-service.yaml` with Service spec: type ClusterIP, selector `app: todo-backend`, port 8000 to targetPort 8000, name `backend-service`
- [ ] T009 [US1] Verify backend deployment: configure Minikube Docker env, build image, apply deployment and service, check pods running with `kubectl get pods -l app=todo-backend`, check service with `kubectl get svc backend-service`

**Checkpoint**: Backend containerized and deployed to Minikube, accessible internally at `http://backend-service:8000`

---

## Phase 3: User Story 3 - Secrets Management (Priority: P1) 🎯 MVP

**Goal**: Securely inject DATABASE_URL and OPENAI_API_KEY into backend pods via Kubernetes Secrets

**Independent Test**: Secrets created, backend pods receive environment variables, no plaintext secrets in code

### Implementation for User Story 3

- [ ] T010 [US3] Document secret creation command in deployment script: `kubectl create secret generic todo-secrets --from-literal=DATABASE_URL="$DATABASE_URL" --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY"` with check for existing secret first
- [ ] T011 [US3] Verify secret injection: create secret manually, restart backend deployment, exec into pod and verify env vars with `kubectl exec <pod> -- env | grep -E "DATABASE_URL|OPENAI_API_KEY"` (values should be present but not logged)
- [ ] T012 [US3] Verify no plaintext secrets: search codebase for hardcoded secrets with `git grep -i "postgresql://"` and `git grep -i "sk-"` (should return no results in committed files)
- [ ] T013 [US3] Add `.env` and `.env.*` to `.gitignore` if not already present to prevent accidental secret commits

**Checkpoint**: Secrets management implemented securely, backend pods receive credentials from Kubernetes Secrets

---

## Phase 4: User Story 2 - Frontend Containerization (Priority: P2)

**Goal**: Deploy Next.js frontend as containerized service accessible externally via NodePort

**Independent Test**: Frontend container builds with correct API URL, deploys to Minikube, accessible via browser, communicates with backend

### Implementation for User Story 2

- [ ] T014 [US2] Create `frontend/Dockerfile` with multi-stage build:
  - Stage 1 (builder): FROM node:20-alpine, WORKDIR /app, ARG NEXT_PUBLIC_API_URL, ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL, COPY package*.json ./, RUN npm ci, COPY . ., RUN npm run build
  - Stage 2 (runner): FROM node:20-alpine, WORKDIR /app, ENV NODE_ENV=production, COPY --from=builder /app/public ./public, COPY --from=builder /app/.next/standalone ./, COPY --from=builder /app/.next/static ./.next/static, EXPOSE 3000, CMD ["node", "server.js"]
- [ ] T015 [US2] Update `frontend/next.config.ts` to enable standalone output: add `output: 'standalone'` to next config
- [ ] T016 [US2] Test frontend Docker build locally: `docker build -t todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 ./frontend` and verify image size < 300MB
- [ ] T017 [US2] Create `k8s/frontend-deployment.yaml` with Deployment spec: 2 replicas, image `todo-frontend:latest`, imagePullPolicy Never, container port 3000, env var NEXT_PUBLIC_API_URL=http://backend-service:8000, resources (requests: 256Mi/250m, limits: 512Mi/500m), livenessProbe on `/` (initialDelaySeconds: 30, periodSeconds: 10), readinessProbe on `/` (initialDelaySeconds: 10, periodSeconds: 5)
- [ ] T018 [US2] Create `k8s/frontend-service.yaml` with Service spec: type NodePort, selector `app: todo-frontend`, port 3000 to targetPort 3000, nodePort 30080, name `frontend-service`
- [ ] T019 [US2] Verify frontend deployment: build image with backend service URL, apply deployment and service, check pods running with `kubectl get pods -l app=todo-frontend`, get Minikube URL with `minikube service frontend-service --url`, access in browser and verify UI loads
- [ ] T020 [US2] Test frontend-to-backend communication: open browser console, perform task CRUD operations, verify API calls succeed and data persists in Neon database

**Checkpoint**: Frontend containerized and deployed to Minikube, accessible externally, communicates with backend successfully

---

## Phase 5: User Story 4 - Orchestration Automation (Priority: P3)

**Goal**: Provide automated deployment script for one-command Minikube deployment

**Independent Test**: Running `./deploy_minikube.sh` successfully deploys entire stack without manual intervention

### Implementation for User Story 4

- [ ] T021 [US4] Create `deploy_minikube.sh` script with shebang `#!/bin/bash` and set -e for error handling
- [ ] T022 [US4] Add Minikube status check: verify Minikube is running with `minikube status`, if not running print error and exit
- [ ] T023 [US4] Add Docker environment configuration: detect shell (bash/powershell), configure Minikube Docker env with `eval $(minikube docker-env)` or PowerShell equivalent, verify with `docker info`
- [ ] T024 [US4] Add secret creation logic: check if `todo-secrets` exists with `kubectl get secret todo-secrets`, if not exists prompt user for DATABASE_URL and OPENAI_API_KEY, create secret with `kubectl create secret generic todo-secrets --from-literal=...`
- [ ] T025 [US4] Add image build commands: build backend with `docker build -t todo-backend:latest ./backend`, build frontend with `docker build -t todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 ./frontend`, verify builds succeed
- [ ] T026 [US4] Add Kubernetes deployment commands: apply manifests in order (backend-deployment, backend-service, frontend-deployment, frontend-service) with `kubectl apply -f k8s/`, wait for rollout with `kubectl rollout status deployment/backend-deployment` and `kubectl rollout status deployment/frontend-deployment`
- [ ] T027 [US4] Add verification checks: verify all pods running with `kubectl get pods`, verify services with `kubectl get svc`, print Minikube URL with `minikube service frontend-service --url`
- [ ] T028 [US4] Add error handling: trap errors and print helpful messages (e.g., "Minikube not running", "Docker build failed", "Secret creation failed"), include troubleshooting hints
- [ ] T029 [US4] Test deployment script: run on clean Minikube cluster, verify all resources created, verify application accessible, time execution (should be < 10 minutes)
- [ ] T030 [US4] Make script executable: `chmod +x deploy_minikube.sh`

**Checkpoint**: Deployment automation complete, entire stack can be deployed with single command

---

## Phase 6: Validation and Documentation

**Purpose**: End-to-end testing and documentation updates

- [ ] T031 Test rolling update: modify backend code, rebuild image, run `kubectl rollout restart deployment/backend-deployment`, verify zero downtime by continuously polling API during update
- [ ] T032 Test pod failure recovery: delete one backend pod with `kubectl delete pod <pod-name>`, verify Kubernetes automatically creates new pod and it becomes ready within 30 seconds
- [ ] T033 Test health checks: simulate unhealthy pod by breaking health endpoint, verify pod is removed from service endpoints and restarted
- [ ] T034 [P] Update `README.md` with Phase IV deployment section: prerequisites (Minikube, kubectl, Docker), deployment instructions (run deploy_minikube.sh), verification steps, access URLs
- [ ] T035 [P] Create `specs/004-deployment-k8s/TROUBLESHOOTING.md` with common issues: ImagePullBackOff (solution: configure Docker env), CrashLoopBackOff (solution: check secrets and logs), Service not accessible (solution: check endpoints and Minikube IP)
- [ ] T036 Verify all success criteria from spec.md: image build time < 5 min, pods running within 60s, frontend accessible and loads < 3s, API latency < 500ms, no plaintext secrets, zero-downtime update works, pod failure recovery works
- [x] T037 [US4] Project Renaming and Final SDD Sync: Update project identity from '001-todo-phase-I' to 'evolution-of-todo' across all specs, docs, package.json files, README.md, and Kubernetes manifests. Update repository URL to https://github.com/Bilal-Gulzar/evolution-of-todo. Mark Phase IV as Complete in architecture.md.

**Checkpoint**: All validation complete, documentation updated, project identity synchronized, Phase IV ready for production use

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Backend Containerization (Phase 2)**: Depends on Setup completion
- **Secrets Management (Phase 3)**: Can start in parallel with Phase 2, but must complete before backend deployment verification (T009)
- **Frontend Containerization (Phase 4)**: Depends on Backend Containerization (Phase 2) completion - frontend needs backend service to be available
- **Orchestration Automation (Phase 5)**: Depends on all previous phases - script automates the entire deployment
- **Validation (Phase 6)**: Depends on all previous phases - validates complete system

### Critical Path

Setup (T001-T003) → Backend Containerization (T004-T009) → Frontend Containerization (T014-T020) → Orchestration Automation (T021-T030) → Validation (T031-T036)

Secrets Management (T010-T013) can run in parallel with Backend Containerization but must complete before T009.

### Task Dependencies

**Within Backend Containerization (US1)**:
- T004 (Dockerfile) → T005 (build test) → T006 (container test) → T007 (deployment manifest) → T008 (service manifest) → T009 (verify deployment)

**Within Secrets Management (US3)**:
- T010 → T011 → T012 → T013 (sequential, each builds on previous)

**Within Frontend Containerization (US2)**:
- T014 (Dockerfile) → T015 (next.config) → T016 (build test) → T017 (deployment manifest) → T018 (service manifest) → T019 (verify deployment) → T020 (test communication)

**Within Orchestration Automation (US4)**:
- T021 (create script) → T022-T028 (add features in order) → T029 (test) → T030 (make executable)

### Parallel Opportunities

- T002 and T003 (both .dockerignore files) can run in parallel
- T010-T013 (Secrets Management) can run in parallel with T004-T008 (Backend Containerization implementation)
- T034 and T035 (documentation) can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 + 3 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Backend Containerization (T004-T009)
3. Complete Phase 3: Secrets Management (T010-T013)
4. **STOP and VALIDATE**: Test backend independently - can it be accessed from within cluster? Does it connect to database?
5. This gives you a working backend in Kubernetes (MVP!)

### Incremental Delivery

1. Complete Setup + Backend + Secrets → Backend MVP deployed
2. Add Frontend Containerization (T014-T020) → Full-stack deployed
3. Add Orchestration Automation (T021-T030) → One-command deployment
4. Add Validation (T031-T036) → Production-ready

### Sequential Execution (Recommended)

Execute tasks in order T001 → T036. This ensures all dependencies are met and provides clear checkpoints for validation.

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each logical group of tasks (e.g., after completing each phase)
- Stop at any checkpoint to validate independently
- All file paths are exact and ready for implementation
- Image tags use `latest` for local development (Minikube)
- Secrets are NEVER committed to git - always created via kubectl command
- Frontend MUST use Kubernetes DNS name `backend-service` not `localhost`
