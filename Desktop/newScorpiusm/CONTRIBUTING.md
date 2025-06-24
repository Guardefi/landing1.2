# Contributing to Scorpius DeFi Security Platform

Welcome to the Scorpius DeFi Security Platform! We're excited that you want to contribute. This guide will help you get started quickly and ensure your contributions align with our standards.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** - For containerized development
- **Node.js 18+** - For frontend development
- **Python 3.11+** - For backend development
- **Git** - Version control

### One-Command Setup

```bash
# Clone the repository
git clone <repository-url>
cd scorpius

# Start the complete development environment
just dev

# Alternative: Use Docker Compose directly
docker-compose -f docker-compose.dev.yml --profile dev up
```

**Target Setup Time**: ≤90 seconds for subsequent runs, ≤5 minutes for first-time setup

## 🏗️ Development Environment

### Available Profiles

```bash
# Minimal (databases only) - fastest startup
just compose-minimal

# Full development environment
just dev
# or
just compose

# With monitoring tools (Grafana, Prometheus, Jaeger)
just compose-monitoring

# With development tools (Adminer, Redis Commander, Mailhog)
just compose-tools
```

### Service URLs

Once running, access these services:

- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin123)
- **Prometheus**: http://localhost:9090
- **Jaeger Tracing**: http://localhost:16686
- **Database Admin**: http://localhost:8081
- **Redis Commander**: http://localhost:8082
- **Email Testing**: http://localhost:8025

### Hot Reload Development

The development environment supports hot reload for both frontend and backend:

- **Frontend**: Vite hot module replacement (HMR)
- **Backend**: FastAPI with watchfiles auto-reload
- **File watching**: Automatically detects changes in `.py`, `.ts`, `.tsx`, `.yaml` files

## 📋 Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Edit files and the development server will automatically reload:

```bash
# Start development environment
just dev

# In another terminal, make changes to:
# - Frontend: src/**/*.tsx, src/**/*.ts
# - Backend: backend/**/*.py
# - Styles: src/**/*.css, tailwind.config.ts
```

### 3. Run Quality Checks

```bash
# Run all tests
just test

# Run linting and formatting
just lint

# Fix linting issues automatically
just lint-fix

# Format code
just format
```

### 4. Commit Your Changes

```bash
# Add your changes
git add .

# Commit (pre-commit hooks will run automatically)
git commit -m "feat: add new vulnerability detection rule"

# Push to your branch
git push origin feature/your-feature-name
```

### 5. Create Pull Request

- Open a PR against the `main` branch
- Fill out the PR template
- Ensure all CI checks pass
- Request review from code owners

## 🧪 Testing

### Running Tests

```bash
# All tests (frontend + backend)
just test

# Frontend tests only
just test-frontend

# Backend tests only
just test-backend

# With coverage report
just test-coverage
```

### Test Coverage Requirements

- **Backend**: Minimum 20% coverage
- **Frontend**: Minimum 10% coverage
- **New code**: Should include tests for new functionality

### Writing Tests

#### Backend Tests

```python
# backend/tests/test_example.py
import pytest
from fastapi.testclient import TestClient

def test_vulnerability_scanner(client: TestClient):
    response = client.post("/api/v1/scan", json={
        "address": "0x1234567890123456789012345678901234567890"
    })
    assert response.status_code == 200
    assert "scan_id" in response.json()
```

#### Frontend Tests

```typescript
// src/test/components/Example.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ExampleComponent from '../ExampleComponent';

describe('ExampleComponent', () => {
  it('renders without crashing', () => {
    render(<ExampleComponent />);
    expect(screen.getByText('Example')).toBeInTheDocument();
  });
});
```

## 🔍 Code Quality Standards

### Linting and Formatting

Our project uses strict code quality standards:

- **Python**: Ruff (all rules), Black, isort
- **TypeScript**: ESLint (strict), Prettier
- **Automatic fixing**: `just lint-fix`

### Pre-commit Hooks

Pre-commit hooks automatically run on every commit:

- Code formatting (Black, Prettier)
- Linting (Ruff, ESLint)
- Type checking (mypy, TypeScript)
- Security scanning (gitleaks)
- Test suite execution

### Code Style Guidelines

#### Python

```python
# Use type hints
def calculate_risk_score(vulnerabilities: List[Vulnerability]) -> float:
    """Calculate risk score based on vulnerabilities."""
    if not vulnerabilities:
        return 0.0

    # Implementation here
    return risk_score

# Use async/await for I/O operations
async def scan_contract(address: str) -> ScanResult:
    """Scan smart contract for vulnerabilities."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/scan/{address}")
        return ScanResult.parse_obj(response.json())
```

#### TypeScript/React

```typescript
// Use proper typing
interface VulnerabilityProps {
  vulnerability: Vulnerability;
  onSelect: (id: string) => void;
}

// Functional components with hooks
export function VulnerabilityCard({ vulnerability, onSelect }: VulnerabilityProps) {
  const handleClick = useCallback(() => {
    onSelect(vulnerability.id);
  }, [vulnerability.id, onSelect]);

  return (
    <Card onClick={handleClick}>
      <CardHeader>
        <CardTitle>{vulnerability.title}</CardTitle>
      </CardHeader>
    </Card>
  );
}
```

## 🗄️ Database Management

### Local Development Database

```bash
# Reset database to clean state
just reset-db

# Seed with test data
just seed

# Access database directly
docker-compose -f docker-compose.dev.yml exec postgres psql -U scorpius -d scorpius_dev
```

### Migrations

```bash
# Create new migration
cd backend
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Check migration status
alembic current
```

## 📊 Monitoring and Debugging

### Logs

