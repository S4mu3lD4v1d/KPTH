# KindPath Collective Platform (KindEarth / KindPath) — Roadmap

This roadmap is doctrine-first and pilot-led.
We prioritise: **sovereignty, safety, auditability, and human-legible tools**.

Status tags:
- **Now** = actively building / stabilising
- **Next** = defined and ready once “Now” is stable
- **Later** = planned, but gated by governance + pilot learning

---

## Product Lines

### Inward-Facing (Core Platform / Pilot Infrastructure)
1) KindEarth Ecological Evaluation Tool  
2) KindEarth Social Policy Analyser & Forecasting Tool (drift, syntropy/entropy)  
3) KindPath Social Impact Consulting Tool  
4) KindPath Economic Forecasting Tool (in-house pilot only)  
5) KindPath Digital Library Tool (micro-community data sovereignty)  
6) KindPath Life-Field Tool (current reality vs ideal reality)

### Outward-Facing (Public / Education / Creative Interfaces)
7) Syntropic Farming & Food Security Education Tool  
8) ‘Q’ Audio / Music Analysis & Education Suite

---

## Now (0–8 weeks): Make the platform “pilot-grade”

### Repo & Documentation Spine
- [ ] Establish canonical tool map (`/docs/tools/TOOLS_OVERVIEW.md`)
- [ ] Add per-tool specs (even stubs) under `/docs/tools/`
- [ ] Add governance docs under `/docs/governance/`:
  - [ ] Data sovereignty
  - [ ] Consent & refusal
  - [ ] Ethics boundaries
- [ ] Add SECURITY + CONTRIBUTING
- [ ] Remove committed `.env` and enforce secret hygiene

### Platform Reliability (Prototype → Pilot Readiness)
- [ ] Docker Compose stack boots cleanly from docs (fresh machine test)
- [ ] Backups + restore verified (local → MinIO → external target)
- [ ] Signed export bundles working end-to-end (audit trail)
- [ ] Basic observability: health checks + minimal logs + error surfaces

### Digital Library (MVP)
- [ ] Upload / store items (local-first + cloud sync pattern)
- [ ] Search working (Meilisearch) with clear provenance fields
- [ ] Versioning / changelog records (who/what/when)
- [ ] Consent-aware redaction pathway (recorded, reversible, auditable)

### Life-Field (MVP)
- [ ] “Current reality vs ideal reality” capture
- [ ] Reflection entries + time-series progression
- [ ] Practitioner–participant shared visibility (role-based)
- [ ] Export a pilot bundle (signed)

---

## Next (2–4 months): Add analysis layers + pilot ops workflow

### KindEarth Ecological Evaluation Tool
- [ ] Input schema for ecological observations (place-based, non-extractive)
- [ ] Evaluation outputs: constraints, capacity, congruence (interpretable)
- [ ] Mapping outputs (basic) + export bundles

### KindEarth Social Policy Analyser & Forecasting
- [ ] Define drift and syntropy/entropy state machine (docs first)
- [ ] Implement baseline drift detection from pilot + context signals
- [ ] Scenario exploration (not prediction): “if-then” posture maps

### Social Impact Consulting Tool (Pilot Ops)
- [ ] Pilot creation templates
- [ ] Milestones + tapering checkpoints (ARR concept integrated)
- [ ] Reporting exports for institutions (plain language + audit trail)

---

## Later (4–12+ months): Outward-facing education + creative suite

### Syntropic Farming & Food Security Education Tool
- [ ] Region/place-based learning modules
- [ ] Micro-community library integration (local knowledge + provenance)
- [ ] Offline-first field access

### ‘Q’ Audio / Music Suite
- [ ] Analyzer mode (learning + accessibility)
- [ ] Field recording mode (environmental listening + sharing)
- [ ] Community sharing interfaces aligned to sovereignty principles

---

## Gates (non-negotiable)
We do not ship “outward-facing” tools at scale unless:
- governance is explicit and visible
- refusal paths are real and easy
- measurement remains benevolent and interpretable
- exports are auditable and ownership stays local

---

## Milestone Definitions
- **Prototype-grade:** runs locally, functions demonstrated
- **Pilot-grade:** reliable, auditable exports, consent + refusal enforced, backup/restore verified
- **Scale-ready:** governance hardened, UX stable, observability, documented operations, safe failure modes