# Kubernetes Deployment Troubleshooting Guide

This guide covers common issues you may encounter when deploying the Todo application to Kubernetes (Minikube).

---

## Prerequisites Issues

### Issue: Minikube not found
**Symptoms**: `minikube: command not found`

**Solution**:
1. Install Minikube: https://minikube.sigs.k8s.io/docs/start/
2. Verify installation: `minikube version`
3. Add to PATH if necessary

---

### Issue: kubectl not found
**Symptoms**: `kubectl: command not found`

**Solution**:
1. Install kubectl: https://kubernetes.io/docs/tasks/tools/
2. Verify installation: `kubectl version --client`
3. Add to PATH if necessary

---

### Issue: Docker not running
**Symptoms**: `Cannot connect to the Docker daemon`

**Solution**:
1. Start Docker Desktop (Windows/Mac) or Docker daemon (Linux)
2. Verify: `docker ps`
3. Ensure Docker is running before starting Minikube

---

## Minikube Issues

### Issue: Minikube won't start
**Symptoms**: `minikube start` fails with various errors

**Solutions**:

**For driver issues**:
```bash
# Try different driver
minikube start --driver=docker
# or
minikube start --driver=virtualbox
```

**For resource issues**:
```bash
# Allocate more resources
minikube start --memory=4096 --cpus=2
```

**For existing cluster issues**:
```bash
# Delete and recreate
minikube delete
minikube start --driver=docker
```

---

### Issue: Docker environment not configured
**Symptoms**: Images not found, `ImagePullBackOff` errors

**Solution**:
```bash
# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# Verify
docker images | grep todo

# Rebuild images if needed
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest --build-arg VITE_API_URL=http://backend-service:8000/api/v1 ./frontend
```

**Windows PowerShell**:
```powershell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

---

## Image Build Issues

### Issue: Backend image build fails
**Symptoms**: Docker build errors during backend image creation

**Common Causes & Solutions**:

**Missing dependencies**:
```bash
# Check requirements.txt exists
ls backend/requirements.txt

# Try building with verbose output
docker build -t todo-backend:latest ./backend --progress=plain
```

**Network issues**:
```bash
# Build with no cache
docker build -t todo-backend:latest ./backend --no-cache
```

---

### Issue: Frontend image build fails
**Symptoms**: Docker build errors during frontend image creation

**Common Causes & Solutions**:

**Node modules issues**:
```bash
# Clean node_modules locally first
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..

# Build with no cache
docker build -t todo-frontend:latest --build-arg VITE_API_URL=http://backend-service:8000/api/v1 ./frontend --no-cache
```

**Build argument not passed**:
```bash
# Ensure VITE_API_URL is passed
docker build -t todo-frontend:latest \
  --build-arg VITE_API_URL=http://backend-service:8000/api/v1 \
  ./frontend
```

---

## Pod Issues

### Issue: Pods stuck in ImagePullBackOff
**Symptoms**: `kubectl get pods` shows `ImagePullBackOff` or `ErrImagePull`

**Solution**:
```bash
# 1. Verify Docker environment is configured
eval $(minikube docker-env)

# 2. Check if images exist
docker images | grep todo

# 3. If images don't exist, rebuild them
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest --build-arg VITE_API_URL=http://backend-service:8000/api/v1 ./frontend