```bash
# View all service logs
just logs

# View specific service logs
docker-compose -f docker-compose.dev.yml logs -f backend
docker-compose -f docker-compose.dev.yml logs -f frontend
```

### Debugging

#### Backend Debugging

The development container includes `debugpy` for remote debugging:

```python
# Add breakpoint in your code
import debugpy
debugpy.breakpoint()
```

Connect your IDE to port 5678 for debugging.

#### Frontend Debugging

- **Browser DevTools**: React DevTools extension
- **VS Code**: Attach to Vite dev server
- **Network requests**: Use browser Network tab or API docs

### Performance Monitoring

Access monitoring tools:

- **Application metrics**: Grafana dashboards
- **Distributed tracing**: Jaeger UI
- **Database performance**: Adminer + query logs
- **API performance**: FastAPI built-in metrics

## 🔐 Security Guidelines

### Environment Variables

```bash
# Never commit secrets
# Use environment variables for all sensitive data
DATABASE_URL="postgresql://user:pass@host:port/db"
SECRET_KEY="use-strong-random-keys"

# For development, use the provided .env.example
cp .env.example .env
```

### Security Scanning

```bash
# Run security scans
just security

# Manual scans
gitleaks detect --no-banner
npm audit
bandit -r backend/
```

### Dependency Management

- Keep dependencies updated
- Review security advisories
- Use `npm audit` and `safety` for vulnerability scanning

## 🐛 Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check what's using ports
lsof -i :8080
lsof -i :8000

# Stop conflicting services
just compose-down
```

#### Database Connection Issues

```bash
# Reset database
just reset-db

# Check database status
docker-compose -f docker-compose.dev.yml ps postgres
```

#### Frontend Build Issues

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Or use Docker
docker-compose -f docker-compose.dev.yml build frontend
```

#### Backend Import Issues

```bash
# Check Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"

# Reinstall dependencies
cd backend
pip install -r requirements.txt -r requirements-dev.txt
```

### Getting Help

1. **Check the logs**: `just logs`
2. **Check service status**: `just status`
3. **Search existing issues**: GitHub Issues
4. **Ask the team**: Create a GitHub Discussion
5. **Emergency**: Contact maintainers directly

## 📁 Project Structure

### Key Directories

```
scorpius/
├── backend/                 # FastAPI backend
│   ├── routes/             # API endpoints
│   ├── models/             # Database models
│   ├── services/           # Business logic
│   ├── tests/              # Backend tests
│   └── alembic/            # Database migrations
│
├── src/                    # React frontend
│   ├── components/         # React components
│   ├── pages/              # Page components
│   ├── hooks/              # Custom hooks
│   ├── services/           # API services
│   └── test/               # Frontend tests
│
├── config-files/           # Configuration files
├── monitoring/             # Grafana, Prometheus configs
├── infrastructure/         # Deployment configs
└── docs/                   # Documentation
```

### Important Files

- `justfile` - Task automation
- `docker-compose.dev.yml` - Development environment
- `pyproject.toml` - Python project configuration
- `package.json` - Node.js project configuration
- `.pre-commit-config.yaml` - Code quality hooks
- `ARCHITECTURE.md` - System architecture

## 🚀 Performance Guidelines

### Frontend Performance

- Use React.memo for expensive components
- Implement proper component lazy loading
- Optimize bundle size with dynamic imports
- Use proper TypeScript for better tree shaking

### Backend Performance

- Use async/await for all I/O operations
- Implement proper database connection pooling
- Use caching (Redis) for frequently accessed data
- Profile slow endpoints with APM tools

### Database Performance

- Use proper indexes for queries
- Implement query optimization
- Use database connection pooling
- Monitor slow queries in development

## 📝 Documentation

### Code Documentation

- **Python**: Use docstrings for all functions and classes
- **TypeScript**: Use JSDoc comments for complex functions
- **API**: Document all endpoints in FastAPI (automatically generates docs)

### Architecture Documentation

- Update `ARCHITECTURE.md` for significant changes
- Document design decisions in ADRs (Architecture Decision Records)
- Keep README files updated in subdirectories

## 🤝 Code Review Guidelines

### For Contributors

- Keep PRs focused and small
- Write clear commit messages
- Add tests for new functionality
- Update documentation as needed
- Respond to review feedback promptly

### For Reviewers

- Be constructive and helpful
- Check for security issues
- Verify tests cover new functionality
- Ensure code follows style guidelines
- Test the changes locally if needed

## 🎯 Release Process

### Version Management

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Tag releases in Git
- Update CHANGELOG.md
- Follow conventional commits for automatic changelog generation

### Deployment

```bash
# Build for production
just build-prod

# Deploy to staging
just deploy-staging

# Deploy to production (manual approval required)
just deploy-prod
```

## 🏆 Best Practices

### General

1. **Write tests first** (TDD when possible)
2. **Keep functions small** and focused
3. **Use meaningful names** for variables and functions
4. **Handle errors gracefully** with proper logging
5. **Document complex business logic**

### Security

1. **Never commit secrets** to version control
2. **Validate all inputs** on both frontend and backend
3. **Use parameterized queries** to prevent SQL injection
4. **Implement proper authentication** and authorization
5. **Keep dependencies updated** and scan for vulnerabilities

### Performance

1. **Profile before optimizing**
2. **Use caching appropriately**
3. **Implement proper error handling**
4. **Monitor resource usage**
5. **Optimize database queries**

---

## 📞 Contact

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: dev@scorpius.security
- **Docs**: See `ARCHITECTURE.md` for system design

Thank you for contributing to Scorpius! 🦂

---

_Happy coding! Let's build the future of DeFi security together._
