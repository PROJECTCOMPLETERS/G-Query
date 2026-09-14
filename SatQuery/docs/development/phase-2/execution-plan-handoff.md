# SatQuery Phase 2 → Phase 3 Handoff Contract

## Purpose

This document defines the handoff boundary between Phase 2 and Phase 3 of the SatQuery backend.

Phase 2 is responsible for taking a user query through:

Query
↓
Query Understanding
↓
Task Prediction
↓
Data Requirements
↓
Data Readiness
↓
Execution Planning
↓
EXECUTION_PLANNED

Phase 3 will consume the final `ExecutionPlan`.

This document defines what Phase 2 guarantees and what information is available to Phase 3.

---

## Phase 2 Endpoint

The final runtime state produced by Phase 2 is:

`EXECUTION_PLANNED`

At this point:

- The user query has been structurally understood.
- The task has been identified.
- Required data has been defined.
- Data readiness has been evaluated by the Data Engine.
- The required execution information has been assembled into an `ExecutionPlan`.

Phase 2 does not execute a model or produce an analysis result.

---

## ExecutionPlan Contract

The canonical Phase 2 `ExecutionPlan` contains:

```text
ExecutionPlan
├── schema_version
├── request_id
├── task
├── input_observations
├── required_modalities
├── temporal_requirements
├── spatial_requirements
├── preprocessing
├── model_requirements
└── expected_output