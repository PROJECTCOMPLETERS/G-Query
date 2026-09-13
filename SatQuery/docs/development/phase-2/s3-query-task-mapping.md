# Query-Task Mapping Test Cases

## Purpose
This document defines 20 realistic user queries for satellite image analysis, maps each to expected tasks and capabilities, and identifies edge cases for validation.

---

## Test Query List (20 Queries)

| # | Query | Input | Expected Task | Capabilities |
|---|-------|-------|---------------|--------------|
| 1 | What is in this satellite image? | 1 image | General VLM | Image Understanding |
| 2 | Where are the buildings? | 1 image | Spatial Object Analysis | Visual Grounding |
| 3 | Find all the buildings. | 1 image | Spatial Object Analysis | Object Detection |
| 4 | How many buildings are there? | 1 image | Spatial Object Analysis | Object Detection + Counting |
| 5 | Identify the roads. | 1 image | Spatial Object Analysis | Object Detection |
| 6 | Classify this satellite image. | 1 image | Satellite Image Understanding | Classification |
| 7 | Describe this area. | 1 image | General VLM | Image Captioning |
| 8 | What changed between these two images? | 2 images | Multi-Observation Analysis | Comparison + Change Detection |
| 9 | Compare these two images. | 2 images | Multi-Observation Analysis | Comparison |
| 10 | Compare the optical images. | 2 optical images | Multi-Observation Analysis | Modality-Specific Comparison (Optical) |
| 11 | Compare the SAR images. | 2 SAR images | Multi-Observation Analysis | Modality-Specific Comparison (SAR) |
| 12 | Compare the optical and SAR images. | 1 optical + 1 SAR image | Multi-Observation Analysis | Cross-Modality Comparison |
| 13 | Identify the flooded area. | 1+ image | Geospatial / Environmental Analysis | Flood Detection |
| 14 | Show the water bodies. | 1 image | Spatial Object Analysis | Water Body Detection |
| 15 | What happened to this area between 2020 and 2025? | 2 images (temporal) | Multi-Observation Analysis | Temporal Change Analysis |
| 16 | Which image shows more buildings? | 2 images | Multi-Observation Analysis | Comparison + Counting |
| 17 | Are there new buildings in the second image? | 2 images | Multi-Observation Analysis | Change Detection (New Construction) |
| 18 | Analyze this satellite image. | 1 image | General VLM | General Analysis |
| 19 | What structures are visible and where are they? | 1 image | Spatial Object Analysis | Object Detection + Visual Grounding |
| 20 | What is the difference between these two observations? | 2 images | Multi-Observation Analysis | Difference Analysis |

---

## Edge Case Testing

### Ambiguous Queries Requiring Clarification

| Query | Issue | Missing Information | Resolution |
|-------|-------|---------------------|------------|
| "Analyze this image." | Too vague | What aspect? (objects, changes, classification, description?) | Default to General VLM; prompt for specificity if needed |
| "Compare these." | Unclear what to compare | Which images? What attributes? | Require at least 2 images; default to general comparison |
| "Where are the objects?" | Undefined object type | What objects? (buildings, roads, vehicles, water?) | Default to prominent objects; prompt for object class |
| "Tell me what changed." | Temporal ambiguity | Which time periods? What type of change? | Require 2+ images; default to any detectable change |
| "Find buildings and tell me how many." | Compound query | Single task or multiple? | Split into Detection + Counting (same task family) |
| "Where are the new buildings?" | Requires temporal context | New compared to what? | Require 2+ temporal images; map to Change Detection + Grounding |
| "Compare optical and SAR and explain the difference." | Complex cross-modality | What aspect to compare? (features, coverage, quality?) | Map to Cross-Modality Comparison + Explanation |

---

## Mapping Rules (Draft)

| Condition | Task Category | Specific Capability |
|-----------|---------------|---------------------|
| User requests object location (where, show, point to) | Spatial Object Analysis | Visual Grounding |
| User requests object detection (find, identify, what objects) | Spatial Object Analysis | Object Detection |
| User requests counting (how many, count) | Spatial Object Analysis | Counting |
| User requests classification (classify, what type) | Satellite Image Understanding | Classification |
| User requests general description (describe, what is, analyze) | General VLM | Image Understanding / Captioning |
| Multiple observations required (2+ images) | Multi-Observation Analysis | Comparison / Change Detection |
| User asks about temporal differences (changed, between dates, new) | Multi-Observation Analysis | Change Analysis |
| User explicitly requests optical/SAR comparison | Multi-Observation Analysis | Modality-Specific or Cross-Modality Comparison |
| Flood/water analysis requested (flooded, water bodies) | Geospatial / Environmental Analysis | Flood/Water Detection |
| Compound queries (find + count, where + what) | Spatial Object Analysis | Combined Capabilities (Detection + Counting + Grounding) |

---

## Next Steps

1. Review edge cases with team
2. Refine mapping rules based on ambiguous scenarios
3. Validate Structured Query can capture all required information
4. Implement mapper only after rules are stable

---

## Status : FINALIZED**