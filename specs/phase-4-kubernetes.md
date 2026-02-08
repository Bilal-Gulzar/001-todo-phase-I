# Phase 4: Kubernetes Deployment Specification

**Status:** ✅ Implemented
**Version:** 1.0
**Last Updated:** 2026-02-08
**Owner:** Development Team

---

## 1. Overview

Phase 4 transforms the Todo application into a cloud-native, container-orchestrated system using Kubernetes. This phase focuses on production-ready deployment patterns, scalability, and operational excellence.

### 1.1 Goals

- Deploy application to Kubernetes cluster (Minikube for local, production-ready architecture)
- Implement horizontal scaling with multiple replicas
- Secure sensitive configuration using Kubernetes Secrets
- Establish clear service boundaries (internal vs external access)
- Enable zero-downtime deployments

### 1.2 Non-Goals

- Multi-cluster deployment
- Service mesh implementation (Istio/Linkerd)
- Persistent volume claims (using external Neon PostgreSQL)
- Horizontal Pod Autoscaling (HPA) - future enhancement

---

## 2. Functional Requirements

### FR-1: Container Orchestration
**Priority:** P0 (Critical)

The application MUST be deployable to a Kubernetes cluster with the following characteristics:

- **Backend Service:**
  - 2 replicas for high availability
  - ClusterIP service (internal only)
  - Port 8000 exposed internally
  - Health checks: liveness and readiness probes on `/docs`

- **Frontend Service:**
  - 2 replicas for load distribution
  - NodePort service (external access)
  - Port 3000 internally, 30080 externally
  - Health checks: liveness and readiness probes on `/`

**Acceptance Criteria:**
- ✅ `kubectl get pods` shows 4 running pods (2 backend, 2 frontend)
- ✅ `kubectl get svc` shows both services with correct types
- ✅ Frontend accessible via `http://<minikube-ip>:30080`
- ✅ Backend NOT accessible externally (ClusterIP only)

### FR-2: Service Communication
**Priority:** P0 (Critical)

Frontend MUST communicate with backend using Kubernetes DNS service discovery.

- Frontend uses `http://backend-service:8000` (NOT localhost)
- Backend service name resolves to ClusterIP within cluster
- No hardcoded IP addresses

**Acceptance Criteria:**
- ✅ Frontend environment variable `NEXT_PUBLIC_API_URL=http://backend-service:8000`
- ✅ API calls from frontend successfully reach backend pods
- ✅ Load balancing across backend replicas works automatically

### FR-3: External Database Integration
**Priority:** P0 (Critical)

Backend MUST connect to external Neon PostgreSQL database using connection string from Kubernetes Secret.

- Database is NOT deployed in cluster (external SaaS)
- Connection string includes SSL mode for security
- Backend pods can connect from any node

**Acceptance Criteria:**
- ✅ Backend successfully connects to Neon PostgreSQL
- ✅ Database operations (CRUD) work correctly
- ✅ Connection pooling handles multiple replicas

### FR-4: AI Agent Integration
**Priority:** P0 (Critical)

Backend MUST integrate with Groq API for AI-powered task management using API key from Kubernetes Secret.

- API key stored securely in Secret
- Agent functionality works across all backend replicas
- No API key leakage in logs or error messages

**Acceptance Criteria:**
- ✅ Chat endpoint `/api/v1/chat` responds successfully
- ✅ AI agent can create, list, update, delete tasks
- ✅ Groq API key loaded from environment variable

---

## 3. Non-Functional Requirements

### NFR-1: Scalability
**Priority:** P0 (Critical)

The system MUST support horizontal scaling without code changes.

- **Metrics:**
  - Support 2-10 replicas per service
  - Linear performance scaling up to 5 replicas
  - No session affinity required (stateless design)

- **Constraints:**
  - Each pod: 256Mi-512Mi memory, 250m-500m CPU
  - Startup time: < 30 seconds per pod
  - Ready time: < 10 seconds after startup

**Acceptance Criteria:**
- ✅ `kubectl scale deployment backend-deployment --replicas=3` works without errors
- ✅ All replicas pass health checks
- ✅ Load distributed evenly across replicas

### NFR-2: Security
**Priority:** P0 (Critical)

