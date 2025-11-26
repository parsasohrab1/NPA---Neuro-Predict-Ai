#!/bin/bash

###############################################################################
# Kubernetes Deployment Script for NeuroPredict AI
# Version: 1.0.0
# Description: Automated deployment to Kubernetes cluster
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="${NAMESPACE:-neuropredict}"
MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-neuropredict-monitoring}"
ENVIRONMENT="${ENVIRONMENT:-production}"
DRY_RUN="${DRY_RUN:-false}"

# Logging functions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Banner
echo "═══════════════════════════════════════════════════════════════"
echo "  NeuroPredict AI - Kubernetes Deployment"
echo "  Environment: $ENVIRONMENT"
echo "  Namespace: $NAMESPACE"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        error "kubectl not found. Please install kubectl."
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        error "Cannot connect to Kubernetes cluster."
        exit 1
    fi
    
    # Check helm (optional but recommended)
    if ! command -v helm &> /dev/null; then
        warning "helm not found. Some features may not be available."
    fi
    
    log "Prerequisites check passed ✓"
}

# Create namespaces
create_namespaces() {
    log "Creating namespaces..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f namespace.yaml --dry-run=client
    else
        kubectl apply -f namespace.yaml
    fi
    
    log "Namespaces created ✓"
}

# Create secrets
create_secrets() {
    log "Creating secrets..."
    
    # Check if secrets already exist
    if kubectl get secret neuropredict-secrets -n $NAMESPACE &> /dev/null; then
        warning "Secrets already exist. Skipping creation."
        read -p "Do you want to update secrets? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    # Option 1: From environment variables
    if [ -f ".env.production" ]; then
        log "Loading secrets from .env.production..."
        source .env.production
        
        if [ "$DRY_RUN" = "false" ]; then
            kubectl create secret generic neuropredict-secrets \
                --from-literal=DATABASE_URL="$DATABASE_URL" \
                --from-literal=DATABASE_URL_SYNC="$DATABASE_URL_SYNC" \
                --from-literal=POSTGRES_USER="$POSTGRES_USER" \
                --from-literal=POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
                --from-literal=SECRET_KEY="$SECRET_KEY" \
                --from-literal=JWT_SECRET_KEY="$JWT_SECRET_KEY" \
                --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
                --namespace=$NAMESPACE \
                --dry-run=client -o yaml | kubectl apply -f -
        else
            info "DRY RUN: Would create secrets from .env.production"
        fi
    else
        warning "No .env.production file found."
        info "Please create secrets manually or use secrets-template.yaml"
        info "kubectl create secret generic neuropredict-secrets --from-file=... -n $NAMESPACE"
    fi
    
    log "Secrets configuration complete ✓"
}

# Create ConfigMaps
create_configmaps() {
    log "Creating ConfigMaps..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f configmaps.yaml --dry-run=client
    else
        kubectl apply -f configmaps.yaml
    fi
    
    log "ConfigMaps created ✓"
}

# Deploy persistent volumes
deploy_storage() {
    log "Deploying storage resources..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f persistentvolumes.yaml --dry-run=client
    else
        kubectl apply -f persistentvolumes.yaml
    fi
    
    log "Storage resources deployed ✓"
}

# Deploy database
deploy_database() {
    log "Deploying PostgreSQL database..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f postgres-statefulset.yaml --dry-run=client
    else
        kubectl apply -f postgres-statefulset.yaml
        
        # Wait for database to be ready
        info "Waiting for database to be ready..."
        kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
    fi
    
    log "Database deployed ✓"
}

# Deploy Redis
deploy_redis() {
    log "Deploying Redis cache..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f redis-deployment.yaml --dry-run=client
    else
        kubectl apply -f redis-deployment.yaml
        
        # Wait for Redis to be ready
        info "Waiting for Redis to be ready..."
        kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s
    fi
    
    log "Redis deployed ✓"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    if [ "$DRY_RUN" = "true" ]; then
        info "DRY RUN: Would run database migrations"
        return
    fi
    
    # Create a job to run migrations
    cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration-$(date +%s)
  namespace: $NAMESPACE
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: neuropredict/backend:latest
        command: ["alembic", "upgrade", "head"]
        envFrom:
          - configMapRef:
              name: neuropredict-backend-config
          - secretRef:
              name: neuropredict-secrets
      restartPolicy: OnFailure
  backoffLimit: 3
EOF
    
    log "Database migrations initiated ✓"
}

# Deploy backend
deploy_backend() {
    log "Deploying backend application..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f backend-deployment.yaml --dry-run=client
    else
        kubectl apply -f backend-deployment.yaml
        
        # Wait for backend to be ready
        info "Waiting for backend to be ready..."
        kubectl wait --for=condition=available deployment/neuropredict-backend -n $NAMESPACE --timeout=300s
    fi
    
    log "Backend deployed ✓"
}

# Deploy frontend
deploy_frontend() {
    log "Deploying frontend applications..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f frontend-deployment.yaml --dry-run=client
    else
        kubectl apply -f frontend-deployment.yaml
        
        # Wait for frontend to be ready
        info "Waiting for frontend to be ready..."
        kubectl wait --for=condition=available deployment/neuropredict-frontend -n $NAMESPACE --timeout=300s
        kubectl wait --for=condition=available deployment/neuropredict-admin -n $NAMESPACE --timeout=300s
    fi
    
    log "Frontend deployed ✓"
}