# 4. Verify imagePullPolicy is set to Never in deployment YAML
grep imagePullPolicy k8s/*-deployment.yaml

# 5. Restart deployments
kubectl rollout restart deployment/backend-deployment
kubectl rollout restart deployment/frontend-deployment
```

---

### Issue: Pods stuck in CrashLoopBackOff
**Symptoms**: Pods repeatedly restarting

**Diagnosis**:
```bash
# Check pod status
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# View previous crash logs
kubectl logs <pod-name> --previous

# Describe pod for events
kubectl describe pod <pod-name>
```

**Common Causes & Solutions**:

**Backend: Database connection failure**:
```bash
# Check if secret exists
kubectl get secret todo-secrets

# Verify secret has DATABASE_URL
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
echo

# Recreate secret if needed
kubectl delete secret todo-secrets
bash k8s/create-secrets.sh
kubectl rollout restart deployment/backend-deployment
```

**Backend: Missing environment variables**:
```bash
# Check if all required env vars are set
kubectl describe pod <backend-pod-name> | grep -A 10 Environment

# Verify secret keys match deployment
kubectl get secret todo-secrets -o yaml
```

**Frontend: Nginx configuration issues**:
```bash
# Check frontend logs
kubectl logs <frontend-pod-name>

# Exec into pod to debug
kubectl exec -it <frontend-pod-name> -- sh
ls -la /usr/share/nginx/html
cat /etc/nginx/conf.d/default.conf
```

---

### Issue: Pods not ready (failing health checks)
**Symptoms**: Pods in Running state but not Ready (0/1)

**Diagnosis**:
```bash
# Check readiness probe status
kubectl describe pod <pod-name> | grep -A 5 Readiness

# Check if health endpoint is accessible
kubectl exec -it <pod-name> -- curl http://localhost:8000/docs  # backend
kubectl exec -it <pod-name> -- wget -O- http://localhost:3000/health  # frontend
```

**Solutions**:

**Backend health check failing**:
```bash
# Check if FastAPI is running
kubectl logs <backend-pod-name> | grep "Uvicorn running"

# Check if database connection works
kubectl logs <backend-pod-name> | grep -i "database\|error"

# Increase initialDelaySeconds if startup is slow
# Edit k8s/backend-deployment.yaml and increase from 10s to 30s
```

**Frontend health check failing**:
```bash
# Check if nginx is running
kubectl logs <frontend-pod-name>

# Verify health endpoint exists
kubectl exec -it <frontend-pod-name> -- wget -O- http://localhost:3000/health
```

---

## Service Issues

### Issue: Frontend not accessible via NodePort
**Symptoms**: Cannot access application at `http://<minikube-ip>:30080`

**Diagnosis**:
```bash
# Get Minikube IP
minikube ip

# Check if service exists
kubectl get svc frontend-service

# Check service endpoints
kubectl get endpoints frontend-service

# Try accessing via minikube service command
minikube service frontend-service
```

**Solutions**:

**No endpoints**:
```bash
# Pods not ready - check pod status
kubectl get pods -l app=todo-frontend

# Fix pod issues first, then endpoints will appear
```

**Wrong NodePort**:
```bash
# Verify NodePort is 30080
kubectl get svc frontend-service -o yaml | grep nodePort

# If different, update k8s/frontend-service.yaml and reapply
kubectl apply -f k8s/frontend-service.yaml
```

**Firewall blocking**:
```bash
# On Windows, check Windows Firewall
# On Linux, check iptables/firewalld
# On Mac, check System Preferences > Security & Privacy > Firewall
```

---

### Issue: Frontend cannot reach backend
**Symptoms**: Frontend loads but API calls fail, CORS errors

**Diagnosis**:
```bash
# Check if backend service exists
kubectl get svc backend-service

# Check backend endpoints
kubectl get endpoints backend-service

# Test connectivity from frontend pod
kubectl exec -it <frontend-pod-name> -- wget -O- http://backend-service:8000/docs
```

**Solutions**:

**Backend service not found**:
```bash
# Apply backend service
kubectl apply -f k8s/backend-service.yaml

# Verify DNS resolution
kubectl exec -it <frontend-pod-name> -- nslookup backend-service
```

**Wrong API URL in frontend**:
```bash
# Frontend must use http://backend-service:8000/api/v1
# Rebuild frontend with correct build arg
docker build -t todo-frontend:latest \
  --build-arg VITE_API_URL=http://backend-service:8000/api/v1 \
  ./frontend

# Restart frontend deployment
kubectl rollout restart deployment/frontend-deployment
```

**Backend pods not ready**:
```bash
# Check backend pod status
kubectl get pods -l app=todo-backend

# Fix backend issues first
```

---

## Secret Issues

### Issue: Secret not found
**Symptoms**: Pods fail with "secret not found" error

**Solution**:
```bash
# Create secret
bash k8s/create-secrets.sh

# Verify secret exists
kubectl get secret todo-secrets

# Restart deployments to pick up secret
kubectl rollout restart deployment/backend-deployment
```

---

### Issue: Invalid secret values
**Symptoms**: Backend connects but database operations fail

**Solution**:
```bash
# Delete and recreate secret with correct values
kubectl delete secret todo-secrets
bash k8s/create-secrets.sh

# Restart backend
kubectl rollout restart deployment/backend-deployment

# Verify backend logs
kubectl logs -l app=todo-backend --tail=50
```

---

## Deployment Issues

### Issue: Rolling update stuck
**Symptoms**: `kubectl rollout status` hangs or shows old pods not terminating

**Solution**:
```bash
# Check rollout status
kubectl rollout status deployment/backend-deployment

# Check pod events
kubectl get events --sort-by=.metadata.creationTimestamp

# Force restart
kubectl rollout restart deployment/backend-deployment

# If stuck, delete old pods manually
kubectl delete pod <old-pod-name>
```

---

### Issue: Out of resources
**Symptoms**: Pods stuck in Pending state, "Insufficient memory/cpu" errors

**Solution**:
```bash
# Check node resources
kubectl top nodes

# Check pod resource requests
kubectl describe pod <pod-name> | grep -A 5 Requests

# Increase Minikube resources
minikube stop
minikube start --memory=8192 --cpus=4

# Or reduce pod resource requests in deployment YAML
```

---

## Debugging Commands

### View all resources
```bash
kubectl get all
kubectl get all -o wide
```

### View logs
```bash
# Backend logs
kubectl logs -l app=todo-backend --tail=50 -f

# Frontend logs
kubectl logs -l app=todo-frontend --tail=50 -f

# Specific pod
kubectl logs <pod-name> --tail=100 -f

# Previous crash
kubectl logs <pod-name> --previous
```

### Describe resources
```bash
kubectl describe pod <pod-name>
kubectl describe deployment <deployment-name>
kubectl describe service <service-name>
kubectl describe secret todo-secrets
```

### Execute commands in pod
```bash
# Backend
kubectl exec -it <backend-pod-name> -- bash
kubectl exec -it <backend-pod-name> -- python -c "import sys; print(sys.version)"

# Frontend
kubectl exec -it <frontend-pod-name> -- sh
kubectl exec -it <frontend-pod-name> -- ls -la /usr/share/nginx/html
```

### Port forwarding (for debugging)
```bash
# Forward backend port
kubectl port-forward svc/backend-service 8000:8000

# Forward frontend port
kubectl port-forward svc/frontend-service 3000:3000
```

### Check events
```bash
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events --field-selector type=Warning
```

---

## Complete Cleanup

If you need to start fresh:

```bash
# Delete all Kubernetes resources
kubectl delete -f k8s/

# Delete secrets
kubectl delete secret todo-secrets

# Delete Minikube cluster
minikube delete

# Start fresh
minikube start --driver=docker
eval $(minikube docker-env)
bash deploy.sh
```

---

## Getting Help

If you're still stuck:

1. Check pod logs: `kubectl logs <pod-name>`
2. Check pod events: `kubectl describe pod <pod-name>`
3. Check service endpoints: `kubectl get endpoints`
4. Verify images exist: `docker images | grep todo`
5. Verify secrets exist: `kubectl get secret todo-secrets`
6. Check Minikube status: `minikube status`
7. Check Docker environment: `docker info`

For more help, refer to:
- Kubernetes documentation: https://kubernetes.io/docs/
- Minikube documentation: https://minikube.sigs.k8s.io/docs/
- Docker documentation: https://docs.docker.com/
