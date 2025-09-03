# 🐳 Docker Troubleshooting Guide for Portfolia

## 🚨 Common Issues & Solutions

### 1. Volume Mount File Synchronization Issues

**Problem**: Docker container shows old version of files (e.g., `main.py` has 25 lines instead of 78)

**Symptoms**:
- Health endpoints return 404
- File changes not reflected in container
- Container shows different file content than local

**Root Causes**:
- macOS Docker Desktop file sync limitations
- Volume mount conflicts
- Docker layer caching issues
- File permission problems

**Solutions**:

#### Option A: Use Docker Development Script (Recommended)
```bash
# Test file synchronization
./docker-dev.sh test-sync

# If sync fails, attempt automatic fix
./docker-dev.sh fix-sync

# Rebuild container completely
./docker-dev.sh rebuild
```

#### Option B: Manual Volume Mount Fix
```bash
# Stop services
docker-compose down

# Remove problematic containers
docker-compose rm -f api

# Rebuild without cache
docker-compose build --no-cache api

# Start services
docker-compose up -d
```

#### Option C: Temporary Volume Mount Removal
```bash
# Edit docker-compose.yml and comment out volume mount
# volumes:
#   - ./python/api:/app:delegated

# Restart services
docker-compose restart api
```

### 2. Container Health Check Failures

**Problem**: Services fail health checks or don't start properly

**Solutions**:
```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs api
docker-compose logs db
docker-compose logs redis

# Check individual service health
docker-compose exec db pg_isready -U username -d portfolio
docker-compose exec redis redis-cli ping
```

### 3. Port Conflicts

**Problem**: Port already in use errors

**Solutions**:
```bash
# Check what's using the port
lsof -i :8080
lsof -i :5432
lsof -i :6379

# Kill conflicting processes
kill -9 <PID>

# Or use different ports in docker.env
API_PORT=8081
POSTGRES_PORT=5433
REDIS_PORT=6380
```

### 4. Permission Issues

**Problem**: Container can't read/write files

**Solutions**:
```bash
# Fix file permissions
chmod 755 python/api/
chmod 644 python/api/*.py

# Check file ownership
ls -la python/api/

# Fix ownership if needed
sudo chown -R $USER:$USER python/api/
```

## 🔧 Docker Development Script Usage

### Available Commands

```bash
# Start all services
./docker-dev.sh start

# Stop all services
./docker-dev.sh stop

# Restart services
./docker-dev.sh restart

# Rebuild API container
./docker-dev.sh rebuild

# Clean up Docker resources
./docker-dev.sh cleanup

# Check API health
./docker-dev.sh health

# View logs
./docker-dev.sh logs

# Enter container shell
./docker-dev.sh shell

# Test file synchronization
./docker-dev.sh test-sync

# Attempt automatic fix for sync issues
./docker-dev.sh fix-sync

# Show help
./docker-dev.sh help
```

### Quick Troubleshooting Workflow

```bash
# 1. Check if Docker is running
docker info

# 2. Test file synchronization
./docker-dev.sh test-sync

# 3. If sync fails, try automatic fix
./docker-dev.sh fix-sync

# 4. If still failing, rebuild container
./docker-dev.sh rebuild

# 5. Check API health
./docker-dev.sh health

# 6. View logs if issues persist
./docker-dev.sh logs
```

## 🏗️ Docker Architecture Improvements

### Multi-Stage Builds

The updated Dockerfile now supports:
- **Development stage**: With auto-reload and debugging
- **Production stage**: Optimized for deployment
- **Better caching**: Dependencies installed first
- **Security**: Non-root user execution

### Health Checks

All services now include health checks:
- **API**: HTTP health endpoint verification
- **Database**: PostgreSQL connection test
- **Redis**: Ping command verification

### Network Configuration

- **Custom network**: `portfolio_network` with fixed subnet
- **Service discovery**: Containers can communicate by service name
- **Port isolation**: Better security and organization

## 📋 Troubleshooting Checklist

### Before Starting Services
- [ ] Docker Desktop is running
- [ ] No conflicting processes on required ports
- [ ] Environment files are properly configured
- [ ] Source code is up to date

### When Services Won't Start
- [ ] Check Docker logs: `docker-compose logs`
- [ ] Verify environment variables: `docker-compose config`
- [ ] Check service dependencies: `docker-compose ps`
- [ ] Verify network connectivity: `docker network ls`

### When API Endpoints Don't Work
- [ ] Test file synchronization: `./docker-dev.sh test-sync`
- [ ] Check container file content: `docker-compose exec api cat main.py`
- [ ] Verify health checks: `./docker-dev.sh health`
- [ ] Check API logs: `./docker-dev.sh logs`

### When File Changes Don't Sync
- [ ] Verify volume mount in docker-compose.yml
- [ ] Check file permissions and ownership
- [ ] Try rebuilding container: `./docker-dev.sh rebuild`
- [ ] Consider removing volume mount temporarily

## 🚀 Performance Optimization

### Docker Settings for macOS

Add to `~/.docker/daemon.json`:
```json
{
  "experimental": true,
  "features": {
    "buildkit": true
  },
  "max-concurrent-downloads": 10,
  "max-concurrent-uploads": 5
}
```

### Environment Variables

Set in your shell profile:
```bash
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export DOCKER_SCHEMA_VERSION=1.40
```

### Volume Mount Optimization

For development, use `:delegated` flag:
```yaml
volumes:
  - ./python/api:/app:delegated
```

For production, use named volumes:
```yaml
volumes:
  - app_code:/app
```

## 🔍 Debugging Commands

### Container Inspection
```bash
# Inspect container configuration
docker inspect portfolio-api-1

# Check container file system
docker-compose exec api ls -la /app

# Compare file content
diff <(cat python/api/main.py) <(docker-compose exec -T api cat main.py)

# Check container environment
docker-compose exec api env
```

### Network Debugging
```bash
# Check network configuration
docker network inspect portfolio_portfolio_network

# Test inter-container communication
docker-compose exec api ping db
docker-compose exec api ping redis

# Check port bindings
docker port portfolio-api-1
```

### Resource Monitoring
```bash
# Monitor container resources
docker stats

# Check disk usage
docker system df

# Monitor logs in real-time
docker-compose logs -f --tail=100
```

## 📚 Additional Resources

- [Docker Desktop for Mac Troubleshooting](https://docs.docker.com/desktop/mac/troubleshoot/)
- [Docker Compose File Reference](https://docs.docker.com/compose/compose-file/)
- [Docker Volume Mount Best Practices](https://docs.docker.com/storage/volumes/)
- [Docker Health Checks](https://docs.docker.com/engine/reference/builder/#healthcheck)

## 🆘 Getting Help

If you're still experiencing issues:

1. **Check the logs**: `./docker-dev.sh logs`
2. **Run diagnostics**: `./docker-dev.sh test-sync`
3. **Check system resources**: `docker system df`
4. **Verify configuration**: `docker-compose config`
5. **Check Docker Desktop status**: Ensure it's running and healthy

---

**Last Updated**: August 26, 2024  
**Docker Version**: Tested with Docker Desktop 4.x  
**OS**: macOS (Primary), Linux (Compatible)
