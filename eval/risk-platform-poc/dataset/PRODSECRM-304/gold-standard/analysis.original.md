---
jira_key: "PRODSECRM-304"
title: "HuggingFace IBM Granite External Model Reference"
status: draft
severity: "Medium"
likelihood: "Unlikely"
impact: "Moderate"
created: "2026-09-02"
updated: "2026-09-03"
analyst: "Aleksandra Haklik"
session_id: "2026-09-02-125403"
adversarial_mode: pending
adversarial_disposition: pending
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-03)"
    added: "2026-09-03"
---

# Risk Assessment: PRODSECRM-304

## Executive Summary [AI-GENERATED]

The Offline Knowledge Portal (OKP) is requesting a supply chain exception to consume IBM Granite embedding model artifacts from HuggingFace at build time, without validated integrity controls — if that model were compromised upstream, OKP would serve manipulated search results to customers with no detection mechanism in place. Severity is rated **Medium** / **Unlikely** / **Moderate**: the target model (`ibm-granite/granite-embedding-30m-english`, 30M parameters, safetensors format) has a bounded threat surface, but the approval process has structural governance gaps — no draft EC Policy YAML attached, no SHA256 pinning, a circular remediation relationship with [PRODSECRM-227](https://redhat.atlassian.net/browse/PRODSECRM-227) (whose 60-day deadline expires 2026-09-06), and scanning controls assumed from the RHEL AI precedent are documented as incomplete in [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118). Recommended treatment is **conditional acceptance** with prerequisites: draft EC Policy with repo-level + sha256 pinning, documented compensating controls for scanning gaps, and cross-reference to -227/226 remediation status.

---

## Section 1: Risk Identification [AI-GENERATED]

**Maps to:** JIRA Summary, Description

| Field | Value |
|-------|-------|
| Risk Type | Supply Chain / Process |
| Title | External HuggingFace model artifact consumption without validated supply chain controls |
| Description | OKP requires an Enterprise Contract Policy derived from `registry-standard` with an `allowed_external_references` allowance for IBM Granite embedding model artifacts on HuggingFace. The approval process has governance gaps: no reviewable policy artifact, no artifact pinning, incomplete scanning coverage, and an unacknowledged circular remediation relationship with a prior exception. |

**Context:**

This risk was filed by Paula Wambui on 2026-09-02 as [PRODSECRM-304](https://redhat.atlassian.net/browse/PRODSECRM-304), with no assignee. It is a Supply Chain Exception for the Offline Knowledge Portal (OKP), a product within Portfolio and Delivery (PnD). The approving VP is bwalker@redhat.com, with an exception expiration of 2027-03-02. Additional watchers: mclayton, jowhite, jsprague.

The exception request references the existing RHEL AI Enterprise Contract Policy, which already allows the `ibm-granite` HuggingFace organization via `allowed_external_references`, but that approval is scoped to the RHEL AI release pipeline only. OKP requires its own policy.

**Related issues:**
- [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) ("Manifesting Models", In Progress, High/Likely/Major) — the parent risk for model supply chain. Documents that the model scanning pipeline (Snyk, ClamAV, Clair) has known coverage gaps. AIBOM work is unowned.
- [PRODSECRM-227](https://redhat.atlassian.net/browse/PRODSECRM-227) ("EC exception for Embedding models", Closed as Duplicate → [PRODSECRM-226](https://redhat.atlassian.net/browse/PRODSECRM-226)) — OCP Lightspeed's exception for the same `ibm-granite` embedding models. Its remediation plan stated: "internalization of embedding model by OKP will allow drop off of the embedding model dependency from OLS side." -304 is the OKP side of that same dependency, now requesting its own exception.
- [PRODSECRM-269](https://redhat.atlassian.net/browse/PRODSECRM-269) ("OKP Solr CVE Exception", Resolved) — prior OKP exception with the same approving VP (bwalker@redhat.com). Labels: `product:offline-knowledge-portal`, `bu:middleware`.
- RHOKP-1744: Validated target model as `ibm-granite/granite-embedding-30m-english`.
- RHOKP-1681: Planned migration to `granite-embedding-small-english-r2`.
- RHOKP-1801/1799: ProdSec/Konflux process work (due 2026-09-18).

### Supplementary Intelligence Sources [HUMAN]

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| Analyst research | Target model: ibm-granite/granite-embedding-30m-english (validated in RHOKP-1744); planned migration to granite-embedding-small-english-r2 (RHOKP-1681); differs from RHEL AI OGX precedent (granite-embedding-125m-english). No Konflux lock file or draft EC policy MR attached. | RHOKP-1744, RHOKP-1681, RHOKP-1801, RHOKP-1799, PRODSECRM-227 |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | Medium | Bounded model threat (30M-param safetensors, no executable code); governance gaps are procedural, not catastrophic; single-product blast radius |
| Likelihood | Unlikely | IBM Granite is a trusted, high-profile org on HuggingFace; safetensors format eliminates pickle deserialization; model is small (<2GB, scanning gaps don't apply at this size) |
| Impact | Moderate | OKP is a single product; compromised embedding model would degrade search quality or manipulate retrieval results for OKP users; no cross-product contamination |

### Rating Rationale

**Severity justification:**

Medium because: (a) the target model is small (30M parameters, ~120MB safetensors), from a trusted IBM-maintained HuggingFace organization, in a format specifically designed to prevent code execution; (b) the blast radius is limited to a single product (OKP); (c) the governance gaps — while real — are procedural issues that can be resolved before or as conditions of approval, not fundamental architectural flaws.

The severity would escalate to High if: the EC Policy is approved at org-level (allowing any model in `ibm-granite`, including future models with code), the model format changes from safetensors to include executable code (Python config files), or if OKP's embedding model feeds into a security-critical decision path (e.g., access control, content filtering).

**Likelihood justification:**

Unlikely because: (a) IBM maintains the `ibm-granite` HuggingFace organization — it is a large, well-resourced corporate actor with reputational incentive to secure its model repos; (b) the safetensors format eliminates the most common model-layer attack vector (pickle deserialization); (c) the model is small enough for existing scanning tools (ClamAV <2GB) to process. The likelihood would increase if: HuggingFace model repos gained broader attack surface (platform-level compromise), the EC Policy does not pin to a specific commit/sha256 (allowing silent model replacement), or the `ibm-granite` org scope is broader than necessary.

**Impact justification:**

Moderate because: (a) a compromised embedding model in OKP would degrade or manipulate retrieval-augmented generation results — customers would receive incorrect or manipulated search responses from the knowledge portal; (b) there is no cross-product contamination — OKP's EC Policy is isolated from RHEL AI's policy; (c) the Offline Knowledge Portal is an enterprise product with a bounded user base. The impact would escalate if: OKP's embedding outputs feed into other products or services, or if the knowledge portal serves security-relevant content where manipulation could cause material harm.

### CVE Landscape

No CVE associations identified for this specific model. However, [CVE-2024-11394](https://nvd.nist.gov/vuln/detail/CVE-2024-11394) (HuggingFace `transformers` library vulnerability) is relevant context — it demonstrates that HuggingFace model artifacts can contain exploitable code. This CVE does not apply to safetensors-format models but applies to models with Python code files.

**Data Source:** Manual analysis. CVE-2024-11394 referenced in [PRODSECRM-118 comments](https://redhat.atlassian.net/browse/PRODSECRM-118) (Przemyslaw Roguski, Apr 2025).

---

## Section 3: Objective Alignment [AI-GENERATED]

**Maps to:** Risk Council governance model — 7 risk objectives

| # | Objective | Affected? | Explanation |
|---|-----------|-----------|-------------|
| 1 | Product availability | No | The exception enables OKP functionality; denying it blocks the product. The risk itself does not affect availability. |
| 2 | Customer trust | Yes | Shipping externally-sourced AI model artifacts without validated integrity controls could undermine customer confidence if a supply chain compromise is discovered. |
| 3 | Regulatory compliance | No | No direct regulatory trigger. CRA supply chain obligations are contextual (analyst override declined — no frameworks loaded). |
| 4 | Revenue / cost | No | No direct revenue impact from the exception itself. |
| 5 | Strategic roadmap | Yes | OKP is positioned as the successor to OLS's RAG component (per PRODSECRM-227 remediation plan). If OKP's supply chain controls are inadequate, the strategic migration from OLS to OKP inherits the same supply chain risk rather than resolving it. |
| 6 | Product integrity | Yes | An externally-sourced embedding model is a component of OKP's output quality. If the model is compromised or manipulated, OKP's search results are unreliable. |
| 7 | Safety, privacy, and data integrity | No | No direct safety or privacy implications for an embedding model used in document retrieval. |

**Primary objective:** Product integrity — the embedding model directly determines the quality and trustworthiness of OKP's retrieval results.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| Enterprise Contract Policy framework (Konflux) | Preventive | Effective (framework-level) | EC policies enforce supply chain compliance at build time. However, no draft policy exists for -304 yet — the control framework exists but the specific policy has not been written. |
| RHEL AI `allowed_external_references` precedent | Preventive | Partially Effective | The RHEL AI policy allows `ibm-granite` org, establishing organizational trust. But the scanning pipeline behind this approval has documented gaps per [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118): Snyk scans pipeline files not model files (bug), ClamAV fails on >2GB files, Clair times out on large downloads. |
| Safetensors format | Preventive | Effective (for code execution) | Safetensors eliminates pickle deserialization attacks. Does NOT protect against model weight manipulation or upstream repo compromise. |
| VP approval gate | Detective | Partially Effective | VP approval (bwalker@redhat.com) is required. However, no reviewable artifact (draft EC Policy YAML) is attached for the VP to evaluate — the approval is for the concept, not the implementation. |
| Exception expiration (2027-03-02) | Corrective | Effective (time-bounded) | The exception has a fixed expiration. However, prior OKP exception (-269) was also time-bounded and resolved without documented follow-through on remediation. |

### Residual Exposure

1. **No draft EC Policy to review.** The approval is being requested without the technical artifact (EC Policy YAML) being available for security review. Neither the VP nor ProdSec can evaluate the actual scope of the allowance (org-level vs. repo-level, pinned vs. unpinned).

2. **No SHA256/commit pinning.** Without pinning to a specific model version, a compromised upstream model would be silently consumed at the next build. The RHEL AI precedent uses org-level allowance, not commit-level pinning.

3. **Circular remediation with -227.** The remediation for OLS's embedding model exception (-227) was "OKP will internalize." OKP is now requesting its own external exception for the same model. The internalization path exists (RHOKP-1681 migration to `granite-embedding-small-english-r2`) but the relationship is not acknowledged in -304.

4. **-226/227 remediation deadline expiring.** The 60-day remediation deadline set by Ian Murphy on -226/227 is 2026-09-06 — 3 days from this assessment. If the OKP internalization was the expected resolution, that deadline appears unmet.

5. **Scanning coverage gap for model content.** While the 30M-parameter model is below the 2GB ClamAV threshold, the Snyk bug (scanning pipeline files instead of model files) means no actual vulnerability scanning occurs on the model content in the current Konflux pipeline.

6. **Process work trails the exception.** RHOKP-1801/1799 (ProdSec/Konflux process work) is due 2026-09-18. The exception may need to ship before process controls are in place, creating a 2-week window with no process framework.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0–7 days)

- [ ] **Produce draft EC Policy YAML** — **Owner:** OKP team (Paula Wambui / mclayton) — **Definition of done:** EC Policy derived from `registry-standard` with: (a) repo-level scope (`ibm-granite/granite-embedding-30m-english`, not org-level), (b) SHA256 pinning to a specific commit hash, (c) safetensors-only file allowance (exclude `.py`, `.pkl`, `.bin` files). MR submitted to `konflux-release-data`.
- [ ] **Cross-reference -227/226 remediation status** — **Owner:** OKP team / ProdSec (Ian Murphy) — **Definition of done:** Documented status of the -226/227 60-day remediation (deadline 2026-09-06). If the remediation was OKP internalization, explain how -304 relates to that path. If the remediation has been re-scoped, update -226.

### Short-Term (1–4 weeks)

- [ ] **Document compensating controls for scanning gaps** — **Owner:** OKP team + PSAI — **Definition of done:** Written statement of which scanning controls apply to this model at build time, given [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) documented gaps. ClamAV covers this model (<2GB); confirm Snyk bug status; confirm whether Garak scanning applies to embedding models.
- [ ] **Complete RHOKP-1801/1799 process work** — **Owner:** OKP team / ProdSec — **Definition of done:** ProdSec/Konflux process framework in place (due 2026-09-18). EC Policy approved only after process framework is operational.
- [ ] **Add 90-day review checkpoint** — **Owner:** ProdSec — **Definition of done:** Calendar reminder for 2026-12-01 review of this exception. Evaluate: has internalization (RHOKP-1681) progressed? Is the external reference still needed? Is the model still the same version?

### Long-Term (1–3 months)

- [ ] **Complete internalization migration** — **Owner:** OKP team — **Definition of done:** OKP consumes embedding model from an internally controlled artifact source (not HuggingFace at build time). RHOKP-1681 (`granite-embedding-small-english-r2` migration) completed. Exception no longer required.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Draft EC Policy YAML | OKP team | Produce and submit for review before VP approval | High |
| -226/227 remediation status | ProdSec / OKP team | Clarify whether 2026-09-06 deadline was met and how -304 relates | High |
| Snyk scanning bug status | PSAI / Konflux | Confirm whether the Snyk bug (scanning pipeline files not model files) has been fixed since Apr 2026 | Medium |
| Model version tracking | OKP team | Document which model version/commit OKP is currently consuming and whether it will change | Medium |

### Conditional Acceptance Prerequisites

| Prerequisite | Status | Evidence Required | Owner |
|-------------|--------|-------------------|-------|
| Draft EC Policy YAML with repo-level + sha256 pinning | Not Met | MR to konflux-release-data | OKP team |
| -227/226 remediation status documented | Not Met | Comment on -226 or -304 clarifying relationship | ProdSec / OKP team |
| Compensating controls for PRODSECRM-118 scanning gaps documented | Not Met | Written statement of applicable scanning controls | OKP team + PSAI |

**Acceptance blocked until:** All three prerequisites show "Met" status, or the approving VP (bwalker@redhat.com) explicitly waives a prerequisite with documented rationale.

---

## Section 6: Escalation Analysis [AI-GENERATED]

**Maps to:** PSRR issue creation, PRODSECRM-to-PSRR link

### PSRR Promotion Assessment

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk (concrete numbers) | Partial | Model size quantified (30M params, ~120MB). Impact not financially quantified. |
| 2 | Actionable path (systemic fix) | Yes | Internalization via RHOKP-1681; EC Policy with pinning as interim control |
| 3 | Context provided (summary + recommendation) | Yes | This assessment; PRODSECRM-118 and -227 context |
| 4 | Tied to an objective | Yes | Product integrity |
| 5 | Named accountable risk owner (director+) | No | No assignee on -304; VP approval requested but no risk owner named |
| 6 | Consequence of inaction (6–12 month degradation) | Partial | Pattern of exceptions without controls could normalize; PRODSECRM-118 scanning gaps persist |
| 7 | Risk posture requested | Yes | Conditional acceptance with prerequisites |
| 8 | Acceptance timebox | Yes | Exception expires 2027-03-02; 90-day review checkpoint recommended |

**Promotion recommendation:** NOT WARRANTED

**Rationale:** This is a Medium-severity, single-product supply chain exception with bounded blast radius. The governance gaps are real but procedural — they can be resolved through conditional acceptance prerequisites without executive escalation. The parent risk ([PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118), High/Likely/Major) is the appropriate escalation vehicle for the systemic model supply chain problem. -304 is a symptom, not the root cause.

---

## Analyst Assessment [HUMAN]

**Action:** {CONCUR | MODIFY | OVERRIDE | DEFER}

**Changes from AI recommendation:**
{To be completed by analyst}

**Rationale for overrides:**
{Required if action is OVERRIDE}

**Sign-off:** {Analyst name} | {Date}

---

## Supporting Evidence

| File | Description | Date Added |
|------|-------------|------------|
| intelligence.json | JIRA graph traversal: 1 issue, 0 comments, 0 URLs (depth 0) | 2026-09-02 |

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-304 (primary risk) | JIRA | [PRODSECRM-304](https://redhat.atlassian.net/browse/PRODSECRM-304) | Yes |
| 2 | PRODSECRM-118 (Manifesting Models — parent risk) | JIRA | [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) | Yes |
| 3 | PRODSECRM-227 (EC exception for Embedding models — Closed as Duplicate) | JIRA | [PRODSECRM-227](https://redhat.atlassian.net/browse/PRODSECRM-227) | Yes |
| 4 | PRODSECRM-226 (EC exception for Hermetic Building — In Progress) | JIRA | [PRODSECRM-226](https://redhat.atlassian.net/browse/PRODSECRM-226) | Yes |
| 5 | PRODSECRM-269 (OKP Solr CVE Exception — Resolved) | JIRA | [PRODSECRM-269](https://redhat.atlassian.net/browse/PRODSECRM-269) | Yes |
| 6 | CVE-2024-11394 (HuggingFace transformers vulnerability) | CVE | [CVE-2024-11394](https://nvd.nist.gov/vuln/detail/CVE-2024-11394) | Yes |
| 7 | RHOKP-1744 (target model validation) | JIRA | [RHOKP-1744](https://redhat.atlassian.net/browse/RHOKP-1744) | Unverified |
| 8 | RHOKP-1681 (migration to granite-embedding-small-english-r2) | JIRA | [RHOKP-1681](https://redhat.atlassian.net/browse/RHOKP-1681) | Unverified |
| 9 | RHOKP-1801 (ProdSec/Konflux process work) | JIRA | [RHOKP-1801](https://redhat.atlassian.net/browse/RHOKP-1801) | Unverified |
| 10 | RHOKP-1799 (ProdSec/Konflux process work) | JIRA | [RHOKP-1799](https://redhat.atlassian.net/browse/RHOKP-1799) | Unverified |
