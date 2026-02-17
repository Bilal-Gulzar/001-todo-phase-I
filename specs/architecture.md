# Evolution of Todo - Application Architecture

**Version**: 4.0
**Last Updated**: 2026-02-18
**Status**: Active

---

## Overview

This document describes the architectural evolution of the Evolution of Todo application from local development (Phases I-III) to cloud-native Kubernetes deployment (Phase IV).

---

## Phase I-III: Local Development Architecture

### System Context

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Next.js Frontend (localhost:3000)          │
│              - React 19 + TypeScript                    │
│              - Tailwind CSS + Shadcn/ui                 │
│              - Client-side JWT storage                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI Backend (localhost:8000)           │
│              - Python 3.12                              │
│              - JWT Authentication                       │
│              - AI Agent (Groq API)                      │
└────────────────────┬────────────────────────────────────┘
                     │ PostgreSQL Protocol
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Neon PostgreSQL (Cloud SaaS)               │
│              - Managed PostgreSQL                       │
│              - SSL/TLS connections                      │
└─────────────────────────────────────────────────────────┘
```

### Characteristics

**Deployment Model**: Local processes
- Frontend: `npm run dev` (development server)
- Backend: `uvicorn app.main:app --reload` (development server)

**Communication**: Direct HTTP on localhost
- Frontend → Backend: `http://localhost:8000/api/v1`
- Backend → Database: Direct connection via DATABASE_URL

**State Management**: Stateless
- No server-side sessions
- JWT tokens stored in browser localStorage
- All persistent state in Neon PostgreSQL

**Scalability**: Single instance
- One frontend process
- One backend process
- No load balancing
- No redundancy

---

## Phase 4: Kubernetes Deployment Architecture

### System Context

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP
                     │ http://<minikube-ip>:30080
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Minikube)              │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Frontend Service (NodePort:30080)                │ │
│  │  - Type: NodePort                                 │ │
│  │  - External access point                          │ │
│  └─────────────────┬─────────────────────────────────┘ │
│                    │ Load balancing                    │
│                    ▼                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Frontend Pods (2 replicas)                     │   │
│  │  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ Pod 1        │  │ Pod 2        │            │   │
│  │  │ Next.js:3000 │  │ Next.js:3000 │            │   │
│  │  │ 256Mi-512Mi  │  │ 256Mi-512Mi  │            │   │
│  │  └──────────────┘  └──────────────┘            │   │
│  └─────────────────┬─────────────────────────────────┘ │
│                    │ http://backend-service:8000       │
│                    │ (Kubernetes DNS)                  │
│                    ▼                                    │
│  ┌───────────────────────────────────────────────────┐ │
│  │  Backend Service (ClusterIP:8000)                │ │
│  │  - Type: ClusterIP                               │ │
│  │  - Internal only (not externally accessible)     │ │
│  └─────────────────┬─────────────────────────────────┘ │
│                    │ Load balancing                    │
│                    ▼                                    │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Backend Pods (2 replicas)                      │   │
│  │  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │ Pod 1        │  │ Pod 2        │            │   │
│  │  │ FastAPI:8000 │  │ FastAPI:8000 │            │   │
│  │  │ 256Mi-512Mi  │  │ 256Mi-512Mi  │            │   │
│  │  └──────────────┘  └──────────────┘            │   │
│  └─────────────────┬─────────────────────────────────┘ │
│                    │                                    │
│  ┌─────────────────▼─────────────────────────────────┐ │
│  │  Kubernetes Secrets                               │ │
│  │  - DATABASE_URL (base64 encoded)                 │ │
│  │  - OPENAI_API_KEY (base64 encoded)               │ │
│  └───────────────────────────────────────────────────┘ │
│                                                         │
└────────────────────┬────────────────────────────────────┘
                     │ External connections
                     ▼