Sensitive configuration MUST be stored in Kubernetes Secrets, never in code or ConfigMaps.

- **Protected Data:**
  - `DATABASE_URL`: Neon PostgreSQL connection string
  - `GROQ_API_KEY`: Groq API authentication key

- **Security Measures:**
  - Secrets encoded in base64 (Kubernetes default)
  - No secrets in Docker images
  - No secrets in git repository
  - Environment variable injection at runtime

**Acceptance Criteria:**
- ✅ `kubectl get secret todo-secrets` exists
- ✅ No plaintext secrets in any committed files
- ✅ Pods receive secrets as environment variables
- ✅ Secret values not visible in `kubectl describe pod`

### NFR-3: Reliability
**Priority:** P1 (High)

The system MUST support zero-downtime deployments and automatic recovery.

- **Health Checks:**
  - Liveness probe: Restart unhealthy pods
  - Readiness probe: Remove from service until ready
  - Initial delay: 30s (liveness), 10s (readiness)

- **Deployment Strategy:**
  - Rolling update (default)
  - Max unavailable: 1 pod
  - Max surge: 1 pod

**Acceptance Criteria:**
- ✅ `kubectl rollout restart deployment/backend-deployment` causes zero downtime
- ✅ Failed pods automatically restart
- ✅ Unhealthy pods removed from load balancer

### NFR-4: Observability
**Priority:** P2 (Medium)

The system SHOULD provide visibility into application state and behavior.

- **Logging:**
  - Structured logs to stdout/stderr
  - Accessible via `kubectl logs`
  - Includes request IDs for tracing

- **Metrics:**
  - Pod resource usage visible in `kubectl top pods`
  - Service endpoints visible in `kubectl get endpoints`

**Acceptance Criteria:**
- ✅ `kubectl logs -l app=todo-backend` shows application logs
- ✅ Logs include startup messages and error details
- ✅ Resource usage within defined limits

---

## 4. Deployment Blueprint

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────┐
│           Minikube Cluster              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Frontend Service (NodePort)     │  │
│  │  Port: 30080 (external)          │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Frontend Pods (2 replicas)      │  │
│  │  - Image: todo-frontend:latest   │  │
│  │  - Port: 3000                    │  │
│  │  - ENV: NEXT_PUBLIC_API_URL      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│               │ http://backend-service:8000
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Backend Service (ClusterIP)     │  │
│  │  Port: 8000 (internal only)      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Backend Pods (2 replicas)       │  │
│  │  - Image: todo-backend:latest    │  │
│  │  - Port: 8000                    │  │
│  │  - ENV: DATABASE_URL (secret)    │  │
│  │  - ENV: GROQ_API_KEY (secret)    │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Kubernetes Secrets              │  │
│  │  - DATABASE_URL                  │  │
│  │  - GROQ_API_KEY                  │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
           │
           │ External Connections
           ▼
    ┌──────────────────┐
    │ Neon PostgreSQL  │ (Cloud SaaS)
    └──────────────────┘
    ┌──────────────────┐
    │ Groq API         │ (Cloud SaaS)
    └──────────────────┘
```

### 4.2 Dockerization Strategy

#### Backend Dockerfile
- **Base Image:** `python:3.12-slim`
- **Build Strategy:** Single-stage (simple, fast)
- **Dependencies:** Installed from `requirements.txt`
- **Entry Point:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Size Optimization:** Minimal system dependencies, no cache

#### Frontend Dockerfile
- **Base Image:** `node:20-alpine`
- **Build Strategy:** Multi-stage (builder + runner)
- **Stage 1 (Builder):**
  - Install dependencies with `npm install`
  - Build Next.js app with `npm run build`
  - Accept `NEXT_PUBLIC_API_URL` as build argument
- **Stage 2 (Runner):**
  - Copy built artifacts from builder
  - Production-only dependencies
  - Minimal attack surface
- **Size Optimization:** Alpine base, multi-stage reduces final image size by ~60%

### 4.3 Service Mapping

| Service | Type | Internal Port | External Port | Purpose |
|---------|------|---------------|---------------|---------|
| `backend-service` | ClusterIP | 8000 | N/A | Internal API access only |
| `frontend-service` | NodePort | 3000 | 30080 | External user access |

**Design Rationale:**
- Backend is ClusterIP to prevent direct external access (security)
- Frontend is NodePort for easy Minikube access (LoadBalancer requires cloud provider)
- In production, use Ingress controller instead of NodePort

### 4.4 Secret Management

**Creation Method:**
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require" \
  --from-literal=GROQ_API_KEY="gsk_..."
```

