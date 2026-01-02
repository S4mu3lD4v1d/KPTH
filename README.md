# KindPath Foundation App Suite

A suite of applications for KindPath Foundation, including data capture, digital library, and ecological evaluation tools with encryption, backups, and real-time analysis.

## Architecture

- **Data Capture Service**: Ingests data and publishes to Redpanda (Kafka-compatible), with local encrypted storage.
- **Digital Library Service**: CRUD operations for literature, search via Meilisearch, redaction tracking, and provenance. Includes literature mapping with links and currency checks.
- **Ecological Evaluation Service**: Mapping, metrics, exports to configured endpoints with signed bundles.
- **Worker**: Background real-time analysis using Celery.
- **Infrastructure**: Docker Compose with Redpanda, PostgreSQL, MinIO (S3), Meilisearch, Vault (secrets).

Data is encrypted at rest (MinIO SSE), transport (TLS), and optionally message-level. Backups are duplicated locally, to MinIO, and to external services. Exports are signed and sent to audited endpoints.

## Quick Start

1. Copy `.env.example` to `.env` and configure secrets (sample keys generated).
2. Run `./scripts/dev/up` to start services.
3. Access services at localhost ports (e.g., data-capture:8001, digital-library:8002, etc.).

## Literature Mapping

- Upload literature with currency date.
- Link articles via `/literature/{id}/link` (types: related, cites, redacted_from).
- View map via `/literature/{id}/map`.
- Check outdated articles via `/literature/currency?days_old=365`.
- Update with provenance tracking: PUT /literature/{id} logs versions.

## Ecological Mapping & Congruence

- Post data with coords: POST /eco-data.
- View map: GET /eco-data/map.
- Dashboard: GET /dashboard (Leaflet map).
- Send for global congruence: POST /eco-data/congruence.

## Backups

- `./scripts/backup/create`: Backs up DB to local, MinIO, and external services.
- `./scripts/backup/restore <id>`: Restores from backup.

## Hidden Service

- Worker runs as systemd service: `sudo cp services/worker/kindpath-worker.service /etc/systemd/system/ && sudo systemctl enable kindpath-worker && sudo systemctl start kindpath-worker`.

## Real-time Analysis

- Worker analyzes data for climate trends (linear regression, significance).

## Development

- `./scripts/dev/up`: Start all services.
- `./scripts/dev/down`: Stop services.

## Final Touches Needed

- Configure real external endpoints/tokens in .env.
- Add TLS certificates for transport encryption.
- Test end-to-end once services up.