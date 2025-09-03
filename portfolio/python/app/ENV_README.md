# Environment Configuration

This project uses two environment files for different development scenarios.

## Files

- **`.env`** - For local development (localhost hosts)
- **`.env.docker`** - For Docker development (Docker service names)

## Quick Setup

Run the setup script to generate both files:

```bash
./generate_env_docker.sh
```

## Usage

### Local Development
```bash
# The .env file is automatically loaded
uvicorn app.main:app --reload
```

### Docker Development
```bash
# Explicitly specify the Docker environment file
docker-compose --env-file .env.docker up -d
```

## Key Differences

| Variable | .env (Local) | .env.docker (Docker) |
|----------|--------------|----------------------|
| `POSTGRES_HOST` | `localhost` | `postgres` |
| `REDIS_HOST` | `localhost` | `redis` |
| Other variables | Same values | Same values |

## Customization

1. Edit `.env` for local development settings
2. Edit `.env.docker` for Docker-specific settings
3. Both files should have the same structure and values (except hostnames)

## Security

⚠️ **Important**: Change the default secret keys in both files before production use:
- `SECRET_KEY`
- `JWT_SECRET_KEY`
