# KindPath Collective Platform — Architecture (KindEarth / KindPath)

This document describes the platform architecture at a high level.
The platform is designed to be:
- sovereignty-first
- audit-friendly
- local ownership by default
- modular (tools can be adopted independently)

---

## Conceptual Layers

### 1) Interfaces (People + Community)
- **Life-Field Tool** (current vs ideal reality, reflections, progression)
- **Digital Library** (shared knowledge, provenance, changelogs)
- (Later) **Syntropic Food Tool**, **Q Audio Suite**

### 2) Intelligence (KindEarth + KindPath Analysis)
- **Ecological Evaluation** (constraints, capacity, congruence)
- **Policy Analyser** (drift, syntropy/entropy, scenario exploration)
- **Economic Forecasting** (in-house posture mapping only)

### 3) Operations (Pilots + Reporting)
- Pilot templates, milestones, tapering checkpoints
- Signed exports, reporting bundles, audit logs

### 4) Sovereignty & Integrity
- Consent and refusal enforcement
- Local ownership + export controls
- Audit trails + provenance
- Secret hygiene and secure transport/storage

---

## Current Implementation (Services)

The repository currently contains a multi-service prototype stack (Docker Compose) with:

- **Data Capture Service**
  - Ingests structured data
  - Publishes events to Redpanda
  - Stores locally with encryption-at-rest intent

- **Digital Library Service**
  - CRUD for literature items
  - Search (Meilisearch)
  - Provenance + redaction tracking
  - Mapping / relationship exploration
  - Currency checks / “is this still current?” workflows

- **Ecological Evaluation Service**
  - Captures ecological observations and mappings
  - Generates export bundles
  - Sends signed exports to configured endpoints

- **Worker**
  - Celery background jobs for ongoing analysis, indexing, exports, and checks

---

## Data Flow (High Level)

User/Practitioner actions (Life-Field, Library, Eco Eval) produce **events** and **records**.
Those are stored locally, synchronised as permitted, indexed for search, and bundled for export.

```text
[Life-Field UI]         [Digital Library UI]        [Eco Eval UI]
      |                       |                          |
      v                       v                          v
+----------------+    +--------------------+     +--------------------+
| Data Capture   |    | Digital Library    |     | Ecological Eval    |
| Service        |    | Service            |     | Service            |
+--------+-------+    +---------+----------+     +---------+----------+
         |                       |                          |
         | events                | index/update             | export bundle
         v                       v                          v
   +-----------+            +-----------+              +------------+
   | Redpanda  |            | Meilisearch|             | Signed      |
   | (bus)     |            | (search)  |              | Exports     |
   +-----+-----+            +-----+-----+              +------+------+
         |                       |                           |
         v                       v                           v
   +-----------+            +-----------+              +-------------+
   | Worker    |----------->| Postgres  |              | Endpoints   |
   | (Celery)  |            | + MinIO   |              | (config)    |
   +-----------+            | (S3)      |              +-------------+
                            +-----------+

Storage & Integrity Model
Storage

Postgres: structured records, metadata, references

MinIO (S3): objects, documents, media, bundles (SSE encryption-at-rest)

Local-first posture: local ownership is default; sync is governed

Integrity

Provenance: who/what/when/version for library items and pilot records

Audit logs: exports and significant changes create traceable events

Signed bundles: exports are signed to support audit and tamper detection

Security

Vault: secrets management (no secrets committed)

Transport encryption: planned/required for production

Message-level encryption (optional): for sensitive lanes where needed

Tool-to-Service Mapping
Tool	Primary Service(s)	Status
Digital Library Tool	digital-library + storage + search	Active
Life-Field Tool	kindpath-life-field + data-capture	Active/Building
Ecological Evaluation Tool	ecological-tool + exports	Active/Building
Social Policy Analyser	kindearth (planned) + worker	Planned
Social Impact Consulting Tool	pilot ops (planned)	Planned
Economic Forecasting Tool	worker + kindearth signals	Planned (in-house)
Syntropic Food Education Tool	(separate product lane)	Later
‘Q’ Audio Suite	(separate product lane)	Later
Design Rules (Non-negotiable)

Refusal without penalty

Local ownership by default

No black-box decisioning

Auditability over novelty

Exportable, portable, reversible

If a component violates these, it must be redesigned or removed.