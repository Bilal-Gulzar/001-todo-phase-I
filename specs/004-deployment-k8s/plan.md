# Implementation Plan: Local Kubernetes Deployment

**Feature**: 004-deployment-k8s
**Created**: 2026-02-17
**Status**: Draft
**Input**: spec.md (User Stories 1-4)

---

## 1. Scope and Dependencies

### In Scope

- Production-ready Dockerfiles for backend (FastAPI) and frontend (Next.js)
- Kubernetes manifests for deployments and services (backend ClusterIP, frontend NodePort)
- Kubernetes Secret for DATABASE_URL and OPENAI_API_KEY
- Health checks (liveness and readiness probes) for both services
- Multi-stage build for frontend to optimize image size
- `.dockerignore` files to exclude unnecessary files
- Deployment automation script for Minikube
- Documentation for deployment and verification

### Out of Scope

- Helm charts (using raw Kubernetes manifests for simplicity)
- Ingress controller (using NodePort for local access)
- Horizontal Pod Autoscaler (HPA)
- Persistent volumes (using external Neon PostgreSQL)
- CI/CD pipeline integration
- Production cloud deployment (GKE, EKS, AKS)
- Service mesh (Istio, Linkerd)
- Monitoring and observability stack (Prometheus, Grafana)

### External Dependencies

| Dependency | Owner | Status | Notes |
|------------|-------|--------|-------|
| Minikube | User | Required | Must be installed and running |
| Docker | User | Required | For building images |
| kubectl | User | Required | For cluster management |
| Neon PostgreSQL | External SaaS | Active | Connection string required |
| OpenAI API | External SaaS | Active | API key required (via OpenRouter) |
| Existing Backend | Phase 2 | Complete | FastAPI app in `backend/` |
| Existing Frontend | Phase 3 | Complete | Next.js app in `frontend/` |

---

## 2. Key Decisions and Rationale

### Decision 1: Raw Kubernetes Manifests vs Helm Charts

**Options Considered**:
1. Raw Kubernetes YAML manifests
2. Helm charts with templates
3. Kustomize overlays

**Trade-offs**:
- Raw manifests: Simple, no learning curve, direct control, but repetitive for multiple environments
- Helm: Powerful templating, package management, but adds complexity and learning curve
- Kustomize: Good for overlays, but less powerful than Helm

**Rationale**: Use raw Kubernetes manifests for Phase IV. This is a local development deployment with a single environment (Minikube). Helm adds unnecessary complexity for this use case. If we need multi-environment support later, we can migrate to Helm.

**Principles**: Smallest viable change, avoid over-engineering

**Reversibility**: High - can migrate to Helm later by converting manifests to templates

---

### Decision 2: Multi-Stage Build for Frontend

**Options Considered**:
1. Single-stage build (install deps + build + run in same image)
2. Multi-stage build (separate builder and runner stages)

**Trade-offs**:
- Single-stage: Simpler Dockerfile, but larger image size (~1GB) with build tools and dev dependencies
- Multi-stage: More complex Dockerfile, but smaller final image (~200MB) with only production dependencies

**Rationale**: Use multi-stage build for frontend. Next.js builds can be large, and we want to minimize image size for faster pulls and reduced attack surface. The complexity is minimal and well-documented.

**Principles**: Security (minimal attack surface), performance (smaller images)

**Reversibility**: Medium - can simplify to single-stage if needed, but would increase image size

---

### Decision 3: ClusterIP for Backend, NodePort for Frontend

**Options Considered**:
1. Both services as NodePort (external access)
2. Backend ClusterIP, Frontend NodePort
3. Both services as ClusterIP with Ingress

**Trade-offs**:
- Both NodePort: Simple, but exposes backend directly (security risk)
- Backend ClusterIP + Frontend NodePort: Secure backend, simple frontend access
- Both ClusterIP + Ingress: Most production-like, but requires Ingress controller setup

**Rationale**: Backend as ClusterIP (internal only), Frontend as NodePort (external access). This follows security best practices by not exposing the backend API directly. NodePort is simpler than Ingress for local Minikube access.

