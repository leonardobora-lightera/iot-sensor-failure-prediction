<!-- Sync Impact Report
Version change: none -> 0.1.0
Modified principles: (added) Ground-Truth First; Data Preservation & Exploration; Observability & Telemetry; Testing & Validation; Governance & Versioning
Added sections: Data Handling & Privacy; Development Workflow
Removed sections: none
Templates updated:
 - .specify/templates/plan-template.md -> updated (Constitution Check clarified)
 - .specify/templates/spec-template.md -> updated (reference to constitution added)
 - .specify/templates/tasks-template.md -> updated (reference to constitution added)
Templates pending review: .specify/templates/commands/*.md -> pending (verify agent-specific references)
Follow-up TODOs: none.
-->
# IoT-SPD Troubleshooting Constitution

## Core Principles

### Ground-Truth First (NON-NEGOTIABLE)

When direct ground-truth signals exist in the data, they MUST be preserved and prioritized over derived or proxy indicators. In practice for IoT-SPD this means: all occurrences of `msg_type == 6` and their `buffer_error` codes are ground-truth failure events and MUST NOT be filtered out by automated rules. Any model labels, feature engineering, or alerts that contradict preserved ground-truth data MUST be justified and documented.

Rationale: A direct failure signal (device-reported error) is higher fidelity than inferred proxies (e.g., CV instability). Prioritizing ground truth reduces label noise and improves downstream model validity.

### Data Preservation & Exploration

Raw telemetry and error fields MUST be retained through ingestion and early processing stages. Exploratory analysis via notebooks (Phase 0 artifacts) is REQUIRED prior to applying destructive filters. All filtering steps MUST be reversible or recorded (audit trail) so analysts can re-run upstream transformations and validate information preservation.

Rationale: Early exploratory analysis uncovers signals (e.g., `buffer_error` taxonomy) that automated filters can inadvertently discard. Keeping raw data prevents irreversible information loss.

### Observability & Telemetry

All pipeline stages MUST emit structured telemetry (timestamped logs, event traces, and metrics) that include provenance for derived features. Error taxonomies (28 `buffer_error` codes and their mapped categories) MUST be codified in a shared location and available to models, monitoring, and runbooks.

Rationale: Observability enables rapid diagnosis and correlation between precursor signals (e.g., CV instability) and ground-truth failures (msg_type 6). A shared taxonomy reduces ambiguity.

### Testing & Validation (Data + Model)

Data pipelines MUST include validation tests that assert preservation of critical signals (e.g., counts of `msg_type == 6` before/after each filter). Model training artifacts MUST include holdout validations that measure lead-time detection (7d, 15d, 30d) and ensure models are not trained on filtered-out ground truth. Changes that materially alter data shapes or label definitions require a patch-level or minor-level version bump and a documented migration/rollback plan.

Rationale: Tests prevent regressions where important signals are lost. Explicit validation of lead time is necessary because precursor patterns (CV increase) may manifest days or weeks before failures.

### Governance & Versioning

Constitution amendments and changes to mandatory gates are governed by semantic versioning (MAJOR.MINOR.PATCH). Amendments that add new principles or materially change obligations -> MINOR. Wording clarifications -> PATCH. Backwards-incompatible governance changes (removing or redefining non-negotiable principles) -> MAJOR. Every amendment MUST include: change rationale, migration plan, a data validation checklist, and an approval PR.

Rationale: Clear rules for changes maintain trust and enable safe evolution of development practices.

## Data Handling & Privacy

All telemetry and error data handled by this project MUST comply with applicable data protection rules. Sensitive fields (if any) must be redacted at the earliest point required by law or policy. Data retention policies and anonymization strategies MUST be documented in `docs/data-retention.md` and linked from the spec for any feature that ingests or exposes device identifiers.

Rationale: Operational telemetry often contains device identifiers and location metadata; explicit handling and documentation avoids accidental leaks and makes downstream processing safer.

## Development Workflow & Quality Gates

1. All changes MUST be proposed via pull request with an implementation plan and tests.
2. Every PR that touches ingestion, filtering, or labeling logic MUST include a `Constitution Check` artifact in its plan: a short checklist that verifies key signals (example: `msg_type 6` counts preserved, `buffer_error` codes preserved).
3. CI gates MUST include: unit tests, data-contract tests (schema validation), and a preservation test asserting counts of `msg_type == 6` do not drop unless explicitly intended and documented.
4. Any change that affects labels or the training dataset MUST include reproducer scripts and before/after validation metrics (msg6_count, unique buffer_error codes, devices with errors).

Rationale: Embedding these gates into the workflow prevents regressions and keeps ML training aligned with ground truth.

## Governance

All project teams MUST treat this Constitution as the source of truth for development gates. Amendments follow this process:

1. Propose change in a PR that updates `.specify/memory/constitution.md` and includes: rationale, risk assessment, migration steps, and validation checklist.
2. At least one domain owner (data scientist) and one engineering owner MUST approve changes.
3. Execute migration/validation in a feature branch and present results before merging.

**Version**: 0.1.0 | **Ratified**: 2025-10-31 | **Last Amended**: 2025-10-31

Amendment notes: initial creation capturing the project's data-first and ground-truth priorities. Subsequent clarifications (typo fixes, wording changes) should be PATCH bumps; new principles or governance changes should be MINOR or MAJOR as per rules above.
