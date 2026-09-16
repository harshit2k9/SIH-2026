#!/bin/bash

# SecureDocs SIH-2026 Deployment Script
# This script automates the deployment process using Docker Compose

set -e  # Exit on error

echo "=========================================="
echo "SecureDocs SIH-2026 - Deployment Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is available
check_docker() {
    if command -v docker &> /dev/null; then
        echo -e "${GREEN}✓ Docker found${NC}"
        docker --version
    else
        echo -e "${RED}✗ Docker not found. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check for docker compose or docker-compose
    if command -v docker compose &> /dev/null; then
        COMPOSE_CMD="docker compose"
        echo -e "${GREEN}✓ Docker Compose v2 found${NC}"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        echo -e "${GREEN}✓ Docker Compose v1 found${NC}"
    else
        echo -e "${RED}✗ Docker Compose not found. Please install Docker Compose.${NC}"
        exit 1
    fi
    echo ""
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}! .env file not found. Using default configuration.${NC}"
        echo "You may want to create a .env file with your custom settings."
        echo ""
    else
        echo -e "${GREEN}✓ .env file found${NC}"
    fi
}

# Check if JWT keys exist
check_jwt_keys() {
    if [ ! -f backend/keys/private.pem ] || [ ! -f backend/keys/public.pem ]; then
        echo -e "${YELLOW}! JWT keys not found. Generating new keys...${NC}"
        mkdir -p backend/keys
        openssl genrsa -out backend/keys/private.pem 2048 2>/dev/null
        openssl rsa -in backend/keys/private.pem -pubout -out backend/keys/public.pem 2>/dev/null
        chmod 600 backend/keys/private.pem
        chmod 644 backend/keys/public.pem
        echo -e "${GREEN}✓ JWT keys generated${NC}"
    else
        echo -e "${GREEN}✓ JWT keys found${NC}"
    fi
    echo ""
}

# Stop existing containers
stop_containers() {
    echo "Stopping existing containers (if any)..."
    $COMPOSE_CMD down 2>/dev/null || true
    echo -e "${GREEN}✓ Containers stopped${NC}"
    echo ""
}

# Build and start services
deploy_services() {
    echo "Building and starting all services..."
    echo "This may take a few minutes on first run..."
    echo ""
    
    $COMPOSE_CMD up -d --build
    
    echo ""
    echo -e "${GREEN}✓ Services deployed${NC}"
}

# Wait for services to be healthy
wait_for_services() {
    echo ""
    echo "Waiting for services to become healthy..."
    
    # Wait for PostgreSQL
    echo -n "Waiting for PostgreSQL"
    until $COMPOSE_CMD exec -T postgres pg_isready -U sddms_user -d sddms_db > /dev/null 2>&1; do
        echo -n "."
        sleep 2
    done
    echo -e " ${GREEN}✓${NC}"
    
    # Wait for MinIO
    echo -n "Waiting for MinIO"
    until curl -s http://localhost:9000/minio/health/live > /dev/null 2>&1; do
        echo -n "."
        sleep 2
    done
    echo -e " ${GREEN}✓${NC}"
    
    # Wait for Backend
    echo -n "Waiting for Backend API"
    timeout=120
    elapsed=0
    while [ $elapsed -lt $timeout ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            break
        fi
        echo -n "."
        sleep 2
        elapsed=$((elapsed + 2))
    done
    
    if [ $elapsed -ge $timeout ]; then
        echo -e " ${YELLOW}⚠ Backend taking longer than expected. Check logs with: $COMPOSE_CMD logs backend${NC}"
    fi
    
    echo ""
}

# Display status
show_status() {
    echo "=========================================="
    echo "Deployment Complete!"
    echo "=========================================="
    echo ""
    echo "Services Status:"
    $COMPOSE_CMD ps
    echo ""
    echo "Access URLs:"
    echo -e "  Frontend:       ${GREEN}http://localhost:5173${NC}"
    echo -e "  Backend API:    ${GREEN}http://localhost:8000${NC}"
    echo -e "  API Docs:       ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  MinIO Console:  ${GREEN}http://localhost:9001${NC}"
    echo ""
    echo "Default Credentials:"
    echo "  MinIO:"
    echo "    Username: minio_admin"
    echo "    Password: minio_secure_password_2025"
    echo ""
    echo "Next Steps:"
    echo "  1. Visit http://localhost:5173 to access the application"
    echo "  2. Check API documentation at http://localhost:8000/docs"
    echo "  3. View logs: $COMPOSE_CMD logs -f"
    echo "  4. Stop services: $COMPOSE_CMD down"
    echo ""
}

# Main execution
main() {
    check_docker
    check_env
    check_jwt_keys
    stop_containers
    deploy_services
    wait_for_services
    show_status
}

# Run main function
main "$@"