**Principles**: Security (defense in depth), simplicity for local development

**Reversibility**: High - can add Ingress later for production

---

### Decision 4: Secrets via kubectl create secret vs YAML Manifest

**Options Considered**:
1. Create secrets via `kubectl create secret` command
2. Create secrets via YAML manifest (base64 encoded)
3. Use external secret management (Sealed Secrets, External Secrets Operator)

**Trade-offs**:
- kubectl command: Simple, secrets never in git, but manual step
- YAML manifest: Declarative, but secrets in git (even if base64 encoded)
- External secret manager: Most secure, but adds complexity

**Rationale**: Use `kubectl create secret` command in deployment script. Secrets should never be committed to git, even if base64 encoded. The command approach is simple and secure for local development.

**Principles**: Security (no secrets in git), simplicity

**Reversibility**: High - can migrate to external secret manager later

---

### Decision 5: Image Tag Strategy

**Options Considered**:
1. Use `latest` tag for local development
2. Use git commit SHA as tag
3. Use semantic versioning

**Trade-offs**:
- `latest`: Simple, but can cause confusion with cached images
- Git SHA: Precise, but requires git integration
- Semantic version: Clear versioning, but requires version management

**Rationale**: Use `latest` tag for Phase IV local development. Minikube uses local Docker images, so we can control when images are rebuilt. For production, we would use git SHA or semantic versioning.

**Principles**: Simplicity for local development

**Reversibility**: High - can change tag strategy later

---

## 3. Interfaces and API Contracts

### Docker Build Interfaces

#### Backend Image Build
```bash
docker build -t todo-backend:latest ./backend
```

**Inputs**:
- `backend/` directory with source code
- `backend/requirements.txt` with Python dependencies
- `backend/.dockerignore` to exclude unnecessary files

**Outputs**:
- Docker image `todo-backend:latest`
- Exposed port: 8000
- Entry point: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Environment Variables Required**:
- `DATABASE_URL`: PostgreSQL connection string (from Secret)
- `OPENAI_API_KEY`: OpenAI API key (from Secret)

---

#### Frontend Image Build
```bash
docker build -t todo-frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 \
  ./frontend
```

**Inputs**:
- `frontend/` directory with source code
- `frontend/package.json` with Node dependencies
- `frontend/.dockerignore` to exclude unnecessary files
- Build arg: `NEXT_PUBLIC_API_URL` (Kubernetes DNS name for backend)

**Outputs**:
- Docker image `todo-frontend:latest`
- Exposed port: 3000
- Entry point: `node server.js` (Next.js production server)

---

### Kubernetes Service Interfaces

#### Backend Service (ClusterIP)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: todo-backend
  ports:
  - port: 8000
    targetPort: 8000
```

**Access**: Internal only (within cluster)
**DNS Name**: `backend-service.default.svc.cluster.local` (or `backend-service` within same namespace)
**Endpoints**: All backend pods matching selector `app: todo-backend`

---

#### Frontend Service (NodePort)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: todo-frontend
  ports:
  - port: 3000
    targetPort: 3000
    nodePort: 30080
```

**Access**: External via `http://<minikube-ip>:30080`
**DNS Name**: `frontend-service.default.svc.cluster.local` (internal)
**Endpoints**: All frontend pods matching selector `app: todo-frontend`

---

### Health Check Interfaces

#### Backend Health Checks
- **Liveness Probe**: `GET /docs` (FastAPI auto-generated docs page)
  - Initial delay: 30s
  - Period: 10s
  - Failure threshold: 3
- **Readiness Probe**: `GET /docs`
  - Initial delay: 10s
  - Period: 5s
  - Failure threshold: 3

#### Frontend Health Checks
- **Liveness Probe**: `GET /`
  - Initial delay: 30s
  - Period: 10s
  - Failure threshold: 3
- **Readiness Probe**: `GET /`
  - Initial delay: 10s
  - Period: 5s
  - Failure threshold: 3

