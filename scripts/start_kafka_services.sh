#!/bin/bash

# 🚀 AI Teddy Bear Kafka Services Startup Script
# ===============================================
# 
# This script starts the complete Kafka infrastructure for the
# AI Teddy Bear event-driven architecture.

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.kafka.yml"
PROJECT_NAME="teddy-kafka"
STARTUP_TIMEOUT=300  # 5 minutes
HEALTH_CHECK_RETRIES=30

echo -e "${CYAN}🚀 AI Teddy Bear Kafka Services Startup${NC}"
echo "================================================"

# Function to check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker is running${NC}"
}

# Function to check if docker-compose file exists
check_compose_file() {
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Docker compose file '$COMPOSE_FILE' not found.${NC}"
        echo "Please ensure you're running from the project root directory."
        exit 1
    fi
    echo -e "${GREEN}✅ Docker compose file found${NC}"
}

# Function to stop existing services
stop_existing_services() {
    echo -e "${YELLOW}🛑 Stopping existing Kafka services...${NC}"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --remove-orphans >/dev/null 2>&1 || true
    echo -e "${GREEN}✅ Existing services stopped${NC}"
}

# Function to start services
start_services() {
    echo -e "${BLUE}🚀 Starting Kafka services...${NC}"
    echo "This may take a few minutes on first run..."
    
    # Pull latest images
    echo -e "${CYAN}📥 Pulling latest Docker images...${NC}"
    docker-compose -f $COMPOSE_FILE pull --quiet
    
    # Start services
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Kafka services started${NC}"
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        exit 1
    fi
}

# Function to wait for service health
wait_for_health() {
    local service=$1
    local port=$2
    local retries=0
    
    echo -e "${YELLOW}⏳ Waiting for $service to be healthy...${NC}"
    
    while [ $retries -lt $HEALTH_CHECK_RETRIES ]; do
        if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps $service | grep -q "healthy"; then
            echo -e "${GREEN}✅ $service is healthy${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 10
        retries=$((retries + 1))
    done
    
    echo -e "\n${RED}❌ $service failed to become healthy within timeout${NC}"
    return 1
}

# Function to verify Kafka connectivity
verify_kafka() {
    echo -e "${CYAN}🔍 Verifying Kafka connectivity...${NC}"
    
    # Check if Kafka is accepting connections
    timeout 30 bash -c 'until echo > /dev/tcp/localhost/9092; do sleep 1; done' 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Kafka broker is accessible on localhost:9092${NC}"
    else
        echo -e "${YELLOW}⚠️  Kafka broker not immediately accessible${NC}"
        echo "This is normal if services are still starting up..."
    fi
}

# Function to list topics
list_topics() {
    echo -e "${CYAN}📋 Listing Kafka topics...${NC}"
    
    # Wait a bit for topic creation to complete
    sleep 5
    
    if docker exec -it teddy-kafka kafka-topics --list --bootstrap-server localhost:9092 2>/dev/null; then
        echo -e "${GREEN}✅ Topics listed successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not list topics yet (services still starting)${NC}"
    fi
}

# Function to show service status
show_status() {
    echo -e "\n${PURPLE}📊 Service Status:${NC}"
    echo "==================="
    
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    
    echo -e "\n${PURPLE}🌐 Service URLs:${NC}"
    echo "================="
    echo -e "Kafka Broker:      ${CYAN}localhost:9092${NC}"
    echo -e "Schema Registry:   ${CYAN}http://localhost:8081${NC}"
    echo -e "Kafka Connect:     ${CYAN}http://localhost:8083${NC}"
    echo -e "Control Center:    ${CYAN}http://localhost:9021${NC}"
    echo -e "Kafka Exporter:    ${CYAN}http://localhost:9308${NC}"
}

# Function to show logs
show_logs() {
    if [ "$1" = "--logs" ]; then
        echo -e "\n${CYAN}📄 Service Logs (last 50 lines each):${NC}"
        echo "====================================="
        
        for service in zookeeper kafka schema-registry; do
            echo -e "\n${YELLOW}--- $service logs ---${NC}"
            docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs --tail=50 $service
        done
    fi
}

# Function to run health checks
run_health_checks() {
    echo -e "\n${CYAN}🏥 Running comprehensive health checks...${NC}"
    echo "========================================="
    
    # Check Zookeeper
    echo -e "${YELLOW}Checking Zookeeper...${NC}"
    if echo ruok | nc localhost 2181 | grep -q imok; then
        echo -e "${GREEN}✅ Zookeeper is OK${NC}"
    else
        echo -e "${RED}❌ Zookeeper health check failed${NC}"
    fi
    
    # Check Schema Registry
    echo -e "${YELLOW}Checking Schema Registry...${NC}"
    if curl -sf http://localhost:8081/subjects >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Schema Registry is OK${NC}"
    else
        echo -e "${RED}❌ Schema Registry health check failed${NC}"
    fi
    
    # Check Kafka Connect
    echo -e "${YELLOW}Checking Kafka Connect...${NC}"
    if curl -sf http://localhost:8083/connectors >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Kafka Connect is OK${NC}"
    else
        echo -e "${RED}❌ Kafka Connect health check failed${NC}"
    fi
}

# Function to create test event
create_test_event() {
    echo -e "\n${CYAN}🧪 Creating test event...${NC}"
    
    cat << EOF | docker exec -i teddy-kafka kafka-console-producer --bootstrap-server localhost:9092 --topic system.health-check
{
    "event_type": "system.health_check",
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)",
    "status": "healthy",
    "message": "Kafka infrastructure is ready for AI Teddy Bear events"
}
EOF

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Test event created successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Could not create test event${NC}"
    fi
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --logs       Show service logs after startup"
    echo "  --test       Create a test event after startup"
    echo "  --stop       Stop all services"
    echo "  --restart    Restart all services"
    echo "  --status     Show service status"
    echo "  --help       Show this help message"
}

# Main execution
main() {
    case "${1:-}" in
        --stop)
            echo -e "${YELLOW}🛑 Stopping all Kafka services...${NC}"
            docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down --remove-orphans
            echo -e "${GREEN}✅ All services stopped${NC}"
            exit 0
            ;;
        --restart)
            echo -e "${YELLOW}🔄 Restarting all Kafka services...${NC}"
            stop_existing_services
            ;;
        --status)
            show_status
            exit 0
            ;;
        --help)
            show_usage
            exit 0
            ;;
    esac
    
    # Run startup sequence
    check_docker
    check_compose_file
    stop_existing_services
    start_services
    
    echo -e "\n${YELLOW}⏳ Waiting for services to become healthy...${NC}"
    echo "This may take up to 5 minutes..."
    
    # Wait for core services
    wait_for_health "zookeeper" "2181"
    wait_for_health "kafka" "9092"
    wait_for_health "schema-registry" "8081"
    
    # Verify connectivity
    verify_kafka
    
    # List topics
    list_topics
    
    # Run health checks
    run_health_checks
    
    # Create test event if requested
    if [ "$1" = "--test" ]; then
        create_test_event
    fi
    
    # Show logs if requested
    show_logs "$1"
    
    # Show final status
    show_status
    
    echo -e "\n${GREEN}🎉 Kafka infrastructure is ready!${NC}"
    echo -e "${CYAN}You can now run: python scripts/kafka_example_usage.py${NC}"
    echo -e "${YELLOW}To stop services: $0 --stop${NC}"
    echo -e "${YELLOW}To view Control Center: http://localhost:9021${NC}"
}

# Handle Ctrl+C
trap 'echo -e "\n${YELLOW}🛑 Script interrupted${NC}"; exit 1' INT

# Run main function
main "$@" 