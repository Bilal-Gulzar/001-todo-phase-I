# Phase 4: Kubernetes Deployment Guide

## Prerequisites

1. **Minikube** installed and running
2. **kubectl** installed and configured
3. **Docker** installed (for building images)

## Deployment Steps

### Step 1: Start Minikube

```bash
minikube start --driver=docker
```

### Step 2: Configure Docker to Use Minikube's Docker Daemon

This allows Minikube to access locally built images without pushing to a registry.

**Windows (PowerShell):**
```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

**Linux/Mac:**
```bash
eval $(minikube docker-env)
```

### Step 3: Build Docker Images

Build both backend and frontend images inside Minikube's Docker environment.

```bash
# Build backend image
docker build -t todo-backend:latest ./backend

# Build frontend image with correct API URL
docker build -t todo-frontend:latest \
  --build-arg NEXT_PUBLIC_API_URL=http://backend-service:8000 \
  ./frontend
```

### Step 4: Create Kubernetes Secrets

**Option A: Edit the secrets.yaml file**

Edit `k8s/secrets.yaml` and replace the placeholder values:
- `DATABASE_URL`: Your Neon PostgreSQL connection string
- `GROQ_API_KEY`: Your Groq API key

Then apply:
```bash
kubectl apply -f k8s/secrets.yaml
```

**Option B: Create secrets directly (Recommended for production)**

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:password@host.neon.tech/database?sslmode=require" \
  --from-literal=GROQ_API_KEY="your-groq-api-key-here"
```

### Step 5: Deploy Backend

```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
```

Verify backend is running:
```bash
kubectl get pods -l app=todo-backend
kubectl logs -l app=todo-backend
```

### Step 6: Deploy Frontend

```bash
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
```

Verify frontend is running:
```bash
kubectl get pods -l app=todo-frontend
kubectl logs -l app=todo-frontend
```

### Step 7: Access the Application

Get the Minikube IP and access the frontend:

```bash
minikube ip
```

Then open in browser:
```
http://<minikube-ip>:30080
```

Or use Minikube's service command:
```bash
minikube service frontend-service
```

## Verification Commands

### Check All Resources

```bash
kubectl get all
```

### Check Secrets

```bash
kubectl get secrets
kubectl describe secret todo-secrets
```

### Check Logs

```bash
# Backend logs
kubectl logs -l app=todo-backend --tail=50

# Frontend logs
kubectl logs -l app=todo-frontend --tail=50
```

### Check Service Endpoints

```bash
kubectl get endpoints
```

### Port Forward for Testing (Optional)

If you want to test backend directly:
```bash
kubectl port-forward service/backend-service 8000:8000
```

Then access: http://localhost:8000/docs

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Image Pull Errors

Ensure you built images in Minikube's Docker environment:
```bash
eval $(minikube docker-env)  # Run this before building
docker images | grep todo    # Verify images exist
```

### Backend Can't Connect to Database

Check secrets are correctly set:
```bash
kubectl get secret todo-secrets -o yaml
```

### Frontend Can't Reach Backend

Verify backend service is running:
```bash
kubectl get svc backend-service
kubectl get endpoints backend-service
```

Check frontend environment variable:
```bash
kubectl exec -it <frontend-pod-name> -- env | grep NEXT_PUBLIC_API_URL
```

## Cleanup

To remove all resources:

```bash
kubectl delete -f k8s/frontend-service.yaml
kubectl delete -f k8s/frontend-deployment.yaml
kubectl delete -f k8s/backend-service.yaml
kubectl delete -f k8s/backend-deployment.yaml
kubectl delete secret todo-secrets
```

Or delete everything at once:
```bash
kubectl delete -f k8s/
```

Stop Minikube:
```bash
minikube stop
```

## Docker Compose (Local Testing)

For local testing without Kubernetes:

```bash
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/docs
- Database: localhost:5432

Stop:
```bash
docker-compose down -v
```

## Architecture Overview

```
┌─────────────────────────────────────────┐
│           Minikube Cluster              │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Frontend Service (NodePort)     │  │
│  │  Port: 30080                     │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Frontend Pods (2 replicas)      │  │
│  │  Image: todo-frontend:latest     │  │
│  │  Port: 3000                      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│               │ http://backend-service:8000
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Backend Service (ClusterIP)     │  │
│  │  Port: 8000                      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Backend Pods (2 replicas)       │  │
│  │  Image: todo-backend:latest      │  │
│  │  Port: 8000                      │  │
│  └────────────┬─────────────────────┘  │
│               │                         │
│               │ DATABASE_URL (Secret)   │
│               │ GROQ_API_KEY (Secret)   │
│               │                         │
│  ┌────────────▼─────────────────────┐  │
│  │  Kubernetes Secrets              │  │
│  │  - DATABASE_URL (Neon)           │  │
│  │  - GROQ_API_KEY                  │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
           │
           │ External Connection
           ▼
    Neon PostgreSQL
    (Cloud Database)
```

## Key Configuration Points

1. **Frontend → Backend Communication**: Uses `http://backend-service:8000` (ClusterIP service name)
2. **Backend → Database**: Uses Neon PostgreSQL connection string from secrets
3. **External Access**: Frontend exposed via NodePort on port 30080
4. **Secrets Management**: DATABASE_URL and GROQ_API_KEY stored in Kubernetes secrets
5. **Image Strategy**: Built locally and loaded into Minikube (imagePullPolicy: Never)

## Next Steps

- Set up Ingress for production-grade routing
- Configure Horizontal Pod Autoscaler (HPA)
- Add persistent volumes for logs
- Implement CI/CD pipeline
- Configure monitoring with Prometheus/Grafana
