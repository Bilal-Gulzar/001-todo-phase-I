# Evolution of Todo - AI Native Development

## 🎯 Project Overview

A full-stack, cloud-native task management application with AI-powered natural language interface, deployed on Kubernetes. Built following Spec-Driven Development (SDD) methodology with comprehensive specifications and architectural decision records.

**Repository:** https://github.com/Bilal-Gulzar/evolution-of-todo

**Current Status:** ✅ Phase IV Complete - Production-Ready Kubernetes Deployment

---

## 📋 Phase Summary

### Phase 1: Foundation ✅
- Vite + React 19 frontend with TypeScript
- Tailwind CSS + Shadcn/ui styling
- Basic task management UI

### Phase 2: Full-Stack Integration ✅
- FastAPI backend with Python 3.12
- PostgreSQL database (Neon)
- JWT authentication
- RESTful API endpoints

### Phase 3: AI Agent Integration ✅
- Panaversity OpenAI Agents SDK
- Groq API (Llama 3.3 70B Versatile)
- Natural language task management
- Four AI tools: create, list, update, delete

### Phase 4: Cloud-Native Deployment ✅
- Kubernetes orchestration (Minikube)
- Docker containerization with multi-stage builds
- Horizontal scaling (2 replicas per service)
- Secure secret management (Kubernetes Secrets)
- Zero-downtime rolling updates
- Automated deployment script

---

## 🚀 Phase 4: Cloud-Native Deployment

### Architecture Overview

```
┌─────────────────────────────────────────┐
│         Kubernetes Cluster              │
│                                         │
│  Frontend (NodePort:30080)              │
│    ↓ 2 replicas                         │
│    ↓ Vite + React + Nginx               │
│    ↓                                    │
│    → Backend (ClusterIP:8000)           │
│        ↓ 2 replicas                     │
│        ↓ FastAPI + AI Agent             │
│        ↓                                │
│        → Neon PostgreSQL (External)     │
│        → Groq API (External)            │
└─────────────────────────────────────────┘
```

### Key Features

**Scalability:**
- Horizontal scaling with multiple replicas
- Stateless design for easy scaling
- Load balancing across pods

**Security:**
- Kubernetes Secrets for sensitive data
- Backend not externally accessible (ClusterIP)
- No secrets in code or Docker images

**Reliability:**
- Health checks (liveness + readiness probes)
- Automatic pod restart on failure
- Zero-downtime rolling updates

**Observability:**
- Structured logging to stdout/stderr
- Resource monitoring via kubectl
- Pod and service status visibility

### Deployment Instructions

#### Prerequisites
- Minikube installed and running
- kubectl configured
- Docker installed
- Neon PostgreSQL database created
- Groq API key obtained

#### Quick Start (Automated)

```bash
# One-command deployment
bash deploy.sh
```

The script will:
1. Check prerequisites (Minikube, kubectl, Docker)
2. Start Minikube if not running
3. Configure Docker environment
4. Build Docker images
5. Create secrets (prompts for values)
6. Deploy all Kubernetes resources
7. Wait for deployments to be ready
8. Display access URL

#### Manual Deployment

```bash
# 1. Start Minikube
minikube start --driver=docker

# 2. Configure Docker to use Minikube's daemon
# Linux/Mac:
eval $(minikube docker-env)
# Windows (PowerShell):
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 3. Build Docker images
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest \
  --build-arg VITE_API_URL=http://backend-service:8000/api/v1 \
  ./frontend

# 4. Create Kubernetes secrets
bash k8s/create-secrets.sh
# Or manually:
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require" \
  --from-literal=OPENAI_API_KEY="gsk_..."

# 5. Deploy to Kubernetes
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# 6. Wait for deployments
kubectl rollout status deployment/backend-deployment
kubectl rollout status deployment/frontend-deployment

# 7. Access the application
minikube service frontend-service
# Or get URL: http://$(minikube ip):30080
```

#### Verification Commands