┌─────────────────────────────────────────────────────────┐
│              External Services (Cloud SaaS)             │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │ Neon PostgreSQL      │  │ Groq API             │   │
│  │ (Database)           │  │ (LLM)                │   │
│  └──────────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Characteristics

**Deployment Model**: Container orchestration
- Frontend: Docker container with Next.js production build
- Backend: Docker container with FastAPI + Uvicorn
- Orchestration: Kubernetes (Minikube for local, production-ready architecture)

**Communication**: Kubernetes service discovery
- Frontend → Backend: `http://backend-service:8000` (Kubernetes DNS)
- Backend → Database: Direct connection via DATABASE_URL (from Secret)
- External access: NodePort on port 30080

**State Management**: Stateless (unchanged)
- No server-side sessions
- JWT tokens stored in browser localStorage
- All persistent state in Neon PostgreSQL
- Any pod can handle any request

**Scalability**: Horizontal scaling
- 2 frontend replicas (configurable)
- 2 backend replicas (configurable)
- Automatic load balancing via Kubernetes Services
- Rolling updates with zero downtime

**Reliability**: High availability
- Multiple replicas for redundancy
- Health checks (liveness + readiness probes)
- Automatic pod restart on failure
- Traffic only to healthy pods

**Security**: Defense in depth
- Backend not externally accessible (ClusterIP)
- Secrets managed by Kubernetes (not in code/images)
- Environment variable injection at runtime
- SSL/TLS for external connections

---

## Architectural Comparison

| Aspect | Phase 1-3 (Local) | Phase 4 (Kubernetes) |
|--------|-------------------|----------------------|
| **Deployment** | Local processes (`npm run dev`, `uvicorn --reload`) | Containerized pods in Kubernetes cluster |
| **Instances** | Single instance per service | Multiple replicas (2+ per service) |
| **Load Balancing** | None | Automatic via Kubernetes Services |
| **Service Discovery** | Hardcoded localhost URLs | Kubernetes DNS (`backend-service`) |
| **Secrets** | `.env` files (local) | Kubernetes Secrets (runtime injection) |
| **Scaling** | Manual (start more processes) | Declarative (`kubectl scale`) |
| **Updates** | Stop and restart | Rolling updates (zero downtime) |
| **Health Checks** | None | Liveness + readiness probes |
| **Failure Recovery** | Manual restart | Automatic pod restart |
| **External Access** | Direct to both services | Only frontend via NodePort |
| **Resource Limits** | None | CPU and memory limits per pod |
| **Observability** | Application logs only | Logs + metrics + pod status |

---

## Component Architecture

### Frontend (Next.js)

**Technology Stack**:
- Next.js 14 (App Router)
- React 19
- TypeScript (strict mode)
- Tailwind CSS + Shadcn/ui
- SWR for data fetching

**Key Components**:
- `src/pages/`: Route pages (Dashboard, Login, Signup)
- `src/components/`: Reusable UI components (TaskItem, ChatSidebar, AddTaskForm)
- `src/contexts/`: React contexts (AuthContext for JWT management)
- `src/hooks/`: Custom hooks (useAuth, useTasks)

**Build Strategy** (Phase 4):
- Multi-stage Docker build
- Stage 1: Install dependencies + build Next.js app
- Stage 2: Copy production artifacts only (standalone output)
- Final image: ~200-300MB (optimized)

**Environment Variables**:
- `NEXT_PUBLIC_API_URL`: Backend API base URL
  - Local: `http://localhost:8000/api/v1`
  - Kubernetes: `http://backend-service:8000/api/v1`

---

### Backend (FastAPI)

**Technology Stack**:
- FastAPI (Python 3.12)
- SQLModel (ORM + validation)
- Pydantic (data validation)
- JWT + bcrypt (authentication)
- Panaversity OpenAI Agents SDK (AI agent)
- Groq API (Llama 3.3 70B Versatile)

