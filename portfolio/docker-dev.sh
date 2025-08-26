#!/bin/bash

# Docker Development Script for Portfolia
# This script handles Docker volume mount issues and provides development tools

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker Desktop first."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to clean up Docker resources
cleanup_docker() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose down --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    print_success "Cleanup completed"
}

# Function to rebuild API container
rebuild_api() {
    print_status "Rebuilding API container..."
    
    # Remove existing API container and image
    docker-compose rm -f api
    docker rmi portfolio-api:latest 2>/dev/null || true
    
    # Build with no cache
    docker-compose build --no-cache api
    
    print_success "API container rebuilt"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start database and Redis first
    docker-compose up -d db redis
    
    # Wait for services to be healthy
    print_status "Waiting for database and Redis to be ready..."
    sleep 10
    
    # Check service health
    if docker-compose ps db | grep -q "healthy"; then
        print_success "Database is healthy"
    else
        print_warning "Database health check failed, but continuing..."
    fi
    
    if docker-compose ps redis | grep -q "healthy"; then
        print_success "Redis is healthy"
    else
        print_warning "Redis health check failed, but continuing..."
    fi
    
    # Start API
    docker-compose up -d api
    
    print_success "All services started"
}

# Function to check API health
check_api_health() {
    print_status "Checking API health..."
    
    # Wait for API to start
    sleep 15
    
    # Try health endpoint
    if curl -f http://localhost:8080/health > /dev/null 2>&1; then
        print_success "API health endpoint is responding"
        return 0
    else
        print_error "API health endpoint is not responding"
        return 1
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing API logs..."
    docker-compose logs -f api
}

# Function to enter container
enter_container() {
    print_status "Entering API container..."
    docker-compose exec api bash
}

# Function to test file sync
test_file_sync() {
    print_status "Testing file synchronization..."
    
    # Check if main.py has the right content
    local_lines=$(wc -l < python/api/main.py)
    container_lines=$(docker-compose exec -T api wc -l < main.py 2>/dev/null || echo "0")
    
    print_status "Local main.py: $local_lines lines"
    print_status "Container main.py: $container_lines lines"
    
    if [ "$local_lines" = "$container_lines" ]; then
        print_success "File synchronization is working"
        return 0
    else
        print_error "File synchronization is NOT working"
        return 1
    fi
}

# Function to fix file sync issues
fix_file_sync() {
    print_status "Attempting to fix file synchronization issues..."
    
    # Stop API container
    docker-compose stop api
    
    # Remove the problematic volume mount temporarily
    print_status "Temporarily removing volume mount..."
    
    # Create a backup of docker-compose.yml
    cp docker-compose.yml docker-compose.yml.backup
    
    # Modify docker-compose.yml to remove volume mount
    sed -i.bak '/- \.\/python\/api:\/app:delegated/d' docker-compose.yml
    
    # Start API without volume mount
    docker-compose up -d api
    
    # Wait for startup
    sleep 10
    
    # Test health endpoint
    if check_api_health; then
        print_success "API working without volume mount"
        print_warning "File changes will require container rebuild"
        
        # Restore original docker-compose.yml
        mv docker-compose.yml.backup docker-compose.yml
        
        return 0
    else
        print_error "API still not working"
        
        # Restore original docker-compose.yml
        mv docker-compose.yml.backup docker-compose.yml
        
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Portfolia Docker Development Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  rebuild     Rebuild API container"
    echo "  cleanup     Clean up Docker resources"
    echo "  health      Check API health"
    echo "  logs        Show API logs"
    echo "  shell       Enter API container"
    echo "  test-sync   Test file synchronization"
    echo "  fix-sync    Attempt to fix file sync issues"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start        # Start all services"
    echo "  $0 health      # Check if API is working"
    echo "  $0 test-sync   # Test if files are syncing"
}

# Main script logic
case "${1:-start}" in
    start)
        check_docker
        start_services
        check_api_health
        ;;
    stop)
        check_docker
        docker-compose down
        print_success "Services stopped"
        ;;
    restart)
        check_docker
        docker-compose restart
        print_success "Services restarted"
        ;;
    rebuild)
        check_docker
        rebuild_api
        start_services
        check_api_health
        ;;
    cleanup)
        check_docker
        cleanup_docker
        ;;
    health)
        check_docker
        check_api_health
        ;;
    logs)
        check_docker
        show_logs
        ;;
    shell)
        check_docker
        enter_container
        ;;
    test-sync)
        check_docker
        test_file_sync
        ;;
    fix-sync)
        check_docker
        fix_file_sync
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
