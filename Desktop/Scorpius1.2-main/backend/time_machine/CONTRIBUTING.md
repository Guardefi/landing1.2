# Contributing to Scorpius Time Machine

## Development Setup

1. **Clone the repository:**

   ```bash
   git clone git@github.com:Guardefi/SCORPIUS-TIME-MACHINE.git
   cd SCORPIUS-TIME-MACHINE
   ```

2. **Set up Python environment:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend:**

   ```bash
   cd ui
   npm install
   npm run build
   cd ..
   ```

4. **Configure environment:**

   ```bash
   cp .env.example .env.development
   # Edit .env.development with your settings
   ```

## Code Standards

- **Python:** Follow PEP 8, use type hints
- **TypeScript/React:** Follow ESLint and Prettier configurations
- **Commits:** Use conventional commit format
- **Testing:** Write tests for new features
- **Documentation:** Update README and inline docs

## Pull Request Process

1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Run linting and tests locally
4. Submit PR with clear description
5. Address review feedback
6. Squash and merge after approval

## Code Review Guidelines

- Focus on security, performance, and maintainability
- Ensure comprehensive test coverage
- Verify documentation is updated
- Check for potential security vulnerabilities

## Security

- Report security issues privately to the maintainers
- Follow secure coding practices
- Use dependency scanning tools
- Validate all inputs and sanitize outputs

## Performance

- Profile critical paths
- Optimize database queries
- Minimize API response times
- Use appropriate caching strategies

## Questions?

Open an issue or reach out to the maintainers for guidance.