---

## 4. Non-Functional Requirements (NFRs) and Budgets

### Performance

**Metrics**:
- Image build time: < 5 minutes combined (backend + frontend)
- Pod startup time: < 60 seconds from image pull to Running state
- Pod ready time: < 10 seconds from Running to Ready state
- API response time: < 500ms p95 (same as Phase 2)
- Frontend page load: < 3 seconds

**Resource Limits** (per pod):
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Rationale**: Conservative limits for local Minikube. Backend and frontend are lightweight applications. These limits allow 4 pods (2 backend + 2 frontend) to run comfortably on a typical developer machine with 8GB RAM.

---

### Reliability

**SLOs**:
- Pod availability: 99% (at least 1 replica healthy at all times)
- Zero-downtime deployments: 100% (rolling updates with max unavailable = 1)
- Automatic recovery: Failed pods restart within 30 seconds

**Deployment Strategy**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

**Rationale**: With 2 replicas, we can afford to have 1 pod unavailable during updates while maintaining service availability.

---

### Security

**Measures**:
1. **No Secrets in Git**: Secrets created via kubectl command, never committed
2. **No Secrets in Images**: Environment variables injected at runtime from Kubernetes Secrets
3. **Minimal Base Images**: Use slim/alpine variants to reduce attack surface
4. **Non-Root User**: Containers run as non-root user (TODO: implement in Dockerfile)
5. **Backend Not Exposed**: ClusterIP service prevents direct external access to backend API

**Secret Management**:
- Secrets stored in Kubernetes etcd (base64 encoded)
- Injected as environment variables at pod creation
- Not visible in `kubectl describe pod` output
- Not included in Docker images or git repository

---

### Cost

**Local Development**: No cloud costs (Minikube runs locally)

**Resource Usage**:
- 4 pods × 512Mi max = 2GB RAM maximum
- 4 pods × 500m CPU max = 2 CPU cores maximum
- Typical developer machine (8GB RAM, 4 cores) can handle this comfortably

---

## 5. Data Management and Migration

### No Data Migration Required

This phase does not change data storage. Backend continues to use external Neon PostgreSQL database with the same schema and connection string.

**Source of Truth**: Neon PostgreSQL (external SaaS)

**Connection String**: Injected via Kubernetes Secret as `DATABASE_URL` environment variable

**No Schema Changes**: Existing database schema from Phase 2 remains unchanged

---

## 6. Operational Readiness

### Observability

**Logging**:
- All logs to stdout/stderr (Kubernetes standard)
- Accessible via `kubectl logs <pod-name>`
- Structured logs with timestamps and log levels
- Request IDs for tracing (already implemented in backend)

**Metrics**:
- Pod resource usage: `kubectl top pods`
- Service endpoints: `kubectl get endpoints`
- Pod status: `kubectl get pods`

**Health Checks**:
- Liveness probes detect and restart unhealthy pods
- Readiness probes remove unhealthy pods from load balancer

---

### Deployment and Rollback

**Deployment**:
```bash
# Build images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 ./frontend

# Create secrets (if not exists)
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY"

# Deploy
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

**Rollback**:
```bash
# Rollback to previous version
kubectl rollout undo deployment/backend-deployment
kubectl rollout undo deployment/frontend-deployment

# Check rollout status
kubectl rollout status deployment/backend-deployment
```

**Zero-Downtime Updates**:
- Rolling update strategy ensures at least 1 pod is always available
- Readiness probes prevent traffic to pods that aren't ready
- Max unavailable = 1, max surge = 1

---

### Runbooks

#### Runbook 1: Pod Crash Loop
**Symptoms**: Pod repeatedly restarting, CrashLoopBackOff status

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # logs from previous crash
```

**Common Causes**:
1. Database connection failure (check DATABASE_URL secret)
2. Missing environment variables (check secret injection)
3. Application error (check logs)

