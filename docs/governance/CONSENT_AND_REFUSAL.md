# Consent & Refusal (KindPath / KindEarth)

Consent is not a checkbox.
Refusal is not a failure.
Both are necessary conditions for ethical systems.

## Core Principle
**Participation must be voluntary, reversible, and understandable.**

---

## Consent Requirements (Non-negotiable)

1. **Informed**
   - People understand what is being collected, why, how it’s used, and what it can’t do.

2. **Freely given**
   - No coercion, no hidden penalties, no “services withheld unless you agree”.

3. **Specific**
   - Consent is tied to defined scopes and purposes.
   - “All future uses” is not acceptable.

4. **Revocable**
   - Consent can be withdrawn at any time.
   - Withdrawal must be simple and non-punitive.

5. **Recorded**
   - Consent should be logged as a clear record (who/what/when/scope/version).

---

## Refusal Rights (Structural)

Refusal must be:
- allowed at entry (opt-out)
- allowed during participation (pause/partial refusal)
- allowed at any time (exit)
- treated as a legitimate outcome

Refusal must not trigger:
- retaliation
- reduction in basic dignity
- loss of access to essential supports outside this platform

---

## Consent Scopes (Recommended Model)

Consent must be expressed in scopes such as:

1. **Collection Scope**
   - what data types may be collected (e.g., reflections, library items, ecological observations)

2. **Access Scope**
   - who can view it (participant, practitioner, custodian, evaluator)

3. **Use Scope**
   - what it can be used for (pilot support, learning, reporting, evaluation)

4. **Sharing Scope**
   - whether it can be exported, and to whom

5. **Retention Scope**
   - how long it is kept and how deletion is handled

---

## Safe Failure & Withdrawal

When a participant withdraws:
- their data remains theirs
- they may request export
- they may request deletion where feasible
- the system should record withdrawal without moralising

The platform must degrade safely:
- partial data should not produce “judgements”
- missing data should be treated as unknown, not negative

---

## Implementation Expectations (Developer Notes)

- Consent must be enforced at the API boundary (not only UI)
- Access tokens should reflect consent scopes
- Exports must require explicit permission (and preferably be signed)
- Audit log of export actions:
  - who exported
  - what scope
  - where it went
  - when it happened

---

## Success Criteria

Consent and refusal are working when:
- people understand their choices
- opt-out is simple and respected
- pilots can end without dependency or abandonment
- trust is strengthened through transparency