**Key Modules**:
- `app/api/`: REST API endpoints (tasks, auth, chat)
- `app/models/`: Database models (Task, User)
- `app/services/`: Business logic (auth_service, task_service)
- `app/agents/`: AI agent implementation (task_agent)
- `app/database.py`: Database connection and session management
- `app/config.py`: Configuration from environment variables

**Build Strategy** (Phase 4):
- Single-stage Docker build (Python 3.12-slim)
- Install dependencies from requirements.txt
- Copy application code
- Final image: ~400-500MB

**Environment Variables**:
- `DATABASE_URL`: PostgreSQL connection string (from Kubernetes Secret)
- `OPENAI_API_KEY`: OpenAI/Groq API key (from Kubernetes Secret)
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_ALGORITHM`: JWT algorithm (HS256)

---

### Database (Neon PostgreSQL)

**Technology**: Managed PostgreSQL (Cloud SaaS)

**Schema**:
```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tasks table
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE
);
```

**Connection**:
- Protocol: PostgreSQL wire protocol over SSL/TLS
- Connection string: `postgresql://user:pass@host.neon.tech/db?sslmode=require`
- Pooling: SQLAlchemy connection pool (default settings)

**Deployment Model**: External SaaS (unchanged in Phase 4)
- Not deployed in Kubernetes cluster
- Accessed from backend pods via internet
- Connection string injected via Kubernetes Secret

---

### AI Agent (Groq API)

**Technology**: Panaversity OpenAI Agents SDK + Groq API

**Model**: Llama 3.3 70B Versatile

**Tools** (4 total):
1. `create_task`: Create new task with title and optional description
2. `list_tasks`: List all tasks (optionally filter by completion status)
3. `update_task`: Update task title, description, or completion status
4. `delete_task`: Delete task by ID

**Integration**:
- Backend calls Groq API via OpenAI-compatible SDK
- API key stored in Kubernetes Secret
- Streaming responses for real-time chat experience

---

## Data Flow

### Task Creation Flow (Phase 4)

```
1. User types in chat: "Add meeting with John at 3pm"
   ↓
2. Frontend sends POST /api/v1/chat
   ↓ (http://backend-service:8000)
3. Kubernetes Service load balances to Backend Pod 1 or 2
   ↓
4. Backend Pod calls Groq API with user message + tools
   ↓
5. Groq LLM decides to call create_task tool
   ↓
6. Backend executes create_task function
   ↓
7. Backend inserts task into Neon PostgreSQL
   ↓
8. Backend returns AI response to Frontend
   ↓
9. Frontend displays AI message in chat
   ↓
10. Frontend refreshes task list (GET /api/v1/tasks)
    ↓
11. Kubernetes Service load balances to Backend Pod 1 or 2
    ↓
12. Backend Pod queries Neon PostgreSQL
    ↓
13. Backend returns task list to Frontend
    ↓
14. Frontend displays updated task list
```

**Key Points**:
- Load balancing happens at step 3 and 11 (may hit different pods)
- Stateless design ensures consistency (all state in database)
- Any backend pod can handle any request

---

## Deployment Architecture (Phase 4)

### Kubernetes Resources

**Deployments** (2 total):
1. `backend-deployment`: Manages backend pods
   - Replicas: 2
   - Image: `todo-backend:latest`
   - Resources: 256Mi-512Mi memory, 250m-500m CPU
   - Health checks: Liveness + readiness on `/docs`
   - Environment: DATABASE_URL, OPENAI_API_KEY (from Secret)

2. `frontend-deployment`: Manages frontend pods
   - Replicas: 2
   - Image: `todo-frontend:latest`
   - Resources: 256Mi-512Mi memory, 250m-500m CPU
   - Health checks: Liveness + readiness on `/`
   - Environment: NEXT_PUBLIC_API_URL (hardcoded in image)

**Services** (2 total):
1. `backend-service`: ClusterIP (internal only)
   - Port: 8000
   - Selector: `app: todo-backend`
   - DNS: `backend-service.default.svc.cluster.local`

