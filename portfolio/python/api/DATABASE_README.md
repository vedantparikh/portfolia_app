# 🗄️ Portfolia Database Documentation

## Overview

This document describes the database architecture and setup for the Portfolia portfolio management application.

## 🏗️ Database Architecture

### Core Tables

#### 1. **Users & Authentication**
- `users` - User account information
- `user_profiles` - Extended user profile data
- `user_sessions` - User session management

#### 2. **Portfolio Management**
- `portfolios` - User investment portfolios
- `portfolio_assets` - Assets within portfolios
- `transactions` - Investment transactions

#### 3. **Asset Management**
- `assets` - Financial instruments (stocks, bonds, ETFs, etc.)
- `asset_prices` - Historical price data
- `market_indices` - Market benchmark indices

#### 4. **Transaction Tracking**
- `transactions` - Portfolio transactions with full details
- `manual_entries` - Manual transaction entry tracking

## 🔧 Setup Instructions

### Prerequisites

1. **PostgreSQL 16.2+** running on port 5432
2. **Redis** running on port 6379 (optional but recommended)
3. **Python 3.12+** with virtual environment

### Quick Setup

```bash
# 1. Start the database (if using Docker)
docker-compose up -d db

# 2. Run the setup script
./setup_database.sh
```

### Manual Setup

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize database
python database/init_db.py

# 4. Set up Alembic migrations
alembic init alembic
alembic revision --autogenerate -m "Initial database schema"
alembic upgrade head
```

## 📊 Database Schema Details

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);
```

### Portfolios Table
```sql
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    currency VARCHAR(3) DEFAULT 'USD',
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id) ON DELETE CASCADE,
    asset_id INTEGER REFERENCES assets(id) ON DELETE CASCADE,
    transaction_type transaction_type_enum NOT NULL,
    status transaction_status_enum DEFAULT 'completed',
    quantity NUMERIC(20,8) NOT NULL,
    price NUMERIC(20,4) NOT NULL,
    total_amount NUMERIC(20,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    settlement_date TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    reference_number VARCHAR(100),
    fees NUMERIC(20,4) DEFAULT 0,
    taxes NUMERIC(20,4) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🔐 Security Features

### Authentication
- JWT-based authentication with refresh tokens
- Password hashing using bcrypt
- Session management with Redis
- Role-based access control (RBAC)

### Data Protection
- Foreign key constraints with CASCADE deletion
- Input validation and sanitization
- SQL injection prevention via SQLAlchemy ORM
- Encrypted sensitive data storage

## 📈 Performance Optimizations

### Indexes
- Primary keys on all tables
- Foreign key indexes for joins
- Composite indexes for common queries
- Date-based indexes for time-series data

### Connection Pooling
- SQLAlchemy connection pooling
- Configurable pool size and overflow
- Connection recycling and timeout handling

### Caching
- Redis for session storage
- Redis for frequently accessed data
- Query result caching

## 🚀 Migration Management

### Using Alembic

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Check current migration status
alembic current
```

### Migration Best Practices

1. **Always backup** before running migrations
2. **Test migrations** in development first
3. **Use descriptive names** for migration files
4. **Review auto-generated migrations** before applying
5. **Keep migrations small** and focused

## 🔍 Health Monitoring

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8080/health

# Detailed health check with statistics
curl http://localhost:8080/health/detailed
```

### Database Utilities

```python
from database.utils import (
    get_database_stats,
    validate_database_integrity,
    cleanup_expired_sessions,
    calculate_portfolio_value
)

# Get database statistics
stats = get_database_stats(db)

# Validate database integrity
integrity = validate_database_integrity(db)

# Clean up expired sessions
cleaned = cleanup_expired_sessions(db)
```

## 🛠️ Troubleshooting

### Common Issues

#### Connection Errors
```bash
# Check PostgreSQL status
pg_isready -h localhost -p 5432 -U username

# Check Redis status
redis-cli -h localhost -p 6379 ping
```

#### Migration Issues
```bash
# Reset migrations (DANGEROUS - only in development)
alembic downgrade base
alembic upgrade head

# Check migration status
alembic current
alembic history
```

#### Performance Issues
```bash
# Check database statistics
curl http://localhost:8080/health/detailed

# Monitor slow queries
# Enable SQLAlchemy echo in database/connection.py
```

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🤝 Contributing

When making database changes:

1. **Update models** in `database/models/`
2. **Create migration** using Alembic
3. **Update documentation** in this file
4. **Test thoroughly** before committing
5. **Follow naming conventions** consistently

---

**Note**: This database setup is designed for development and testing. For production deployment, additional security measures and performance optimizations should be implemented.
