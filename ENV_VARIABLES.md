# Environment Variables Reference

This file documents all environment variables used in the Todo application.

## Backend Environment Variables

### Required

**DATABASE_URL**
- Description: PostgreSQL connection string for Neon database
- Format: `postgresql://user:password@host.neon.tech/dbname?sslmode=require`
- Example: `postgresql://myuser:mypass@ep-cool-name-123456.us-east-2.aws.neon.tech/mydb?sslmode=require`
- Used in: Backend pods (from Kubernetes Secret)

**OPENAI_API_KEY**
- Description: API key for Groq API (OpenAI-compatible)
- Format: `gsk_...` (Groq API key format)
- Example: `gsk_1234567890abcdefghijklmnopqrstuvwxyz`
- Used in: Backend pods (from Kubernetes Secret)

### Optional

**BETTER_AUTH_SECRET**
- Description: Secret key for Better Auth (if using)
- Format: Random string (32+ characters recommended)
- Example: `your-secret-key-here-make-it-long-and-random`
- Used in: Backend pods (from Kubernetes Secret, optional)

**JWT_SECRET_KEY**
- Description: Secret key for JWT token signing
- Format: Random string (32+ characters recommended)
- Default: Auto-generated if not provided
- Used in: Backend application code

**JWT_ALGORITHM**
- Description: Algorithm for JWT token signing
- Format: String (e.g., "HS256")
- Default: "HS256"
- Used in: Backend application code

## Frontend Environment Variables

### Build-time Variables

**VITE_API_URL**
- Description: Backend API base URL
- Format: `http://host:port/api/v1`
- Local development: `http://localhost:8001/api/v1`
- Kubernetes: `http://backend-service:8000/api/v1`
- Used in: Frontend build process (Docker build arg)

## Kubernetes Deployment

### Creating Secrets

**Interactive (Recommended)**:
```bash
bash k8s/create-secrets.sh
```

**Manual**:
```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require" \
  --from-literal=OPENAI_API_KEY="gsk_..." \
  --from-literal=BETTER_AUTH_SECRET="your-secret-here"
```

**From Environment Variables**:
```bash
export DATABASE_URL="postgresql://user:pass@host.neon.tech/db?sslmode=require"
export OPENAI_API_KEY="gsk_..."
export BETTER_AUTH_SECRET="your-secret-here"

kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET"
```

### Verifying Secrets

```bash
# Check if secret exists
kubectl get secret todo-secrets

# View secret keys (not values)
kubectl describe secret todo-secrets

# View secret values (base64 encoded)
kubectl get secret todo-secrets -o yaml

# Decode specific value
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
echo
```

### Updating Secrets

```bash
# Delete existing secret
kubectl delete secret todo-secrets

# Recreate with new values
bash k8s/create-secrets.sh

# Restart deployments to pick up new values
kubectl rollout restart deployment/backend-deployment
```

## Local Development

### Backend (.env file)

Create `backend/.env`:
```bash
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
OPENAI_API_KEY=gsk_...
JWT_SECRET_KEY=your-jwt-secret-here
JWT_ALGORITHM=HS256
```

### Frontend (.env.local file)

Create `frontend/.env.local`:
```bash
VITE_API_URL=http://localhost:8001/api/v1
```

## Security Best Practices

### ✅ DO
- Store secrets in Kubernetes Secrets (production)
- Use `.env` files for local development (never commit)
- Use strong, random values for secret keys (32+ characters)
- Rotate secrets regularly
- Use SSL/TLS for database connections (`sslmode=require`)
- Limit secret access to necessary pods only

### ❌ DON'T
- Commit `.env` files to git
- Hardcode secrets in code
- Include secrets in Docker images
- Share secrets in plain text (Slack, email, etc.)
- Use weak or predictable secret values
- Log secret values

## Troubleshooting

### Backend can't connect to database
- Verify `DATABASE_URL` is correct
- Check if `sslmode=require` is included
- Test connection from local machine first
- Verify Neon database is accessible

### Backend can't call Groq API
- Verify `OPENAI_API_KEY` is correct
- Check if key starts with `gsk_`
- Verify API key has sufficient credits
- Test API key with curl:
  ```bash
  curl https://api.groq.com/openai/v1/models \
    -H "Authorization: Bearer $OPENAI_API_KEY"
  ```

### Frontend can't reach backend
- Verify `VITE_API_URL` is set correctly
- For Kubernetes: Must be `http://backend-service:8000/api/v1`
- For local dev: Must be `http://localhost:8001/api/v1`
- Rebuild frontend if API URL changed

### Secrets not found in pods
- Verify secret exists: `kubectl get secret todo-secrets`
- Check secret is referenced in deployment YAML
- Restart deployment: `kubectl rollout restart deployment/backend-deployment`
- Check pod logs: `kubectl logs <pod-name>`

---

**Note**: Never commit this file with actual secret values. This is a reference template only.
