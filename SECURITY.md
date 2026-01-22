# Security Policy

## Reporting a Vulnerability

Please report security vulnerabilities to the maintainers via email. Do not open public issues for security flaws.

## Data Handling
- **API Tokens**: Customer tokens are handled transiently in the execution state. Ensure SSL/TLS is enabled on the backend.
- **Environment Variables**: API keys and secrets should be stored in `.env` and never committed to version control.
