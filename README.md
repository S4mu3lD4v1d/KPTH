# KindPath Collective Platform (KindEarth / KindPath)

A digital-native platform in active development: pilot operations, community digital libraries,
ecological evaluation, and social-policy analysis — designed to be sovereignty-first, auditable,
and non-extractive.

> The real currency on Earth is intentional human time.
> This platform exists to make upstream conditions legible, measurable, and governable without coercion.

## What this repository is
This repo contains the **platform prototype** and supporting services, including:
- Data capture + event publishing (Redpanda / Kafka-compatible)
- Community Digital Library (search, provenance, redaction tracking)
- Ecological Evaluation tooling (mapping, metrics, signed export bundles)
- Background worker for real-time analysis (Celery)
- Infrastructure stack (Postgres, MinIO/S3, Meilisearch, Vault)

## What this repository is not
- Not a consumer social platform
- Not a prediction engine
- Not surveillance or “scoring people”
- Not a promise of outcomes

## Architecture (current)
- **Data Capture Service:** ingests data and publishes to Redpanda with local encrypted storage
- **Digital Library Service:** CRUD for literature, Meilisearch search, provenance + redaction tracking, mapping + currency checks
- **Ecological Evaluation Service:** mapping + metrics + exports to configured endpoints with signed bundles
- **Worker:** background analysis using Celery
- **Infrastructure:** Docker Compose with Redpanda, PostgreSQL, MinIO (S3), Meilisearch, Vault (secrets)

Data is encrypted at rest (MinIO SSE), with transport encryption planned (TLS),
and optional message-level encryption. Backups can be duplicated locally, to MinIO,
and to external services. Exports are signed and sent to configured endpoints.

## Quick Start
1. Copy `.env.example` → `.env` and configure values.
2. Run `./scripts/dev/up`
3. Access services on localhost ports (e.g. data-capture:8001, digital-library:8002)

## Canonical Tool Map (docs-first)
See:
- `/docs/tools/TOOLS_OVERVIEW.md`
- `/docs/tools/*.md`

## Status
**Prototype / Pilot-readiness build.**
This repo prioritises:
- clarity over hype
- doctrine and boundaries before automation
- manual validation before scaling

## Licence
MIT (see LICENSE).

## Community
Questions, ideas, and proposals live in KindPath Discussions:
https://github.com/S4mu3lD4v1d/kindpath-starter/discussions

For bugs and trackable engineering tasks, use KPTH Issues.