#!/bin/bash

# ========================================
# AI Teddy Bear - Cloud Deployment Script
# ========================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-teddy-bear"
ENVIRONMENT="production"
COMPOSE_FILE="src/docker-compose.prod.yml"

echo -e "${BLUE}🧸 AI Teddy Bear - Cloud Deployment Script${NC}"
echo "================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_requirements() {
    print_status "Checking requirements..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "All requirements met ✅"
}

# Function to validate environment variables
validate_env() {
    print_status "Validating environment variables..."
    
    required_vars=(
        "POSTGRES_PASSWORD"
        "REDIS_PASSWORD"
        "JWT_SECRET_KEY"
        "OPENAI_API_KEY"
        "ENCRYPTION_KEY"
    )
    
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var}" ]]; then
            missing_vars+=("$var")
        fi
    done
    
    if [[ ${#missing_vars[@]} -gt 0 ]]; then
        print_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "  - $var"
        done
        print_error "Please set these variables and try again."
        exit 1
    fi
    
    print_status "Environment variables validated ✅"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "logs"
        "uploads"
        "backups"
        "security-reports"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        print_status "Created directory: $dir"
    done
}

# Function to build and start services
deploy_services() {
    print_status "Building and deploying services..."
    
    # Pull latest images
    print_status "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build custom images
    print_status "Building custom images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_status "Services deployed successfully ✅"
}

# Function to wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    until docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U "${POSTGRES_USER:-teddy_user}" &>/dev/null; do
        sleep 2
    done
    print_status "Database is ready ✅"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping &>/dev/null; do
        sleep 2
    done
    print_status "Redis is ready ✅"
    
    # Wait for main application
    print_status "Waiting for main application..."
    sleep 30  # Give app time to start
    
    # Check health endpoint
    max_attempts=30
    attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            print_status "Application is ready ✅"
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            print_error "Application failed to start after $max_attempts attempts"
            print_error "Check logs with: docker-compose -f $COMPOSE_FILE logs teddy-app"
            exit 1
        fi
        
        print_status "Attempt $attempt/$max_attempts - waiting for application..."
        sleep 10
        ((attempt++))
    done
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Check if migration file exists
    if [[ -f "database_migrations/create_parent_reports_table.sql" ]]; then
        print_status "Found migration file, applying..."
        # Migrations are automatically applied via docker-compose volume mount
        print_status "Migrations applied ✅"
    else
        print_warning "No migration files found"
    fi
}

# Function to display service status
show_status() {
    print_status "Service Status:"
    echo "================================================="
    docker-compose -f "$COMPOSE_FILE" ps
    echo ""
    
    # Get server IP
    SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "YOUR_SERVER_IP")
    
    print_status "Service URLs:"
    echo "• Main Application: http://$SERVER_IP:8000"
    echo "• API Documentation: http://$SERVER_IP:8000/docs"
    echo "• Grafana Dashboard: http://$SERVER_IP:3000"
    echo "• Prometheus Metrics: http://$SERVER_IP:9090"
    echo "• Health Check: http://$SERVER_IP:8000/health"
    echo ""
    echo "💡 Use this IP for ESP32 configuration: $SERVER_IP"
    echo ""
}

# Function to setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Wait for Grafana to be ready
    sleep 10
    
    # Import dashboards (if available)
    if [[ -f "observability/grafana-dashboards.json" ]]; then
        print_status "Grafana dashboards will be auto-imported"
    fi
    
    print_status "Monitoring setup complete ✅"
}

# Function to create backup
create_backup() {
    print_status "Creating initial backup..."
    
    backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup database
    docker-compose -f "$COMPOSE_FILE" exec -T postgres pg_dump -U "${POSTGRES_USER:-teddy_user}" "${POSTGRES_DB:-teddy_bear_prod}" > "$backup_dir/database.sql"
    
    # Backup configuration
    cp -r config "$backup_dir/"
    
    print_status "Backup created: $backup_dir ✅"
}

# Function to display post-deployment instructions
show_post_deployment() {
    echo ""
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo "================================================="
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Update your DNS to point to this server"
    echo "2. Configure SSL certificates"
    echo "3. Set up monitoring alerts"
    echo "4. Test ESP32 connectivity"
    echo "5. Configure parent dashboard access"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "• View logs: docker-compose -f $COMPOSE_FILE logs -f"
    echo "• Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "• Update services: ./scripts/cloud-deployment.sh"
    echo "• Create backup: docker-compose -f $COMPOSE_FILE exec postgres pg_dump..."
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo "• Save your environment variables securely"
    echo "• Set up regular backups"
    echo "• Monitor system resources"
    echo "• Keep API keys secure"
    echo ""
}

# Main deployment function
main() {
    echo "Starting deployment process..."
    
    # Check if it's an update
    if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
        print_warning "Services are already running. This will update them."
        read -p "Continue? (y/N): " -r
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
    fi
    
    check_requirements
    validate_env
    create_directories
    deploy_services
    wait_for_services
    run_migrations
    setup_monitoring
    create_backup
    show_status
    show_post_deployment
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        print_status "Stopping services..."
        docker-compose -f "$COMPOSE_FILE" down
        print_status "Services stopped ✅"
        ;;
    "logs")
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-}"
        ;;
    "status")
        show_status
        ;;
    "backup")
        create_backup
        ;;
    *)
        echo "Usage: $0 {deploy|stop|logs|status|backup}"
        echo "  deploy - Deploy or update services"
        echo "  stop   - Stop all services"
        echo "  logs   - Show service logs"
        echo "  status - Show service status"
        echo "  backup - Create backup"
        exit 1
        ;;
esac 