```bash
# Check all resources
kubectl get all

# View logs
kubectl logs -l app=todo-backend --tail=50
kubectl logs -l app=todo-frontend --tail=50

# Check pod health
kubectl describe pod <pod-name>

# Monitor resource usage
kubectl top pods

# Check service endpoints
kubectl get endpoints
```

#### Scaling

```bash
# Scale backend
kubectl scale deployment backend-deployment --replicas=3

# Scale frontend
kubectl scale deployment frontend-deployment --replicas=3

# Verify scaling
kubectl get pods -w
```

#### Updates

```bash
# Rebuild image
docker build -t todo-backend:latest ./backend

# Rolling update (zero downtime)
kubectl rollout restart deployment/backend-deployment

# Monitor rollout
kubectl rollout status deployment/backend-deployment
```

#### Cleanup

```bash
# Delete all Kubernetes resources
kubectl delete -f k8s/

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop
```

### Docker Compose (Local Testing Alternative)

For local testing without Kubernetes:

```bash
# Start all services
docker-compose up --build

# Access:
# - Frontend: http://localhost:3000
# - Backend API: http://localhost:8000/docs
# - Database: localhost:5432

# Stop services
docker-compose down -v
```

---

## 🏗️ Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.12)
- **Database:** PostgreSQL (Neon - Cloud SaaS)
- **ORM:** SQLModel
- **Authentication:** JWT with bcrypt
- **AI Agent:** Panaversity OpenAI Agents SDK (v0.8.1)
- **LLM:** Groq API (Llama 3.3 70B Versatile)

### Frontend
- **Framework:** Vite + React 19
- **Language:** TypeScript
- **Styling:** Tailwind CSS + Shadcn/ui
- **State Management:** React Hooks + TanStack Query
- **Authentication:** JWT tokens (client-side)
- **Production Server:** Nginx (in Docker)

### Infrastructure
- **Orchestration:** Kubernetes (Minikube for local)
- **Containerization:** Docker (multi-stage builds)
  - Backend: Python 3.12-slim with uv package manager
  - Frontend: Node 20-alpine builder + Nginx alpine runtime
- **Secrets:** Kubernetes Secrets (base64 encoded)
- **Services:** ClusterIP (backend), NodePort (frontend)
- **Health Checks:** Liveness + Readiness probes
- **Resource Limits:** 256Mi-512Mi memory, 250m-500m CPU per pod

---

## 📁 Project Structure

```
evolution-of-todo/
├── backend/
│   ├── app/
│   │   ├── agents/          # AI agent implementation
│   │   ├── api/             # API endpoints
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   ├── config.py        # Configuration
│   │   ├── database.py      # Database connection
│   │   └── main.py          # FastAPI app
│   ├── Dockerfile           # Backend container
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # React components
│   │   ├── contexts/        # Auth context
│   │   └── types/           # TypeScript types
│   ├── Dockerfile           # Frontend container (multi-stage)
│   ├── .dockerignore        # Exclude node_modules from build
│   └── package.json         # Node dependencies
├── k8s/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   └── secrets.yaml         # Template (not committed with real values)
├── specs/
│   └── phase-4-kubernetes.md    # Detailed specification
├── history/
│   └── adr/
│       └── 004-kubernetes-orchestration.md  # Architectural decisions
├── docker-compose.yml       # Local testing
├── PHASE4_DEPLOYMENT.md     # Deployment guide
└── README.md                # This file
```

---

## 🔐 Security Considerations

### Secrets Management
- ✅ No secrets in git repository
- ✅ No secrets in Docker images
- ✅ Kubernetes Secrets for runtime injection
- ✅ Environment variables only

### Network Security
- ✅ Backend not externally accessible (ClusterIP)
- ✅ Frontend as single entry point
- ✅ SSL/TLS for database connections (Neon)

### Authentication
- ✅ JWT tokens with expiration
- ✅ Password hashing with bcrypt
- ✅ Token validation on every request

---

## 📊 Stateful vs Stateless Design

### Current Architecture: **Fully Stateless**

