# Data Sovereignty (KindPath / KindEarth)

This platform is sovereignty-first by design.
Data is not neutral. Knowledge is relational. Ownership matters.

## Core Principle
**Local people and communities retain ownership and interpretive authority over their data.**

The platform must never require:
- centralised ownership
- hidden data extraction
- forced cloud dependence
- proprietary lock-in that prevents exit

---

## Definitions

### Data Owner
The individual, family, community, or authorised custodian group who has primary authority over data created in their context.

### Custodian
A person or organisation authorised by the Data Owner to store, administer, or help interpret data under explicit conditions.

### Operator
An individual or organisation running infrastructure or services (e.g., hosting) without ownership rights unless explicitly granted.

### Export Bundle
A signed, auditable package of data intended to be shared externally with explicit permission.

---

## Ownership Rules (Non-negotiable)

1. **Ownership stays local**
   - Data created in pilots belongs to the participant/community by default.

2. **Portability**
   - Data must be exportable in readable formats.
   - Exports must not require proprietary tools to access.

3. **Minimal collection**
   - Collect only what is necessary for the stated purpose.
   - Avoid “just in case” hoarding.

4. **Purpose limitation**
   - Data may only be used for the purposes consented to.
   - New purposes require new consent.

---

## Storage & Sync Posture

### Local-first
The platform prefers local ownership and local storage where feasible.

### Cloud as an option, not a requirement
Cloud sync may be used only when:
- explicitly enabled by the Data Owner
- reversible (exit is possible)
- access and sharing rules are transparent

### Backup requirements
Backups must be:
- encrypted at rest
- recoverable without vendor lock-in
- auditable (when, by whom, what changed)

---

## Provenance & Changelogs

All significant objects and records must support provenance metadata:
- who created it
- when it was created
- what version it is
- what changed and why
- who approved the change (where relevant)

Changelogs are not surveillance.
They exist to preserve shared truth and reduce contradiction.

---

## Sharing & External Access

External sharing must use:
- explicit scopes (what is shared, with whom, for how long)
- signed export bundles when feasible
- revocation paths (sharing can be withdrawn)

No third-party access by default.

---

## Implementation Expectations (Developer Notes)

- Role-based access control (participant / practitioner / custodian / operator)
- Audit logs for exports and major changes
- `.env` and secrets never committed
- Consent scopes enforced at the API boundary (not just UI)

---

## Success Criteria

Data sovereignty is working when:
- communities can exit without losing their records
- participants understand what is collected and why
- no tool requires extraction to function
- trust increases rather than decays over time