**Injection Method:**
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-secrets
      key: DATABASE_URL
```

**Security Properties:**
- Secrets stored in etcd (encrypted at rest in production)
- Base64 encoded (not encrypted, but obfuscated)
- Injected as environment variables at pod creation
- Not visible in `kubectl describe pod` output
- Not included in Docker images

### 4.5 Stateful vs Stateless Design

**Current Architecture: Stateless**

- **Backend Pods:** Stateless
  - No local data storage
  - All state in external Neon PostgreSQL
  - Any pod can handle any request
  - Enables horizontal scaling

- **Frontend Pods:** Stateless
  - No server-side sessions
  - JWT tokens stored client-side
  - Any pod can serve any user
  - Enables horizontal scaling

**Benefits:**
- Simple scaling: just increase replica count
- No data loss on pod restart
- No need for persistent volumes
- Easy rolling updates

**Trade-offs:**
- Dependency on external database availability
- Network latency to Neon PostgreSQL
- No local caching (could add Redis in future)

---

## 5. Deployment Procedure

### 5.1 Prerequisites
- Minikube installed and running
- kubectl configured
- Docker installed
- Neon PostgreSQL database created
- Groq API key obtained

### 5.2 Deployment Steps

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Configure Docker for Minikube
eval $(minikube docker-env)  # Linux/Mac
# OR
& minikube -p minikube docker-env --shell powershell | Invoke-Expression  # Windows

# 3. Build Docker images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 \
  ./frontend

# 4. Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="YOUR_NEON_URL" \
  --from-literal=GROQ_API_KEY="YOUR_GROQ_KEY"

# 5. Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# 6. Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 7. Verify deployment
kubectl get pods
kubectl get svc

# 8. Access application
minikube service frontend-service
```

### 5.3 Verification Checklist

- [ ] All 4 pods in Running state
- [ ] All pods pass readiness checks
- [ ] Backend logs show successful database connection
- [ ] Frontend accessible via browser
- [ ] API calls from frontend to backend succeed
- [ ] AI chat functionality works
- [ ] Task CRUD operations work

---

## 6. Operational Considerations

### 6.1 Scaling

**Horizontal Scaling:**
```bash
# Scale backend
kubectl scale deployment backend-deployment --replicas=3

# Scale frontend
kubectl scale deployment frontend-deployment --replicas=3
```

**Vertical Scaling:**
Edit deployment YAML to increase resource limits, then apply.

### 6.2 Updates

**Rolling Update:**
```bash
# Rebuild image with same tag
docker build -t todo-backend:latest ./backend

# Restart deployment (pulls new image)
kubectl rollout restart deployment/backend-deployment

# Monitor rollout
kubectl rollout status deployment/backend-deployment
```

### 6.3 Monitoring

```bash
# View logs
kubectl logs -l app=todo-backend --tail=50 -f

# Check resource usage
kubectl top pods

# Check endpoints
kubectl get endpoints

# Describe pod for troubleshooting
kubectl describe pod <pod-name>
```

### 6.4 Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop
```

---

## 7. Future Enhancements

### 7.1 Production Readiness
- [ ] Ingress controller for proper routing
- [ ] TLS/SSL certificates
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] Resource quotas and limits
- [ ] Network policies

### 7.2 Observability
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Distributed tracing (Jaeger)
- [ ] Centralized logging (ELK stack)

### 7.3 Resilience
- [ ] Pod Disruption Budgets (PDB)
- [ ] Circuit breakers
- [ ] Rate limiting
- [ ] Retry policies

### 7.4 Data Management
- [ ] Redis cache for performance
- [ ] Database connection pooling
- [ ] Backup and restore procedures

---

## 8. References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [12-Factor App Methodology](https://12factor.net/)
- [ADR-004: Kubernetes Orchestration](../history/adr/004-kubernetes-orchestration.md)

---

**Document History:**
- 2026-02-08: Initial specification created for Phase 4 deployment