2. `frontend-service`: NodePort (external access)
   - Port: 3000 (internal), 30080 (external)
   - Selector: `app: todo-frontend`
   - Access: `http://<minikube-ip>:30080`

**Secrets** (1 total):
1. `todo-secrets`: Generic secret
   - `DATABASE_URL`: Neon PostgreSQL connection string
   - `OPENAI_API_KEY`: Groq API key

---

## Scaling Strategy

### Horizontal Scaling

**Current Configuration**:
- Backend: 2 replicas
- Frontend: 2 replicas

**Scaling Commands**:
```bash
# Scale up
kubectl scale deployment backend-deployment --replicas=5
kubectl scale deployment frontend-deployment --replicas=3

# Scale down
kubectl scale deployment backend-deployment --replicas=1
```

**Scaling Considerations**:
- Stateless design enables unlimited horizontal scaling
- Each pod: 256Mi-512Mi memory, 250m-500m CPU
- Typical developer machine (8GB RAM, 4 cores) can handle 4-8 pods
- Production: Scale based on CPU/memory metrics (future: HPA)

### Vertical Scaling

**Current Resource Limits**:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

**Scaling Approach**:
- Edit deployment YAML to increase limits
- Apply changes: `kubectl apply -f k8s/backend-deployment.yaml`
- Kubernetes performs rolling update

---

## Reliability and Resilience

### Health Checks

**Backend**:
- Liveness probe: `GET /docs` (FastAPI auto-generated docs)
  - Initial delay: 30s (allow startup time)
  - Period: 10s
  - Failure threshold: 3 (restart after 30s of failures)
- Readiness probe: `GET /docs`
  - Initial delay: 10s
  - Period: 5s
  - Failure threshold: 3 (remove from service after 15s of failures)

**Frontend**:
- Liveness probe: `GET /`
  - Initial delay: 30s
  - Period: 10s
  - Failure threshold: 3
- Readiness probe: `GET /`
  - Initial delay: 10s
  - Period: 5s
  - Failure threshold: 3

### Failure Scenarios

**Pod Crash**:
1. Pod crashes or becomes unhealthy
2. Liveness probe fails 3 times (30 seconds)
3. Kubernetes restarts pod
4. Pod starts and passes readiness probe
5. Pod added back to service endpoints
6. Total recovery time: ~60 seconds

**Database Connection Failure**:
1. Backend pod cannot connect to Neon PostgreSQL
2. Readiness probe fails (health check depends on DB)
3. Pod removed from service endpoints (no traffic)
4. Other healthy pods continue serving traffic
5. When DB connection restored, pod passes readiness probe
6. Pod added back to service endpoints

**Rolling Update**:
1. New image built and deployment updated
2. Kubernetes creates new pod with new image
3. New pod starts and passes readiness probe
4. Kubernetes terminates one old pod
5. Repeat until all pods updated
6. Max unavailable: 1 pod (always at least 1 pod serving traffic)
7. Zero downtime achieved

---

## Security Architecture

### Network Security

**Layers**:
1. **External → Frontend**: NodePort (30080) - only entry point
2. **Frontend → Backend**: ClusterIP (internal only) - not externally accessible
3. **Backend → Database**: SSL/TLS connection to Neon
4. **Backend → Groq API**: HTTPS connection

**Rationale**:
- Backend API not exposed externally (defense in depth)
- Frontend acts as single entry point (easier to secure)
- All external connections encrypted (SSL/TLS)

### Secrets Management

**Storage**:
- Kubernetes Secrets (base64 encoded in etcd)
- Not committed to git repository
- Not included in Docker images

**Injection**:
- Environment variables at pod creation time
- Secrets mounted from Kubernetes Secret object
- Not visible in `kubectl describe pod` output