**Remediation**:
1. Verify secrets exist: `kubectl get secret todo-secrets`
2. Verify secret values are correct (decode base64)
3. Check database connectivity from within cluster
4. Fix issue and restart deployment: `kubectl rollout restart deployment/<name>`

---

#### Runbook 2: Service Not Accessible
**Symptoms**: Cannot access frontend via NodePort, or frontend cannot reach backend

**Diagnosis**:
```bash
kubectl get svc
kubectl get endpoints
kubectl describe svc <service-name>
minikube service frontend-service --url  # get correct URL
```

**Common Causes**:
1. Pods not ready (failing readiness probes)
2. Service selector doesn't match pod labels
3. Wrong NodePort or Minikube IP

**Remediation**:
1. Check pod status: `kubectl get pods`
2. Check service endpoints: `kubectl get endpoints`
3. Verify service selector matches pod labels
4. Get correct Minikube IP: `minikube ip`
5. Test from within cluster: `kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://backend-service:8000/docs`

---

#### Runbook 3: Image Pull Errors
**Symptoms**: Pods stuck in ImagePullBackOff or ErrImagePull

**Diagnosis**:
```bash
kubectl describe pod <pod-name>
docker images | grep todo  # verify images exist locally
```

**Common Causes**:
1. Image not built locally
2. Minikube Docker environment not configured
3. Wrong image name or tag

**Remediation**:
1. Configure Minikube Docker environment: `eval $(minikube docker-env)`
2. Rebuild images: `docker build -t todo-backend:latest ./backend`
3. Verify images: `docker images | grep todo`
4. Set imagePullPolicy to Never in deployment (for local images)

---

## 7. Risk Analysis and Mitigation

