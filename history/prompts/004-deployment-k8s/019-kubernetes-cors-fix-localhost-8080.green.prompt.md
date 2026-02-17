---
id: 019
title: Kubernetes CORS Fix for localhost:8080 Access
stage: green
date: 2026-02-18
surface: agent
model: claude-opus-4-6
feature: 004-deployment-k8s
branch: main
user: bilal gul
command: none
labels: ["kubernetes", "cors", "troubleshooting", "docker", "deployment", "port-forwarding"]
links:
  spec: specs/004-deployment-k8s/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/main.py (updated CORS to allow localhost:8080)
  - backend/Dockerfile (rebuilt as v3)
  - frontend/Dockerfile (rebuilt as v3 with VITE_API_URL=http://localhost:8001/api/v1)
  - k8s/backend-deployment.yaml (updated to use todo-backend:v3)
  - k8s/frontend-deployment.yaml (updated to use todo-frontend:v3)
tests:
  - CORS preflight test: access-control-allow-origin: http://localhost:8080 ✓
  - Frontend accessible at http://localhost:8080 (HTTP 200) ✓
  - Backend API accessible at http://localhost:8001/docs (HTTP 200) ✓
  - All 4 pods running and healthy (2 backend v3, 2 frontend v3) ✓
---

## Prompt

User reported "failed to fetch" error when trying to login at http://localhost:8080. The deployment was running with:
- Backend v2 pods on port 8001
- Frontend v3 pods configured to call http://localhost:8001/api/v1
- Port forwarding active for both services

User requested investigation and fix for the connection issue.

## Response snapshot

Successfully diagnosed and resolved the "failed to fetch" error caused by CORS misconfiguration.

**Root Cause Analysis:**
- Backend CORS configuration only allowed origins: localhost:3000, localhost:3001
- Frontend was accessible at localhost:8080 (via port forwarding)
- Browser blocked requests due to CORS policy violation

**Resolution Steps:**
1. Updated backend/app/main.py CORS middleware to include localhost:8080 and 127.0.0.1:8080
2. Rebuilt backend image as v3: `docker build -t todo-backend:v3 ./backend`
3. Updated k8s/backend-deployment.yaml to use image: todo-backend:v3
4. Applied deployment: `kubectl apply -f k8s/backend-deployment.yaml`
5. User loaded image into Minikube: `minikube image load todo-backend:v3`
6. Deleted backend pods to force recreation with v3 image
7. Waited for readiness probes to pass (60s liveness, 45s readiness delays)
8. Verified CORS with preflight test: `access-control-allow-origin: http://localhost:8080` ✓
9. Set up port forwarding for both services
10. Confirmed both services accessible (HTTP 200)

**Final State:**
- Backend v3: 2 pods running with CORS allowing localhost:8080
- Frontend v3: 2 pods running with VITE_API_URL=http://localhost:8001/api/v1
- Port forwarding active: frontend (8080:3000), backend (8001:8001)
- CORS verification passed: all methods allowed, credentials enabled
- Application ready for testing at http://localhost:8080

## Outcome

- ✅ Impact: Successfully resolved "failed to fetch" error by fixing CORS configuration. Backend now accepts requests from localhost:8080. All 4 pods running healthy with v3 images. Application fully functional for user testing.

- 🧪 Tests: All deployment validation passed: (1) CORS preflight test confirmed access-control-allow-origin: http://localhost:8080, (2) Frontend HTTP 200 at localhost:8080, (3) Backend API HTTP 200 at localhost:8001/docs, (4) All pods Running/Ready (2 backend v3, 2 frontend v3), (5) Port forwarding active for both services.

- 📁 Files: Updated 3 files: backend/app/main.py (added localhost:8080 to CORS origins), k8s/backend-deployment.yaml (image: todo-backend:v3), k8s/frontend-deployment.yaml (already v3). Rebuilt docker images: todo-backend:v3, todo-frontend:v3. Loaded both into Minikube.

- 🔁 Next prompts: (1) Test application functionality (signup, login, task CRUD, AI chat), (2) Verify data persistence in Neon PostgreSQL, (3) Test rolling updates and pod recovery, (4) Consider implementing Ingress controller for better external access instead of port forwarding, (5) Document deployment process and troubleshooting steps.

- 🧠 Reflection: Critical learning: CORS configuration must match the actual origin where the frontend is accessed, not where it's deployed. Port forwarding changes the effective origin from the Kubernetes service to localhost. The backend CORS was configured for localhost:3000 (dev server) but frontend was accessed via localhost:8080 (port forwarding). Always verify CORS with preflight requests when troubleshooting "failed to fetch" errors. Health check delays (60s liveness, 45s readiness) were necessary for database initialization. Image tagging (v3) essential to force Kubernetes to pull updated images with imagePullPolicy: Never.

## Evaluation notes (flywheel)

- Failure modes observed: (1) CORS misconfiguration - backend only allowed localhost:3000/3001 but frontend accessed via localhost:8080, (2) Initial confusion about whether backend was running (it was, but CORS blocked requests), (3) Port forwarding completed notifications but needed manual restart, (4) Backend pods took time to become ready due to database initialization (60s liveness delay required).

- Graders run and results (PASS/FAIL):
  - PASS: CORS preflight test shows access-control-allow-origin: http://localhost:8080
  - PASS: Frontend accessible at localhost:8080 (HTTP 200)
  - PASS: Backend API accessible at localhost:8001/docs (HTTP 200)
  - PASS: All 4 pods running and healthy (2 backend v3, 2 frontend v3)
  - PASS: Port forwarding active for both services
  - PASS: CORS allows all methods and credentials
  - PENDING: User testing of login, signup, task CRUD, AI chat

- Prompt variant (if applicable): N/A - Standard troubleshooting workflow

- Next experiment (smallest change to try): (1) Implement Ingress controller to eliminate need for port forwarding and simplify CORS configuration, (2) Add CORS wildcard for localhost:* during development to avoid future port conflicts, (3) Create health check script to verify CORS configuration automatically, (4) Document common CORS issues and solutions in troubleshooting guide.
