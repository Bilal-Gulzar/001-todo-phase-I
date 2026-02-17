#!/bin/bash
# create-secrets.sh - Create Kubernetes secrets for the Todo application

set -e

echo "=========================================="
echo "Creating Kubernetes Secrets"
echo "=========================================="
echo ""

# Check if secrets already exist
if kubectl get secret todo-secrets &> /dev/null; then
    echo "⚠️  Secret 'todo-secrets' already exists."
    read -p "Do you want to delete and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl delete secret todo-secrets
        echo "✓ Deleted existing secret"
    else
        echo "✓ Using existing secret"
        exit 0
    fi
fi

# Prompt for secret values
echo "Please provide the following secret values:"
echo ""

# DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo "DATABASE_URL (PostgreSQL connection string):"
    echo "Example: postgresql://user:password@host.neon.tech/dbname?sslmode=require"
    read -r DATABASE_URL
fi

# OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "OPENAI_API_KEY (Groq API key):"
    echo "Example: gsk_..."
    read -r OPENAI_API_KEY
fi

# BETTER_AUTH_SECRET (optional)
if [ -z "$BETTER_AUTH_SECRET" ]; then
    echo ""
    echo "BETTER_AUTH_SECRET (optional, press Enter to skip):"
    read -r BETTER_AUTH_SECRET
fi

# Validate required secrets
if [ -z "$DATABASE_URL" ] || [ -z "$OPENAI_API_KEY" ]; then
    echo ""
    echo "❌ Error: DATABASE_URL and OPENAI_API_KEY are required"
    exit 1
fi

# Create the secret
echo ""
echo "Creating secret..."

if [ -z "$BETTER_AUTH_SECRET" ]; then
    kubectl create secret generic todo-secrets \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY"
else
    kubectl create secret generic todo-secrets \
        --from-literal=DATABASE_URL="$DATABASE_URL" \
        --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
        --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET"
fi

echo ""
echo "✓ Secret 'todo-secrets' created successfully"
echo ""
echo "To verify: kubectl get secret todo-secrets"
echo "To view (base64 encoded): kubectl get secret todo-secrets -o yaml"