**Access Control**:
- Only backend pods have access to secrets
- Frontend does not need secrets (API key baked into image at build time)

### Authentication

**JWT Tokens**:
- Signed with HS256 algorithm
- Expiration: 24 hours
- Stored in browser localStorage (client-side)
- Validated on every backend request

**Password Security**:
- Hashed with bcrypt (cost factor: 12)
- Never stored in plaintext
- Never returned in API responses

---

## Observability

### Logging

**Strategy**: Structured logs to stdout/stderr (Kubernetes standard)

**Access**:
```bash
# View backend logs
kubectl logs -l app=todo-backend --tail=50 -f

# View frontend logs
kubectl logs -l app=todo-frontend --tail=50 -f

# View logs from specific pod
kubectl logs <pod-name>

# View logs from previous crash
kubectl logs <pod-name> --previous
```

**Log Format**:
- Timestamp (ISO 8601)
- Log level (INFO, WARNING, ERROR)
- Request ID (for tracing)
- Message

### Metrics

**Available Metrics**:
```bash
# Pod resource usage
kubectl top pods

# Node resource usage
kubectl top nodes

# Service endpoints
kubectl get endpoints

# Pod status
kubectl get pods -o wide
```

**Future Enhancements**:
- Prometheus for metrics collection
- Grafana for visualization
- Custom application metrics (request rate, latency, error rate)

### Monitoring

**Health Status**:
```bash
# Check all resources
kubectl get all

# Check pod health
kubectl describe pod <pod-name>

# Check service endpoints
kubectl get endpoints backend-service
kubectl get endpoints frontend-service
```

---

## Migration Path (Local → Kubernetes)

### Phase 1-3 → Phase 4 Migration

**No Code Changes Required**:
- Application code remains unchanged
- Same API contracts
- Same database schema
- Same authentication mechanism

**Configuration Changes**:
1. Frontend API URL: `localhost:8000` → `backend-service:8000`
2. Secrets: `.env` files → Kubernetes Secrets
3. Deployment: `npm run dev` → Docker + Kubernetes

**Migration Steps**:
1. Create Dockerfiles for backend and frontend
2. Build Docker images
3. Create Kubernetes manifests (deployments, services)
4. Create Kubernetes Secrets
5. Deploy to Minikube
6. Verify functionality
7. Update documentation

**Rollback Plan**:
- Keep local development setup intact
- Can always run locally with `npm run dev` and `uvicorn --reload`
- Kubernetes deployment is additive, not destructive

---

## Future Architecture Considerations

### Production Deployment

**Changes Needed**:
1. **Ingress Controller**: Replace NodePort with Ingress for proper routing
2. **TLS/SSL**: Add certificates for HTTPS
3. **Cloud Provider**: Deploy to GKE, EKS, or AKS (not Minikube)
4. **Image Registry**: Push images to Docker Hub or cloud registry
5. **Horizontal Pod Autoscaler**: Auto-scale based on CPU/memory
6. **Persistent Volumes**: If adding Redis or other stateful services

### Performance Optimization

**Potential Improvements**:
1. **Redis Cache**: Cache frequently accessed data (task lists)
2. **CDN**: Serve static assets from CDN
3. **Database Connection Pooling**: Optimize database connections
4. **Image Optimization**: Further reduce Docker image sizes

### Observability Enhancement

**Recommended Additions**:
1. **Prometheus + Grafana**: Metrics and dashboards
2. **Jaeger**: Distributed tracing
3. **ELK Stack**: Centralized logging
4. **Alerting**: PagerDuty or similar for on-call

---

## Architectural Decision Records

Key architectural decisions are documented in ADRs:

- **[ADR-004: Kubernetes Orchestration](../history/adr/004-kubernetes-orchestration.md)**: Service exposure strategy, secret management, stateless design

---

**Document Version**: 4.0
**Last Updated**: 2026-02-17
**Next Review**: After Phase 5 (if applicable)