### Risk 1: Minikube Docker Environment Not Configured
**Probability**: High (common mistake)
**Impact**: High (images won't be found)
**Blast Radius**: Local development only

**Mitigation**:
- Deployment script checks and configures Docker environment automatically
- Clear error message if not configured
- Documentation includes troubleshooting steps

**Kill Switch**: N/A (local development)

---

### Risk 2: Secrets Not Created Before Deployment
**Probability**: Medium
**Impact**: High (pods will crash)
**Blast Radius**: Local development only

**Mitigation**:
- Deployment script checks if secrets exist before deploying
- Creates secrets if missing (prompts user for values)
- Clear error message if secrets are missing

**Kill Switch**: Delete deployment: `kubectl delete deployment <name>`

---

### Risk 3: Frontend Cannot Reach Backend
**Probability**: Medium (DNS or network issue)
**Impact**: High (application non-functional)
**Blast Radius**: Local development only

**Mitigation**:
- Use Kubernetes DNS name (`backend-service`) instead of localhost
- Test connectivity from within cluster before deploying frontend
- Deployment script includes connectivity test

**Kill Switch**: Rollback frontend deployment

---

### Risk 4: Database Connection Failure
**Probability**: Low (Neon is reliable)
**Impact**: High (backend non-functional)
**Blast Radius**: All backend pods

**Mitigation**:
- Readiness probe prevents traffic to pods that can't connect to database
- Connection string includes SSL mode for security
- Deployment script tests database connectivity before deploying

**Kill Switch**: Rollback backend deployment

---

## 8. Evaluation and Validation

### Definition of Done

**Functional**:
- [ ] Backend Dockerfile builds successfully
- [ ] Frontend Dockerfile builds successfully with multi-stage build
- [ ] Backend deployment creates 2 running pods
- [ ] Frontend deployment creates 2 running pods
- [ ] Backend service is ClusterIP type on port 8000
- [ ] Frontend service is NodePort type on port 30080
- [ ] Secrets are created and injected into backend pods
- [ ] Backend connects to Neon PostgreSQL successfully
- [ ] Frontend is accessible via browser at `http://<minikube-ip>:30080`
- [ ] Frontend can communicate with backend via Kubernetes DNS
- [ ] All CRUD operations work correctly
- [ ] AI chat functionality works correctly
- [ ] Health checks pass for all pods

**Non-Functional**:
- [ ] No plaintext secrets in git repository
- [ ] No secrets in Docker images
- [ ] Image sizes are optimized (backend < 500MB, frontend < 300MB)
- [ ] Rolling update completes without downtime
- [ ] Failed pod automatically restarts within 30 seconds
- [ ] Deployment script completes successfully

**Documentation**:
- [ ] README updated with deployment instructions
- [ ] Troubleshooting guide included
- [ ] Runbooks documented

---

### Output Validation

**Format Validation**:
- Dockerfiles follow best practices (multi-stage, minimal layers, .dockerignore)
- Kubernetes manifests are valid YAML (validate with `kubectl apply --dry-run`)
- Deployment script is executable and includes error handling

**Requirements Validation**:
- All functional requirements from spec.md are addressed
- All user stories have corresponding implementation tasks
- Success criteria are measurable and testable

**Safety Validation**:
- No secrets committed to git (pre-commit hook or manual check)
- Containers run as non-root user (security best practice)
- Resource limits prevent resource exhaustion

---

## 9. Implementation Structure

### File Structure
```
evolution-of-todo/
├── backend/
│   ├── Dockerfile                 # Backend container definition
│   ├── .dockerignore             # Exclude files from image
│   └── app/                      # Existing backend code
├── frontend/
│   ├── Dockerfile                # Frontend multi-stage build
│   ├── .dockerignore             # Exclude files from image
│   └── src/                      # Existing frontend code
├── k8s/
│   ├── backend-deployment.yaml   # Backend deployment manifest
│   ├── backend-service.yaml      # Backend ClusterIP service
│   ├── frontend-deployment.yaml  # Frontend deployment manifest
│   └── frontend-service.yaml     # Frontend NodePort service
├── deploy_minikube.sh            # Automated deployment script
└── specs/
    └── 004-deployment-k8s/
        ├── spec.md               # This feature specification
        ├── plan.md               # This implementation plan
        └── tasks.md              # Task breakdown
```

---

## 10. Architectural Decision Records

### ADR Candidates

The following decisions may warrant ADRs if they prove to be architecturally significant:

1. **Container Orchestration Platform**: Why Kubernetes over Docker Compose or other orchestrators
2. **Service Mesh Decision**: Why we're NOT using a service mesh for Phase IV
3. **Secret Management Strategy**: Why kubectl create secret over other secret management solutions
4. **Image Registry Strategy**: Why local images over remote registry for Phase IV

**Recommendation**: Create ADR for "Container Orchestration Platform" as this is a foundational decision that affects all future deployment strategies.

---

## 11. Dependencies and Execution Order

### Phase Dependencies
1. **Setup**: Create directory structure and .dockerignore files
2. **Backend Containerization**: Build and test backend Docker image
3. **Frontend Containerization**: Build and test frontend Docker image (depends on backend service name)
4. **Kubernetes Manifests**: Create deployment and service manifests
5. **Secrets Management**: Create secret creation process
6. **Deployment Automation**: Create deployment script
7. **Validation**: Test full deployment end-to-end

### Critical Path
Setup → Backend Containerization → Kubernetes Manifests → Secrets → Deployment → Validation

Frontend Containerization can happen in parallel with Backend Containerization, but frontend deployment depends on backend service being available.

---

## 12. Testing Strategy

### Unit Testing
- Dockerfile syntax validation: `docker build --dry-run`
- Kubernetes manifest validation: `kubectl apply --dry-run=client`

### Integration Testing
- Backend container can connect to Neon database
- Frontend container can reach backend service
- Health checks pass for all pods
- Rolling update completes without errors

### End-to-End Testing
1. Deploy full stack to clean Minikube cluster
2. Access frontend via browser
3. Perform CRUD operations on tasks
4. Test AI chat functionality
5. Verify data persists in Neon database
6. Test rolling update (rebuild and redeploy)
7. Test pod failure recovery (delete pod, verify restart)

---

**Plan Status**: Ready for task generation
**Next Step**: Generate tasks.md with sequential, dependency-ordered tasks