# Deploy network policies
deploy_network_policies() {
    log "Deploying network policies..."
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f network-policies.yaml --dry-run=client
    else
        kubectl apply -f network-policies.yaml
    fi
    
    log "Network policies deployed ✓"
}

# Deploy ingress
deploy_ingress() {
    log "Deploying ingress resources..."
    
    # Check if nginx-ingress is installed
    if ! kubectl get ingressclass nginx &> /dev/null; then
        warning "NGINX Ingress Controller not found."
        info "Installing NGINX Ingress Controller..."
        
        if [ "$DRY_RUN" = "false" ]; then
            helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
            helm repo update
            helm install ingress-nginx ingress-nginx/ingress-nginx \
                --create-namespace \
                --namespace ingress-nginx
        fi
    fi
    
    if [ "$DRY_RUN" = "true" ]; then
        kubectl apply -f ingress.yaml --dry-run=client
    else
        kubectl apply -f ingress.yaml
    fi
    
    log "Ingress deployed ✓"
}

# Deploy monitoring stack
deploy_monitoring() {
    log "Deploying monitoring stack..."
    
    if [ ! -d "../../monitoring" ]; then
        warning "Monitoring configuration not found. Skipping."
        return
    fi
    
    cd ../../monitoring
    
    if [ "$DRY_RUN" = "false" ]; then
        # Deploy using docker-compose equivalent or helm charts
        # For production, you'd typically use Prometheus Operator
        if command -v helm &> /dev/null; then
            # Install Prometheus Stack
            helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
            helm repo update
            
            helm upgrade --install prometheus-stack prometheus-community/kube-prometheus-stack \
                --namespace $MONITORING_NAMESPACE \
                --create-namespace \
                --values prometheus-values.yaml || warning "Prometheus stack installation failed"
        fi
    else
        info "DRY RUN: Would deploy monitoring stack"
    fi
    
    cd - > /dev/null
    log "Monitoring stack deployed ✓"
}

# Verify deployment
verify_deployment() {
    log "Verifying deployment..."
    
    echo ""
    info "=== Pods Status ==="
    kubectl get pods -n $NAMESPACE
    
    echo ""
    info "=== Services Status ==="
    kubectl get svc -n $NAMESPACE
    
    echo ""
    info "=== Ingress Status ==="
    kubectl get ingress -n $NAMESPACE
    
    echo ""
    info "=== PVC Status ==="
    kubectl get pvc -n $NAMESPACE
    
    # Check for any failing pods
    FAILING_PODS=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running,status.phase!=Succeeded -o name 2>/dev/null | wc -l)
    
    if [ "$FAILING_PODS" -gt 0 ]; then
        warning "Found $FAILING_PODS pod(s) not in Running state"
        kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running,status.phase!=Succeeded
    else
        log "All pods are running successfully ✓"
    fi
}

# Show access information
show_access_info() {
    log "Deployment complete!"
    
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Access Information"
    echo "═══════════════════════════════════════════════════════════════"
    
    # Get ingress IP/hostname
    INGRESS_IP=$(kubectl get ingress neuropredict-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
    INGRESS_HOST=$(kubectl get ingress neuropredict-ingress -n $NAMESPACE -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
    
    echo ""
    echo "Ingress IP: $INGRESS_IP"
    if [ -n "$INGRESS_HOST" ]; then
        echo "Ingress Hostname: $INGRESS_HOST"
    fi
    
    echo ""
    echo "Applications:"
    echo "  Frontend:  https://neuropredict.ai"
    echo "  Backend:   https://api.neuropredict.ai"
    echo "  Admin:     https://admin.neuropredict.ai"
    echo "  Grafana:   https://grafana.neuropredict.ai"
    echo ""
    
    echo "Useful commands:"
    echo "  View logs:     kubectl logs -f deployment/neuropredict-backend -n $NAMESPACE"
    echo "  Shell access:  kubectl exec -it deployment/neuropredict-backend -n $NAMESPACE -- /bin/bash"
    echo "  Port forward:  kubectl port-forward svc/backend 8000:8000 -n $NAMESPACE"
    echo "  Scale:         kubectl scale deployment/neuropredict-backend --replicas=5 -n $NAMESPACE"
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
}

# Cleanup function
cleanup() {
    if [ "$1" = "delete" ]; then
        warning "This will delete all resources in namespace: $NAMESPACE"
        read -p "Are you sure? (yes/NO) " -r
        echo
        if [[ $REPLY = "yes" ]]; then
            log "Deleting namespace $NAMESPACE..."
            kubectl delete namespace $NAMESPACE
            log "Cleanup complete"
        else
            info "Cleanup cancelled"
        fi
    fi
}

# Main deployment flow
main() {
    check_prerequisites
    
    if [ "$1" = "cleanup" ] || [ "$1" = "delete" ]; then
        cleanup "delete"
        exit 0
    fi
    
    create_namespaces
    create_secrets
    create_configmaps
    deploy_storage
    deploy_database
    deploy_redis
    run_migrations
    deploy_backend
    deploy_frontend
    deploy_network_policies
    deploy_ingress
    deploy_monitoring
    
    echo ""
    verify_deployment
    show_access_info
}

# Parse command line arguments
case "${1:-deploy}" in
    deploy)
        main
        ;;
    cleanup|delete)
        main cleanup
        ;;
    verify)
        verify_deployment
        ;;
    *)
        echo "Usage: $0 {deploy|cleanup|verify}"
        exit 1
        ;;
esac

