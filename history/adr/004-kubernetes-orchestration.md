# ADR-004: Kubernetes Orchestration Strategy

**Status:** ✅ Accepted
**Date:** 2026-02-08
**Deciders:** Development Team
**Technical Story:** Phase 4 - Cloud-Native Deployment

---

## Context and Problem Statement

The Todo application (Phases 1-3) runs successfully as a monolithic deployment with separate backend and frontend processes. For Phase 4, we need to transform this into a cloud-native, container-orchestrated system that supports:

- Horizontal scaling for high availability
- Zero-downtime deployments
- Secure configuration management
- Production-ready deployment patterns

**Key Questions:**
1. How should we expose services (internal vs external)?
2. How should we manage sensitive configuration (database credentials, API keys)?
3. What deployment strategy ensures reliability?
4. How do we handle stateful vs stateless components?

---

## Decision Drivers

### Technical Requirements
- **Scalability:** Must support 2-10 replicas per service
- **Security:** No secrets in code or Docker images
- **Reliability:** Zero-downtime deployments, automatic recovery
- **Simplicity:** Easy to deploy on Minikube for development

### Constraints
- **Environment:** Minikube (local Kubernetes) for development/demo
- **Database:** External Neon PostgreSQL (not in cluster)
- **AI Service:** External Groq API (not in cluster)
- **Timeline:** Hackathon deadline (limited time for complex solutions)

### Non-Functional Priorities
1. Security (P0)
2. Reliability (P0)
3. Simplicity (P1)
4. Performance (P2)

---

## Considered Options

### Option 1: Docker Compose Only
**Description:** Use Docker Compose for orchestration, skip Kubernetes.

**Pros:**
- Simpler configuration
- Faster to implement
- No Kubernetes learning curve

**Cons:**
- Not cloud-native
- Limited scaling capabilities
- No built-in health checks
- Not production-ready
- Doesn't meet Phase 4 requirements

**Decision:** ❌ Rejected - Doesn't meet hackathon requirements for Kubernetes deployment.

---

### Option 2: Kubernetes with LoadBalancer Services
**Description:** Expose both frontend and backend via LoadBalancer services.

**Pros:**
- Production-grade external access
- Automatic external IP assignment
- Standard cloud provider pattern

**Cons:**
- Requires cloud provider (AWS/GCP/Azure)
- Doesn't work on Minikube without MetalLB
- Backend shouldn't be externally accessible (security)
- Overkill for development environment

**Decision:** ❌ Rejected - Incompatible with Minikube, violates security principle (backend exposure).

---

### Option 3: Kubernetes with Ingress Controller
**Description:** Use Ingress for routing, ClusterIP services for both frontend and backend.

**Pros:**
- Production-grade routing
- Single entry point
- Path-based routing
- TLS termination support

**Cons:**
- Requires Ingress controller installation (nginx/traefik)
- Additional complexity
- Overkill for simple two-service architecture
- More time to implement

**Decision:** ❌ Rejected - Too complex for hackathon timeline, future enhancement candidate.

---

### Option 4: Kubernetes with NodePort (Frontend) + ClusterIP (Backend)
**Description:**
- Frontend: NodePort service (external access via Minikube IP:30080)
- Backend: ClusterIP service (internal-only access)

**Pros:**
- ✅ Works perfectly on Minikube
- ✅ Backend not externally accessible (security)
- ✅ Simple configuration
- ✅ Frontend accessible for demo
- ✅ Follows principle of least privilege
- ✅ Easy to upgrade to Ingress later

**Cons:**
- NodePort not ideal for production (use Ingress instead)
- Port range limited (30000-32767)

**Decision:** ✅ **ACCEPTED** - Best balance of simplicity, security, and Minikube compatibility.

---

## Decision: Service Exposure Strategy

### Backend Service: ClusterIP (Internal Only)

**Rationale:**
1. **Security:** Backend API should not be directly accessible from outside the cluster
2. **Architecture:** Frontend acts as the only entry point (API gateway pattern)
3. **Flexibility:** Easy to add authentication/rate limiting at frontend layer
4. **Best Practice:** Internal services should use ClusterIP by default

