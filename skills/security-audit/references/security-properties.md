# Kafka Security Properties

Detailed property lists for authentication, encryption and secrets scanning. Referenced from the main SKILL.md workflow.

## Authentication Properties

- `security.protocol` or `security_protocol` (values: PLAINTEXT, SSL, SASL_PLAINTEXT, SASL_SSL)
- `sasl.mechanism` or `sasl_mechanism` (values: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI, OAUTHBEARER)
- `sasl.jaas.config` or equivalent
- `sasl.username` / `sasl.password`

## Encryption Properties

- `ssl.truststore.location` / `ssl.keystore.location`
- `ssl.truststore.password` / `ssl.keystore.password`
- `ssl.key.password`
- `ssl.endpoint.identification.algorithm`

## Files to Scan

- All source files (`src/`, `app/`, `lib/`)
- Configuration files (`config/`, `*.properties`, `*.yaml`, `*.yml`, `*.toml`)
- Environment files (`.env`, `.env.example`, `.env.production`)
- Docker files (`docker-compose*.yml`, `Dockerfile*`)
- CI/CD files (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`)

## Authentication Audit Rules

### Critical
- `security.protocol=PLAINTEXT` in production/staging configs
- `sasl.mechanism=PLAIN` without SSL/TLS (credentials sent in cleartext)
- No authentication configured at all in production

### Warning
- `sasl.mechanism=PLAIN` even with TLS (weaker than SCRAM)
- Missing `ssl.endpoint.identification.algorithm` (vulnerable to man-in-the-middle)
- JAAS config with inline credentials instead of environment variables

### Suggestion
- Consider upgrading from SCRAM-SHA-256 to SCRAM-SHA-512
- Consider OAUTHBEARER for modern token-based authentication

## Encryption Audit Rules

### Critical
- No SSL/TLS configured for production environments
- Self-signed certificates in production without proper trust chain

### Warning
- `ssl.endpoint.identification.algorithm=""` (hostname verification disabled)
- Keystore/truststore passwords in plaintext config files
- Missing inter-broker encryption (broker-to-broker traffic)

## Secrets Audit Rules

### Critical
- Hardcoded passwords, API keys or keystore passwords in source files
- Credentials committed to version control (check `.env` files tracked by git)
- Broker addresses with credentials in connection strings

### Warning
- `.env.example` containing real credentials instead of placeholders
- Secrets in docker-compose files without proper secret management
- Missing `.gitignore` entries for credential files

### Patterns to Search For
- `password`, `secret`, `api_key`, `apikey`, `token`, `credential`
- Base64-encoded strings in config files
- Connection strings containing `@` (embedded credentials)
