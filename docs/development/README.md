# Development Guide

## Overview

This guide provides detailed information for developers working on the Smart Teddy Bear application. It covers setup, development workflows, and best practices.

## Development Environment

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Make
- Git
- SQLite3
- Visual Studio Code (recommended)

### IDE Setup

#### Visual Studio Code

1. Install recommended extensions:
   - Python
   - Pylance
   - Docker
   - SQLite Viewer
   - GitLens
   - Python Test Explorer

2. Configure settings:
   ```json
   {
       "python.linting.enabled": true,
       "python.linting.pylintEnabled": true,
       "python.formatting.provider": "black",
       "editor.formatOnSave": true,
       "editor.rulers": [88],
       "python.testing.pytestEnabled": true
   }
   ```

### Local Setup

1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/smart-teddy.git
   cd smart-teddy
   ```

2. Create virtual environment:
   ```bash
   make setup
   # Or manually:
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements-dev.txt
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. Initialize database:
   ```bash
   make db-migrate
   ```

## Project Structure

```
smart-teddy/
├── src/
│   ├── domain/           # Business entities and interfaces
│   ├── application/      # Use cases and services
│   ├── infrastructure/   # External implementations
│   └── interfaces/       # API and UI adapters
├── tests/               # Test suites
├── docs/               # Documentation
├── config/             # Configuration files
└── scripts/            # Development scripts
```

## Development Workflow

### 1. Feature Development

1. Create feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement changes following TDD:
   ```bash
   # 1. Write test
   vim tests/your_test.py
   
   # 2. Run test (should fail)
   make test
   
   # 3. Implement feature
   vim src/your_code.py
   
   # 4. Run test (should pass)
   make test
   ```

3. Format and lint code:
   ```bash
   make format
   make lint
   ```

### 2. Running the Application

#### Development Mode

```bash
# With Docker
make docker-dev

# Without Docker
python src/main.py
```

#### Production Mode

```bash
make docker-prod
```

### 3. Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/path/to/test.py

# Run with coverage
pytest --cov=src

# Run parallel tests
pytest -n auto
```

### 4. Database Operations

```bash
# Create migration
alembic revision -m "your migration name"

# Apply migrations
make db-migrate

# Rollback migration
make db-rollback

# Reset database
make db-reset
```

## Debugging

### VSCode Debugging

1. Create `.vscode/launch.json`:
   ```json
   {
       "version": "0.2.0",
       "configurations": [
           {
               "name": "Python: Main",
               "type": "python",
               "request": "launch",
               "program": "src/main.py",
               "console": "integratedTerminal"
           }
       ]
   }
   ```

2. Set breakpoints and start debugging

### Logging

```python
# In your code
from infrastructure.logging import get_logger

logger = get_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Profiling

```bash
# CPU profiling
make profile-cpu

# Memory profiling
make profile-memory
```

## Common Tasks

### Adding a New Entity

1. Create entity in domain layer:
   ```python
   # src/domain/entities/your_entity.py
   from dataclasses import dataclass
   from uuid import UUID, uuid4
   
   @dataclass
   class YourEntity:
       id: UUID = uuid4()
       # Add fields
   ```

2. Create repository interface:
   ```python
   # src/domain/repositories/your_repository.py
   from abc import ABC, abstractmethod
   from .base import BaseRepository
   from ..entities import YourEntity
   
   class YourRepository(BaseRepository[YourEntity]):
       # Add methods
   ```

3. Create repository implementation:
   ```python
   # src/infrastructure/persistence/your_repository.py
   from ...domain.repositories import YourRepository
   
   class YourSQLiteRepository(YourRepository):
       # Implement methods
   ```

4. Add tests:
   ```python
   # tests/domain/test_your_entity.py
   # tests/infrastructure/test_your_repository.py
   ```

### Adding a New Service

1. Create service in application layer:
   ```python
   # src/application/services/your_service.py
   from .base_service import BaseService
   from ...domain.entities import YourEntity
   
   class YourService(BaseService[YourEntity]):
       # Add methods
   ```

2. Update container:
   ```python
   # src/infrastructure/container.py
   from ..application.services import YourService
   
   class Container:
       def _init_services(self):
           self._your_service = YourService(
               self._your_repository,
               self._logger
           )
   ```

3. Add tests:
   ```python
   # tests/application/test_your_service.py
   ```

## Best Practices

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings
- Keep functions small
- Use meaningful names

### Testing

- Write tests first (TDD)
- Test edge cases
- Use meaningful assertions
- Keep tests focused
- Use fixtures wisely

### Error Handling

- Use custom exceptions
- Log errors properly
- Provide context
- Handle edge cases
- Clean up resources

### Performance

- Use async where appropriate
- Cache expensive operations
- Batch database operations
- Profile critical paths
- Monitor memory usage

## Troubleshooting

### Common Issues

1. Database Errors
   ```bash
   # Check database state
   sqlite3 data/teddy.db ".tables"
   
   # Reset database
   make db-reset
   ```

2. Environment Issues
   ```bash
   # Check environment
   python -c "import sys; print(sys.path)"
   
   # Reset environment
   make clean
   make setup
   ```

3. Docker Issues
   ```bash
   # Clean Docker state
   make docker-clean
   
   # Rebuild containers
   make docker-build
   ```

### Getting Help

1. Check documentation
2. Search issue tracker
3. Ask in Discord
4. Contact maintainers

## Additional Resources

- [Architecture Documentation](../architecture/)
- [API Documentation](../api/)
- [Security Guidelines](../security/)
- [Contributing Guidelines](../../CONTRIBUTING.md)