**Configuration:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP  # Internal only
  selector:
    app: todo-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
```

**Access Pattern:**
- Frontend pods access via: `http://backend-service:8000`
- Kubernetes DNS resolves service name to ClusterIP
- Load balancing across backend pods automatic

### Frontend Service: NodePort (External Access)

**Rationale:**
1. **Minikube Compatibility:** NodePort works out-of-the-box on Minikube
2. **Demo-Friendly:** Easy to access via `http://<minikube-ip>:30080`
3. **Simplicity:** No additional components required
4. **Upgrade Path:** Can switch to Ingress in production without code changes

**Configuration:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort  # External access
  selector:
    app: todo-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
    nodePort: 30080  # Fixed port for consistency
```

**Access Pattern:**
- External users access via: `http://<minikube-ip>:30080`
- Minikube provides IP via: `minikube ip`
- Or use: `minikube service frontend-service` (auto-opens browser)

---

## Decision: Secret Management Strategy

### Option A: Environment Variables in Deployment YAML
**Pros:** Simple, no additional resources
**Cons:** ❌ Secrets visible in git, insecure, violates best practices

### Option B: ConfigMaps
**Pros:** Kubernetes-native, easy to update
**Cons:** ❌ Not encrypted, visible in plain text, not suitable for secrets

### Option C: Kubernetes Secrets
**Pros:** ✅ Designed for sensitive data, base64 encoded, separate from code
**Cons:** Base64 is not encryption (but acceptable for Minikube demo)

### Option D: External Secret Manager (Vault, AWS Secrets Manager)
**Pros:** True encryption, audit logs, rotation
**Cons:** ❌ Too complex for hackathon, requires additional infrastructure

**Decision:** ✅ **Kubernetes Secrets (Option C)** - Best balance of security and simplicity.

### Secret Management Implementation

**Creation:**
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require" \
  --from-literal=GROQ_API_KEY="gsk_..."
```

**Injection:**
```yaml
env:
- name: DATABASE_URL
  valueFrom:
    secretKeyRef:
      name: todo-secrets
      key: DATABASE_URL
- name: GROQ_API_KEY
  valueFrom:
    secretKeyRef:
      name: todo-secrets
      key: GROQ_API_KEY
```

**Security Properties:**
- ✅ Not stored in git repository
- ✅ Not baked into Docker images
- ✅ Injected at runtime as environment variables
- ✅ Base64 encoded (obfuscated, not encrypted)
- ✅ Can be encrypted at rest in production (etcd encryption)

**Rationale:**
1. **Separation of Concerns:** Secrets separate from application code
2. **Flexibility:** Easy to update without rebuilding images
3. **Security:** Not visible in `kubectl describe pod` output
4. **Best Practice:** Standard Kubernetes pattern for sensitive data

---

## Decision: Stateless Architecture

### Backend: Stateless Design

**Decision:** Backend pods are fully stateless.

**Rationale:**
1. **Scalability:** Any pod can handle any request
2. **Reliability:** Pod restarts don't lose data
3. **Simplicity:** No need for StatefulSets or persistent volumes

**Implementation:**
- All application state stored in external Neon PostgreSQL
- No local file storage
- No in-memory sessions
- JWT tokens for authentication (stateless)

**Trade-offs:**
- ✅ Easy horizontal scaling
- ✅ Simple rolling updates
- ❌ Network latency to external database
- ❌ Dependency on database availability

### Frontend: Stateless Design

**Decision:** Frontend pods are fully stateless.

**Rationale:**
1. **Scalability:** Any pod can serve any user
2. **Simplicity:** No session affinity required
3. **Next.js:** Server-side rendering is stateless by design

**Implementation:**
- No server-side sessions
- JWT tokens stored client-side
- API calls to backend for all data
- Static assets served from container

**Trade-offs:**
- ✅ Easy horizontal scaling
- ✅ No sticky sessions needed
- ❌ No server-side caching (could add Redis later)

---

## Decision: Multi-Stage Docker Builds

### Frontend: Multi-Stage Build

**Decision:** Use multi-stage Docker build for frontend.

**Rationale:**
1. **Size Optimization:** Final image ~60% smaller
2. **Security:** No build tools in production image
3. **Performance:** Faster deployments, less network transfer

**Implementation:**
```dockerfile
# Stage 1: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
RUN npm run build