**Backend Pods:**
- No local data storage
- All state in external Neon PostgreSQL
- Any pod can handle any request
- Enables horizontal scaling

**Frontend Pods:**
- No server-side sessions
- JWT tokens stored client-side
- Any pod can serve any user
- Enables horizontal scaling

**Benefits:**
- ✅ Simple scaling (just increase replicas)
- ✅ No data loss on pod restart
- ✅ No persistent volumes needed
- ✅ Easy rolling updates

**Trade-offs:**
- ⚠️ Dependency on external database
- ⚠️ Network latency to Neon
- ⚠️ No local caching (future: Redis)

---

## 🎓 Spec-Driven Development (SDD)

This project follows SDD methodology:

### Specifications
- **[Phase 4 Specification](specs/phase-4-kubernetes.md)**: Comprehensive functional and non-functional requirements

### Architectural Decision Records (ADRs)
- **[ADR-004: Kubernetes Orchestration](history/adr/004-kubernetes-orchestration.md)**: Service exposure, secret management, stateless design decisions

### Key Principles
1. **Specification First**: Requirements documented before implementation
2. **Decision Documentation**: All significant decisions recorded with rationale
3. **Traceability**: Clear link between requirements and implementation
4. **Iterative Refinement**: Specs updated as understanding evolves

---

## 🚦 Running Locally (Development)

### Backend (Standalone)
```bash
cd backend
pip install -r requirements.txt

# Create .env file:
# DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
# GROQ_API_KEY=your_groq_key

uvicorn app.main:app --reload --port 8001
```

### Frontend (Standalone)
```bash
cd frontend
npm install

# Create .env.local file:
# NEXT_PUBLIC_API_URL=http://localhost:8001/api/v1

npm run dev
```

Access: http://localhost:3000

---

## 📈 Future Enhancements

### Production Readiness
- [ ] Ingress controller for proper routing
- [ ] TLS/SSL certificates
- [ ] Horizontal Pod Autoscaler (HPA)
- [ ] Resource quotas and limits
- [ ] Network policies

### Observability
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Distributed tracing (Jaeger)
- [ ] Centralized logging (ELK stack)

### Performance
- [ ] Redis cache layer
- [ ] Database connection pooling
- [ ] CDN for static assets
- [ ] Image optimization

### Resilience
- [ ] Pod Disruption Budgets (PDB)
- [ ] Circuit breakers
- [ ] Rate limiting
- [ ] Retry policies with exponential backoff

---

## 📚 Documentation

- **[Phase 4 Specification](specs/phase-4-kubernetes.md)**: Detailed requirements and architecture
- **[ADR-004: Kubernetes Orchestration](history/adr/004-kubernetes-orchestration.md)**: Design decisions and rationale
- **[Deployment Guide](PHASE4_DEPLOYMENT.md)**: Step-by-step deployment instructions with troubleshooting

---

## 🏆 Hackathon Submission

**Phase 4 Completion Date:** February 8, 2026

**Key Achievements:**
- ✅ Full Kubernetes deployment with 4 pods (2 backend, 2 frontend)
- ✅ Secure secret management (no hardcoded credentials)
- ✅ Zero-downtime rolling updates
- ✅ Horizontal scaling capability
- ✅ Production-ready architecture
- ✅ Comprehensive documentation (specs + ADRs)
- ✅ Spec-Driven Development methodology

**Demo Instructions:**
1. Clone repository
2. Follow "Quick Start" section above
3. Access application via `minikube service frontend-service`
4. Test AI chat: "Add a meeting with John at 3pm"
5. Verify task appears in dashboard
6. Scale deployment: `kubectl scale deployment backend-deployment --replicas=3`
7. Observe zero-downtime scaling

---

## 📞 Support

For issues or questions:
- Check [Deployment Guide](PHASE4_DEPLOYMENT.md) troubleshooting section
- Review [Phase 4 Specification](specs/phase-4-kubernetes.md)
- Examine pod logs: `kubectl logs -l app=todo-backend`

---

**Built with ❤️ using Spec-Driven Development**
