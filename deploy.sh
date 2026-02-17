#!/bin/bash
# deploy.sh - Automated deployment script for Todo application to Minikube

set -e

echo "=========================================="
echo "Todo Application - Kubernetes Deployment"
echo "=========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${NC}→ $1${NC}"
}

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo ""

# Check if Minikube is installed
if ! command -v minikube &> /dev/null; then
    print_error "Minikube is not installed or not in PATH"
    echo "Please install Minikube: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi
print_success "Minikube is installed"

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed or not in PATH"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
print_success "kubectl is installed"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi
print_success "Docker is installed"

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    print_warning "Minikube is not running"
    print_info "Starting Minikube..."
    minikube start --driver=docker
    print_success "Minikube started"
else
    print_success "Minikube is running"
fi

echo ""

# Step 2: Configure Docker environment
echo "Step 2: Configuring Docker environment..."
echo ""

print_info "Setting Docker to use Minikube's daemon"
eval $(minikube docker-env)
print_success "Docker environment configured"

echo ""

# Step 3: Build Docker images
echo "Step 3: Building Docker images..."
echo ""

print_info "Building backend image..."
docker build -t todo-backend:latest ./backend
print_success "Backend image built: todo-backend:latest"

echo ""

print_info "Building frontend image..."
docker build -t todo-frontend:latest \
    --build-arg VITE_API_URL=http://backend-service:8000/api/v1 \
    ./frontend
print_success "Frontend image built: todo-frontend:latest"

echo ""

# Verify images
print_info "Verifying images..."
docker images | grep todo
echo ""

# Step 4: Create or verify secrets
echo "Step 4: Managing Kubernetes secrets..."
echo ""

if kubectl get secret todo-secrets &> /dev/null; then
    print_success "Secret 'todo-secrets' already exists"
else
    print_warning "Secret 'todo-secrets' does not exist"
    print_info "Running secret creation script..."
    bash ./k8s/create-secrets.sh
fi

echo ""

# Step 5: Deploy to Kubernetes
echo "Step 5: Deploying to Kubernetes..."
echo ""

print_info "Applying backend deployment..."
kubectl apply -f k8s/backend-deployment.yaml
print_success "Backend deployment applied"

print_info "Applying backend service..."
kubectl apply -f k8s/backend-service.yaml
print_success "Backend service applied"

print_info "Applying frontend deployment..."
kubectl apply -f k8s/frontend-deployment.yaml
print_success "Frontend deployment applied"

print_info "Applying frontend service..."
kubectl apply -f k8s/frontend-service.yaml
print_success "Frontend service applied"

echo ""

# Step 6: Wait for deployments to be ready
echo "Step 6: Waiting for deployments to be ready..."
echo ""

print_info "Waiting for backend deployment..."
kubectl rollout status deployment/backend-deployment --timeout=120s
print_success "Backend deployment ready"

print_info "Waiting for frontend deployment..."
kubectl rollout status deployment/frontend-deployment --timeout=120s
print_success "Frontend deployment ready"

echo ""

# Step 7: Verify deployment
echo "Step 7: Verifying deployment..."
echo ""

print_info "Checking pods..."
kubectl get pods -l app=todo-backend
kubectl get pods -l app=todo-frontend
echo ""

print_info "Checking services..."
kubectl get svc backend-service
kubectl get svc frontend-service
echo ""

# Step 8: Get access URL
echo "Step 8: Getting access information..."
echo ""

MINIKUBE_IP=$(minikube ip)
print_success "Minikube IP: $MINIKUBE_IP"

FRONTEND_URL="http://$MINIKUBE_IP:30080"
print_success "Frontend URL: $FRONTEND_URL"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Access the application at: $FRONTEND_URL"
echo ""
echo "Useful commands:"
echo "  - View all resources:    kubectl get all"
echo "  - View backend logs:     kubectl logs -l app=todo-backend --tail=50 -f"
echo "  - View frontend logs:    kubectl logs -l app=todo-frontend --tail=50 -f"
echo "  - Scale backend:         kubectl scale deployment backend-deployment --replicas=3"
echo "  - Open in browser:       minikube service frontend-service"
echo ""
echo "To clean up:"
echo "  kubectl delete -f k8s/"
echo "  kubectl delete secret todo-secrets"
echo ""