# Stage 2: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
CMD ["npm", "start"]
```

**Benefits:**
- Builder stage: 800MB (includes dev dependencies, source code)
- Runner stage: 320MB (only production artifacts)
- 60% size reduction improves deployment speed

### Backend: Single-Stage Build

**Decision:** Use single-stage build for backend.

**Rationale:**
1. **Simplicity:** Python apps don't benefit as much from multi-stage
2. **Dependencies:** psycopg2 requires compilation (needs gcc in runtime)
3. **Size:** Already using slim base image (python:3.12-slim)

**Implementation:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y gcc libpq-dev
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Trade-off:** Could use multi-stage to remove gcc after building psycopg2, but complexity not worth ~50MB savings for hackathon demo.

---

## Decision: Health Check Strategy

### Liveness Probes

**Decision:** HTTP GET on application endpoints.

**Configuration:**
- Backend: `GET /docs` (FastAPI auto-generated docs)
- Frontend: `GET /` (Next.js home page)
- Initial delay: 30 seconds (allow startup time)
- Period: 10 seconds

**Rationale:**
1. **Reliability:** Kubernetes restarts unhealthy pods automatically
2. **Simplicity:** No custom health check endpoints needed
3. **Coverage:** Tests that application is responding

### Readiness Probes

**Decision:** Same endpoints as liveness, shorter initial delay.

**Configuration:**
- Initial delay: 10 seconds
- Period: 5 seconds

**Rationale:**
1. **Traffic Management:** Pods not added to service until ready
2. **Zero Downtime:** Old pods stay in service until new pods ready
3. **Fast Recovery:** Shorter period for quicker detection

---

## Consequences

### Positive

1. **Security:** Backend not externally accessible, secrets properly managed
2. **Scalability:** Stateless design enables easy horizontal scaling
3. **Reliability:** Health checks ensure automatic recovery
4. **Simplicity:** Works on Minikube without additional components
5. **Demo-Ready:** Easy to access and demonstrate
6. **Production Path:** Clear upgrade path to Ingress and external secret managers

### Negative

1. **NodePort Limitation:** Not ideal for production (need Ingress)
2. **Secret Encoding:** Base64 is not encryption (need etcd encryption in prod)
3. **External Dependencies:** Relies on Neon and Groq availability
4. **No Caching:** Could benefit from Redis for performance

### Neutral

1. **Minikube-Specific:** Some configurations specific to local development
2. **Manual Scaling:** No HPA (Horizontal Pod Autoscaler) yet
3. **Basic Monitoring:** Relies on kubectl commands, no Prometheus/Grafana

---

## Future Improvements

### Short-Term (Next Sprint)
- [ ] Add Ingress controller for production-grade routing
- [ ] Implement Horizontal Pod Autoscaler (HPA)
- [ ] Add Redis for caching and session management
- [ ] Configure etcd encryption for secrets at rest

### Medium-Term (Next Quarter)
- [ ] Migrate to managed Kubernetes (EKS/GKE/AKS)
- [ ] Implement external secret manager (Vault/AWS Secrets Manager)
- [ ] Add Prometheus + Grafana for monitoring
- [ ] Implement distributed tracing (Jaeger)

### Long-Term (Future Phases)
- [ ] Service mesh (Istio/Linkerd) for advanced traffic management
- [ ] Multi-cluster deployment for disaster recovery
- [ ] GitOps with ArgoCD for declarative deployments
- [ ] Cost optimization with spot instances and autoscaling

---

## References

- [Kubernetes Service Types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [12-Factor App: Config](https://12factor.net/config)
- [Docker Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Kubernetes Health Checks](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

## Approval

**Approved By:** Development Team
**Date:** 2026-02-08
**Review Status:** ✅ Accepted and Implemented

---

**Document History:**
- 2026-02-08: Initial ADR created for Phase 4 Kubernetes deployment
