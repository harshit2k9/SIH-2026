# SecureDocs SIH-2026 Makefile
# Simplified deployment and management commands

.PHONY: help build up down logs restart clean deploy health backup restore

# Default command
help:
@echo "SecureDocs SIH-2026 - Available Commands"
@echo "========================================="
@echo ""
@echo "Deployment:"
@echo "  make deploy     - Deploy all services (build + start)"
@echo "  make build      - Build all Docker images"
@echo "  make up         - Start all services"
@echo "  make down       - Stop all services"
@echo "  make restart    - Restart all services"
@echo ""
@echo "Monitoring:"
@echo "  make logs       - View all logs (follow mode)"
@echo "  make logs-backend  - View backend logs"
@echo "  make logs-frontend - View frontend logs"
@echo "  make logs-db    - View database logs"
@echo "  make health     - Check service health"
@echo "  make status     - Show container status"
@echo ""
@echo "Maintenance:"
@echo "  make backup     - Create database backup"
@echo "  make clean      - Remove containers and volumes"
@echo "  make reset      - Full reset (clean + rebuild)"
@echo ""
@echo "Development:"
@echo "  make dev        - Start in development mode"
@echo "  make shell-backend - Open backend shell"
@echo "  make shell-db   - Open database shell"
@echo ""

# Deployment commands
deploy: build up health

build:
@echo "Building Docker images..."
docker compose build

up:
@echo "Starting services..."
docker compose up -d

down:
@echo "Stopping services..."
docker compose down

restart:
@echo "Restarting services..."
docker compose restart

# Monitoring commands
logs:
docker compose logs -f

logs-backend:
docker compose logs -f backend

logs-frontend:
docker compose logs -f frontend

logs-db:
docker compose logs -f postgres

logs-minio:
docker compose logs -f minio

health:
@echo "Checking service health..."
@echo ""
@echo "PostgreSQL:"
@docker compose exec -T postgres pg_isready -U sddms_user -d sddms_db || echo "  Not ready"
@echo ""
@echo "MinIO:"
@curl -s http://localhost:9000/minio/health/live > /dev/null && echo "  Healthy" || echo "  Not ready"
@echo ""
@echo "Backend API:"
@curl -s http://localhost:8000/health > /dev/null && echo "  Healthy" || echo "  Not ready"
@echo ""

status:
docker compose ps

# Maintenance commands
backup:
@echo "Creating database backup..."
@mkdir -p backups
@docker compose exec -T postgres pg_dump -U sddms_user sddms_db > backups/db_backup_$$(date +%Y%m%d_%H%M%S).sql
@echo "Backup created in backups/ directory"

clean:
@echo "Removing containers and volumes..."
docker compose down -v

reset: clean build up health

# Development commands
dev:
@echo "Starting development environment..."
docker compose up -d postgres minio
@echo "Waiting for dependencies..."
@sleep 5
docker compose up -d backend frontend

shell-backend:
docker compose exec backend /bin/bash

shell-db:
docker compose exec postgres psql -U sddms_user -d sddms_db

shell-minio:
docker compose exec minio /bin/bash

# Quick test commands
test-api:
@echo "Testing API endpoints..."
@echo ""
@echo "Health check:"
@curl -s http://localhost:8000/health | head -20
@echo ""
@echo ""
@echo "API Documentation:"
@echo "Visit: http://localhost:8000/docs"

# Install/uninstall aliases
install: deploy
uninstall: clean

# Default target
all: help
