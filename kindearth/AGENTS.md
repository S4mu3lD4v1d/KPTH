# KindEarth Suite — AGENTS.md (In-house rules)

## Non-negotiables
- KindEarth is internal-only. Do NOT create any client-facing "productization" or licensing language.
- No recommendation may be "shipped" unless all Five Gates have responses (answers may be "uncertain", but must exist).
- Red Flags trigger a pause/escalation note; never ignore them.
- Signals (Green/Amber/Red) constrain external language outputs:
  - Green: grounded confidence
  - Amber: conditional language + explicit guardrails
  - Red: no impact claims; recommend pause/redesign

## The KindEarth Pillars (must stay intact)
1) Relational Accountability
2) Regenerative Impact
3) Ethical Grounding
4) Practical Stewardship
5) Reflective Continuity

## Implementation standards
- Prefer simple, testable Python.
- No hidden magic: store decisions, assumptions, uncertainties.
- All CLI commands must have --help and return non-zero on failure.
- Write unit tests for each gate + redflag rule.

## Safety + integrity
- Never fabricate outcomes.
- If a required detail is missing, create a TODO and block “compose/export” until resolved.
