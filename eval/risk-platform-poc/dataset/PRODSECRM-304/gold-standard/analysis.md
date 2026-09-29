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
adversarial_mode: "full (escalated from garth)"
adversarial_disposition: "MAX ROUNDS"
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-03)"
    added: "2026-09-03"
---

# Risk Assessment: PRODSECRM-304

## Executive Summary [AI-GENERATED]

The Offline Knowledge Portal (OKP) is requesting a supply chain exception to consume IBM Granite embedding model artifacts from HuggingFace at build time without validated integrity controls, creating a risk of shipping a compromised AI model to customers — if that model's weights were manipulated upstream, OKP would serve retrieval results steered by an attacker-chosen embedding space with no detection mechanism, causing customers to act on incorrect product information and potentially resulting in loss of customer trust in OKP's knowledge portal outputs [UNRESOLVED: if OKP serves security-relevant content such as vulnerability remediation guidance, impact escalates — customers could follow incorrect security guidance, leading to unpatched or misconfigured systems]. Severity is rated **High** / **Unlikely** / **Moderate** (upgraded from Medium during adversarial review): the approval process compounds a stalled remediation (the -227 internalization commitment remains in "To Do" status on [RHOKP-1681](https://redhat.atlassian.net/browse/RHOKP-1681), verified 2026-09-03), non-functional model content scanning (Snyk bug confirmed current April 2026 per [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) comments), no reviewable technical artifact (missing EC Policy YAML), no SHA256 pinning, and a primary threat model (embedding weight poisoning) that bypasses the cited safetensors mitigant. Recommended treatment is **conditional acceptance** with prerequisites: draft EC Policy with repo-level + sha256 pinning, documented compensating controls for scanning gaps, and resolution of the orphaned -227 internalization tracking.

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
- [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) ("Manifesting Models", In Progress, assigned to Garth Mollett, rated High/Likely/Major by Ian Murphy July 2026, PSRR escalation recommended) — the parent risk for model supply chain. Scanning pipeline gaps **confirmed current as of April 2026** (Emily Fox comment 2026-04-28, quoting Florencio): Snyk scans pipeline files not model files (bug), ClamAV fails on files >2GB, Clair times out on large downloads. Garak scanning was being added "in phase one not via konflux" as of April 2026. AIBOM work is **unowned** — prior technical leads moved off the work, all three tracking tickets (ISV-6781, ISV-6518, ISV-6782) remain unassigned per Ian Murphy's July 2026 assessment.
- [PRODSECRM-227](https://redhat.atlassian.net/browse/PRODSECRM-227) ("EC exception for Embedding models", Closed as Duplicate → [PRODSECRM-226](https://redhat.atlassian.net/browse/PRODSECRM-226)) — OCP Lightspeed's exception for the same `ibm-granite` embedding models. Its description states (verified via JIRA MCP 2026-09-03): "Long term - internalization of embedding model by OKP will allow drop off of the embedding model dependency from OLS side." -304 is the OKP side of that same dependency, now requesting its own exception instead of internalizing. **Critical finding from adversarial review:** -226 is "EC exception required for: Hermetic Building" — a completely different exception type (binary Python package wheels for torch/numpy/scipy/Rust extensions, Product: OCP Lightspeed, VP: scuppett@redhat.com). -227 was closed as Duplicate of an unrelated ticket. The embedding model internalization remediation tracking is orphaned — no open ticket tracks this commitment.
- [PRODSECRM-269](https://redhat.atlassian.net/browse/PRODSECRM-269) ("OKP Solr CVE Exception Request", Resolved) — prior OKP supply chain exception with the same approving VP (bwalker@redhat.com). Remediation plan was to upgrade when upstream Apache Solr patches become available (verified via JIRA MCP 2026-09-03). Exception expiration 2026-10-31. Resolved status suggests remediation path was followed.
- RHOKP-1744: Validated target model as `ibm-granite/granite-embedding-30m-english`.
- [RHOKP-1681](https://redhat.atlassian.net/browse/RHOKP-1681) ("Larger chunk size granite embedding model for OKP RAG", **Status: To Do**, assigned to Jared Sprague, updated 2026-08-31) — the internalization migration path. This is the ticket that would resolve the -227 remediation commitment. It has not started (verified via JIRA MCP 2026-09-03).
- RHOKP-1801/1799: ProdSec/Konflux process work (due 2026-09-18).

### Supplementary Intelligence Sources [HUMAN]

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| Analyst research | Target model: ibm-granite/granite-embedding-30m-english (validated in RHOKP-1744); planned migration to granite-embedding-small-english-r2 (RHOKP-1681); differs from RHEL AI OGX precedent (granite-embedding-125m-english). No Konflux lock file or draft EC policy MR attached. | RHOKP-1744, RHOKP-1681, RHOKP-1801, RHOKP-1799, PRODSECRM-227 |
| JIRA comment (Michael Clayton, 2026-09-03) | Dual-source architecture planned: RHOKP team-controlled S3 bucket (primary) + HuggingFace (fallback for rate-limit/outage resilience). Mirrors RHEL AI pattern. S3 prefetch is a compensating control (team controls artifact source). Product deliverable is an MCP server. EC Policy must cover both sources. Does not resolve content domain question. | PRODSECRM-304 comment 18293920 |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | High | Failed prior remediation (-227 internalization did not occur); no technical artifact (EC Policy YAML) for review; scanning controls documented as non-functional for model content (Snyk bug); org-level scope risk without repo-level pinning; weight-poisoning threat bypasses cited safetensors mitigant |
| Likelihood | Unlikely | IBM Granite is a trusted, high-profile org on HuggingFace; safetensors format eliminates pickle deserialization (but does NOT mitigate weight manipulation); model is small (<2GB, ClamAV can process — but ClamAV applicability to model content unverified) |
| Impact | Moderate | OKP is a single product; compromised embedding model would degrade search quality or manipulate retrieval results for OKP users; no cross-product contamination [UNRESOLVED: OKP content domain not established — impact could escalate to Major if OKP serves security-relevant content] |

### Rating Rationale

**Severity justification:**

High because: (a) the -227 internalization remediation has not started — [RHOKP-1681](https://redhat.atlassian.net/browse/RHOKP-1681) ("Larger chunk size granite embedding model for OKP RAG") is in **"To Do" status** (verified via JIRA MCP 2026-09-03, assigned to Jared Sprague, last updated 2026-08-31). The remediation commitment is tracked in the product backlog. Note: the 2026-08-31 update (2 days before -304 was filed) could indicate active triage or planning rather than abandonment — the "To Do" status indicates work has not started but does not preclude near-term scheduling. Meanwhile, -227 was Closed as Duplicate of -226 (an unrelated hermetic building exception) — whether this was a JIRA housekeeping error or a deliberate close, the effect is that the PRODSECRM-level tracking of the embedding model internalization is lost; (b) no draft EC Policy YAML exists for security review — the VP approval gate is evaluating a concept, not a technical artifact. Note: the risk was filed 2026-09-02 and assessed the same day; the absence of a policy on day one is expected process sequencing, but the assessment rates the current state, not the expected future state; (c) scanning controls documented in [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) are **confirmed non-functional for model content as of April 2026** (Emily Fox comment 2026-04-28, quoting Florencio): Snyk scans pipeline files not model files (bug still present), ClamAV fails on >2GB files, Clair times out on large downloads. Ian Murphy's own July 2026 assessment of -118 rated it High/Likely/Major with PSRR escalation recommended. AIBOM work is unowned; (d) without repo-level pinning, the exception could inherit org-level scope (all models in `ibm-granite`), silently allowing future models with executable code files — this is a risk of the hypothetical worst-case policy design, not a confirmed policy; (e) the primary threat model for embedding models is weight manipulation (shifting vector space distances to produce manipulated retrieval results), and the cited safetensors mitigant addresses code execution only, not weight poisoning — this threat is theoretical with no documented incidents of small embedding model poisoning in the wild, but it is structurally uncontrolled.

**Factor classification (standalone vs. inherited):**
- **Standalone factors (specific to -304):** (a) stalled internalization remediation — confirmed; (b) missing EC Policy YAML — confirmed but expected on day one (process context, not standalone governance failure); (d) org-level scope risk — speculative; (e) weight poisoning threat — theoretical.
- **Inherited factor (systemic, captured by -118):** (c) scanning pipeline gaps — confirmed current but systemic across all model consumption at Red Hat. Already rated High/Likely/Major on -118 with PSRR escalation recommended. Including this as a -304 severity driver risks double-counting.

**Risk matrix tension:** The component ratings are High severity / Unlikely likelihood / Moderate impact. In standard risk matrix frameworks, Unlikely x Moderate typically maps to Medium overall risk. The High severity rating reflects the cumulative governance pattern (stalled remediation + missing artifact + systemic scanning gaps + uncontrolled threat vector) rather than any single factor. The analyst should assess whether the standalone factors alone justify High or whether Medium with -118 as aggravating context is more accurate.

Upgraded from Medium during adversarial review (Garth single-pass escalation). Scanning gap evidence verified from PRODSECRM-118 comments (April 2026, 5 months old — last verified status before this assessment).

**Likelihood justification:**

Unlikely because: (a) IBM maintains the `ibm-granite` HuggingFace organization — it is a large, well-resourced corporate actor with reputational incentive to secure its model repos; (b) the safetensors format eliminates pickle deserialization attacks (the most common model-layer code execution vector); (c) the target model is small (30M parameters) and low-profile, making it an unlikely target for sophisticated supply chain attacks compared to high-download LLMs; (d) weight poisoning of an embedding model requires attacker knowledge of the downstream retrieval application to produce meaningful manipulation, raising the attacker sophistication threshold.

**Uncontrolled threat vector (weight manipulation):** Safetensors does NOT mitigate weight manipulation — a poisoned embedding model shifts vector space distances to produce manipulated retrieval results without executing any code. No cited control currently addresses this threat. The likelihood rating of Unlikely reflects the low target profile and high attacker sophistication requirement, not the adequacy of controls. This is an accepted gap: if SHA256 pinning is implemented (recommended), it would detect unauthorized weight changes at build time, partially addressing this vector. Without pinning, the threat is structurally uncontrolled.

**HuggingFace platform risk (not assessed):** The likelihood assessment focuses on IBM's intent and reputation but does not assess the platform-level attack surface of HuggingFace model hosting. HuggingFace has had documented security incidents (API token exposures). A platform-level compromise or IBM account compromise could enable model replacement regardless of IBM's own security posture. Without SHA256 pinning, this is a silent replacement risk. This is a known gap in the likelihood assessment.

The likelihood would increase to Possible if: HuggingFace platform-level model integrity incidents are documented, the EC Policy does not pin to a specific commit/sha256, or the `ibm-granite` org scope is broader than necessary.

**Impact justification:**

Moderate because: (a) a compromised embedding model in OKP would degrade or manipulate retrieval-augmented generation results — customers would receive incorrect or manipulated search responses from the knowledge portal; (b) OKP's EC Policy is isolated from RHEL AI's policy at the policy level (no cross-policy contamination); (c) OKP is described as a single enterprise product in the exception filing.

**Unsourced assumptions (flagged during adversarial review):** The assertions that OKP has "a bounded user base" and "no cross-product contamination" are inferred from the exception filing description, not verified with the OKP team. Whether OKP's retrieval results or embedding outputs are consumed via API by other products or services has not been investigated. The absence of components and labels on PRODSECRM-304 provides no information about OKP's integration surface.

The impact would escalate to Major if: (a) OKP serves security-relevant content (vulnerability remediation, hardening instructions) where manipulated retrieval could cause customers to follow incorrect security guidance [UNRESOLVED: OKP content domain not established]; or (b) OKP's embedding outputs are consumed by downstream services, expanding the blast radius beyond a single product [UNRESOLVED: OKP architecture and downstream consumers not verified].

### CVE Landscape

No CVE associations identified for this specific model. [CVE-2024-11394](https://nvd.nist.gov/vuln/detail/CVE-2024-11394) (HuggingFace `transformers` library vulnerability) is included as background context only — it demonstrates that HuggingFace model artifacts can contain exploitable code via Python files. **This CVE does not apply to safetensors-format models** and is not a direct threat to the target model. Its relevance is limited to demonstrating the broader HuggingFace attack surface for models that include executable code files (which the EC Policy should exclude via safetensors-only file allowance).

**Data Source:** CVE-2024-11394 referenced in [PRODSECRM-118 comments](https://redhat.atlassian.net/browse/PRODSECRM-118) (attributed to Przemyslaw Roguski, Apr 2025 — comment-level permalink not available; issue-level link only).

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
| 7 | Safety, privacy, and data integrity | [UNRESOLVED: content domain dependent] | If OKP serves security-relevant content (vulnerability remediation guidance, hardening instructions), manipulated retrieval results could cause customers to follow incorrect security guidance — an indirect safety implication. Determination requires establishing OKP's content domain. |

**Primary objective:** Product integrity — the embedding model directly determines the quality and trustworthiness of OKP's retrieval results.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| Enterprise Contract Policy framework (Konflux) | Preventive | Effective (framework-level) | EC policies enforce supply chain compliance at build time. However, no draft policy exists for -304 yet — the control framework exists but the specific policy has not been written. |
| RHEL AI `allowed_external_references` precedent | Preventive | Partially Effective | The RHEL AI policy allows `ibm-granite` org, establishing organizational trust. But the scanning pipeline behind this approval has **confirmed gaps as of April 2026** per [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) (Emily Fox comment 2026-04-28, quoting Florencio): Snyk scans pipeline files not model files (bug), ClamAV fails on >2GB files, Clair times out on large downloads. Garak scanning being added "in phase one not via konflux." Whether RHEL AI's approval included controls (SHA256 pinning, repo-level scoping) that -304 should match is not assessed. |
| Safetensors format | Preventive | Effective (for code execution) | Safetensors eliminates pickle deserialization attacks. Does NOT protect against model weight manipulation or upstream repo compromise. |
| VP approval gate | Detective | Partially Effective | VP approval (bwalker@redhat.com) is required. However, no reviewable artifact (draft EC Policy YAML) is attached for the VP to evaluate — the approval is for the concept, not the implementation. |
| Exception expiration (2027-03-02) | Corrective | Effective (time-bounded) | The exception has a fixed expiration (2027-03-02). Prior OKP exception (-269, Solr CVE) was also time-bounded (expiration 2026-10-31) and is now Resolved — its remediation plan (upgrade when upstream patches available) appears to have been followed. |

### Residual Exposure

1. **No draft EC Policy to review.** The approval is being requested without the technical artifact (EC Policy YAML) being available for security review. Neither the VP nor ProdSec can evaluate the actual scope of the allowance (org-level vs. repo-level, pinned vs. unpinned).

2. **No SHA256/commit pinning.** Without pinning to a specific model version, a compromised upstream model would be silently consumed at the next build. The RHEL AI precedent uses org-level allowance, not commit-level pinning.

3. **Circular remediation with orphaned tracking.** The remediation for OLS's embedding model exception (-227) was "internalization of embedding model by OKP will allow drop off of the embedding model dependency from OLS side" (verified from JIRA description, 2026-09-03). OKP is now requesting its own external exception for the same model instead of internalizing. **Adversarial review finding:** -227 was Closed as Duplicate of [PRODSECRM-226](https://redhat.atlassian.net/browse/PRODSECRM-226), but -226 is "EC exception required for: Hermetic Building" — a completely different exception type (binary Python package wheels for OLS, assigned to Anna Syed, VP: scuppett@redhat.com). The embedding model internalization remediation commitment is on a Closed ticket duplicated to an unrelated ticket. No open issue tracks this commitment.

4. **-226/227 remediation deadline context.** The 60-day remediation deadline referenced in the original analysis (attributed to Ian Murphy on -226/227, deadline 2026-09-06) needs verification: given that -226 is about hermetic building (not embedding models), the deadline may apply to -226's remediation scope, not to the -227 embedding model internalization. The deadline provenance is unverified from comments.

5. **Scanning coverage gap for model content (confirmed April 2026).** While the 30M-parameter model is below the 2GB ClamAV threshold, the Snyk bug (scanning pipeline files instead of model files) means no actual vulnerability scanning occurs on the model content in the current Konflux pipeline. This is confirmed current as of April 2026 per Emily Fox comment on -118 (quoting Florencio). ClamAV may cover this model (<2GB), but ClamAV scans for malware signatures, not model weight integrity. Garak scanning (for LLM behavioral vulnerabilities) was being added in phase one outside of Konflux.

6. **Process work trails the exception.** RHOKP-1801/1799 (ProdSec/Konflux process work) is due 2026-09-18. The exception may need to ship before process controls are in place, creating a 2-week window with no process framework.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0–7 days)

- [ ] **Produce draft EC Policy YAML** — **Owner:** OKP team (Paula Wambui is the reporter; actual technical lead and owner to be confirmed by OKP team — ownership is preliminary) — **Definition of done:** EC Policy derived from `registry-standard` with: (a) repo-level scope (`ibm-granite/granite-embedding-30m-english`, not org-level), (b) SHA256 pinning to a specific commit hash, (c) safetensors-only file allowance (exclude `.py`, `.pkl`, `.bin` files). MR submitted to `konflux-release-data`.
- [ ] **Resolve orphaned remediation tracking** — **Owner:** ProdSec (Ian Murphy is the -118 risk area lead; confirm he is the appropriate owner for OKP exceptions — ownership is preliminary) — **Definition of done:** The -227 embedding model internalization commitment ("internalization of embedding model by OKP will allow drop off of the embedding model dependency from OLS side") is on a Closed ticket that was duplicated to -226, an unrelated hermetic building exception. This remediation commitment is orphaned. Create or reopen a tracking issue for the internalization path. Document how -304 relates to the -227 remediation.

### Short-Term (1–4 weeks)

- [ ] **Document compensating controls for scanning gaps** — **Owner:** OKP team + PSAI — **Definition of done:** Written statement of which scanning controls apply to this model at build time, given [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) documented gaps. ClamAV covers this model (<2GB); confirm Snyk bug status; confirm whether Garak scanning applies to embedding models.
- [ ] **Complete RHOKP-1801/1799 process work** — **Owner:** OKP team / ProdSec — **Definition of done:** ProdSec/Konflux process framework in place (due 2026-09-18). EC Policy approved only after process framework is operational.
- [ ] **Add 90-day review checkpoint** — **Owner:** ProdSec — **Definition of done:** Calendar reminder for 2026-12-01 review of this exception. Evaluate: has internalization (RHOKP-1681) progressed? Is the external reference still needed? Is the model still the same version?

### Long-Term (1–3 months)

- [ ] **Complete internalization migration** — **Owner:** OKP team — **Definition of done:** OKP consumes embedding model from an internally controlled artifact source (not HuggingFace at build time). RHOKP-1681 (`granite-embedding-small-english-r2` migration) completed. Exception no longer required.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| OKP content domain | OKP team | Determine what content OKP serves — general product docs or security-relevant content (vulnerability guidance, hardening instructions). Directly affects impact rating and Objective 7 assessment. | **Critical** |
| Draft EC Policy YAML | OKP team | Produce and submit for review before VP approval | High |
| Orphaned remediation tracking | ProdSec / OKP team | -227 embedding model internalization commitment is on a Closed ticket duplicated to an unrelated issue (-226 hermetic building). Create or reopen a tracking issue. | High |
| Snyk scanning bug fix timeline | PSAI / Konflux | Snyk bug (scanning pipeline files not model files) **confirmed still present as of April 2026** (Emily Fox comment on -118). Determine fix timeline and whether Garak scanning is now operational for embedding models. | Medium |
| Model version tracking | OKP team | Document which model version/commit OKP is currently consuming and whether it will change | Medium |
| HuggingFace model repo contents | OKP team / ProdSec | Verify the `ibm-granite/granite-embedding-30m-english` repo contains only safetensors files (no `.py`, `.pkl`, `config.json` with executable code). Model size (~120MB) is asserted without source. | Medium |
| RHEL AI precedent controls | ProdSec / PSAI | Assess whether RHEL AI's `allowed_external_references` approval includes controls that -304 lacks (SHA256 pinning, repo-level scoping, scanning verification). If RHEL AI also lacks these controls, the gap is systemic. If RHEL AI has them, they establish the standard for OKP. | Medium |
| OKP downstream consumers | OKP team | Confirm whether OKP's retrieval results or embedding outputs are consumed by other products/services via API. Affects blast radius assessment. | Medium |

### Conditional Acceptance Prerequisites

| Prerequisite | Status | Evidence Required | Owner |
|-------------|--------|-------------------|-------|
| Draft EC Policy YAML with repo-level + sha256 pinning | Not Met | MR to konflux-release-data | OKP team |
| Orphaned remediation tracking resolved | Not Met | Open tracking issue for -227 internalization commitment; document how -304 relates to that path | ProdSec / OKP team |
| Compensating controls for PRODSECRM-118 scanning gaps documented | Not Met | Written statement of applicable scanning controls (verify Snyk bug status — April 2025 evidence) | OKP team + PSAI |
| OKP content domain documented | Not Met | Statement of what content OKP serves and whether it includes security-relevant material | OKP team |

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

**Promotion recommendation:** NOT WARRANTED (reassess after content domain determination)

**Rationale:** Promotion is not warranted at this time because: (a) -304's standalone severity factors (stalled remediation, missing EC Policy artifact) are addressable through conditional acceptance prerequisites without executive intervention; (b) the systemic scanning gap factor is inherited from [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) (High/Likely/Major, PSRR escalation already recommended by Ian Murphy July 2026), which is the appropriate escalation vehicle for the platform-wide model supply chain problem; (c) requirement 5 (named risk owner) is unmet. **Acknowledged tension:** the severity section uses -118's scanning gaps as a factor elevating -304 to High, while this section argues -118 is the appropriate escalation vehicle rather than -304. The analyst should assess whether -304's standalone factors justify High severity independently, or whether Medium with -118 as aggravating context is more accurate. If the OKP content domain proves security-relevant (shifting impact to Major), or if -118's PSRR escalation does not proceed, promotion of -304 should be reassessed.

---

## Analyst Assessment [HUMAN]

**Action:** MODIFY

**Changes from AI recommendation:**

AI recommended High severity. Analyst changed to **Medium** because High conflates a bounded product exception (standalone factors: stalled remediation, missing EC Policy artifact) with the systemic PRODSECRM-118 program risk (scanning gaps, unowned AIBOM work). The scanning gaps are real but they are -118's problem, not -304's. -304's standalone severity is Medium: the submission is directionally sound, has RHEL AI precedent, and the target model (30M-param safetensors embedding) has a bounded threat surface. The team hasn't yet produced the EC Policy artifact or confirmed security-relevant use cases, which are governance gaps, not architectural ones.

Treatment: **Conditional acceptance** with prerequisites (unchanged from AI recommendation):
1. Draft EC Policy YAML with repo-level + sha256 pinning
2. Documented compensating controls for PRODSECRM-118 scanning gaps
3. Cross-reference to -227/226 remediation status (orphaned internalization tracking)

Impact: Moderate — **deferred pending OKP team input on content domain**. If OKP serves security-relevant content (vulnerability remediation guidance, hardening instructions), impact escalates to Major and this assessment must be amended via `/risk-amend`. OKP team (Paula Wambui, Jared Sprague) to confirm.

PSRR: NOT WARRANTED. PRODSECRM-118 is the escalation vehicle for the systemic model supply chain problem.

**Sign-off:** Aleksandra Haklik | 2026-09-04

---

## Supporting Evidence

| File | Description | Date Added |
|------|-------------|------------|
| intelligence.json | JIRA graph traversal: 1 issue, 0 comments, 0 URLs (depth 0) | 2026-09-02 |

**Evidence base warning:** The intelligence.json is critically thin (depth 0 only, no linked issues traversed, no comments extracted). Claims about PRODSECRM-118 (including 17 comments), -227, -226, -269, and RHOKP-1681 were subsequently verified via JIRA MCP during the adversarial review (2026-09-03). Scanning gap evidence on -118 is confirmed current from Emily Fox comment 2026-04-28 (quoting Florencio). RHOKP-1744, RHOKP-1801, and RHOKP-1799 remain unverified.

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-304 (primary risk) | JIRA | [PRODSECRM-304](https://redhat.atlassian.net/browse/PRODSECRM-304) | Yes |
| 2 | PRODSECRM-118 (Manifesting Models — parent risk, High/Likely/Major, PSRR escalation recommended) | JIRA | [PRODSECRM-118](https://redhat.atlassian.net/browse/PRODSECRM-118) | Yes (status, comments, and scanning gaps verified via MCP 2026-09-03; scanning bug confirmed current from Emily Fox comment 2026-04-28) |
| 3 | PRODSECRM-227 (EC exception for Embedding models — Closed as Duplicate) | JIRA | [PRODSECRM-227](https://redhat.atlassian.net/browse/PRODSECRM-227) | Yes (description verified via MCP 2026-09-03) |
| 4 | PRODSECRM-226 (EC exception for Hermetic Building — In Progress, Anna Syed) | JIRA | [PRODSECRM-226](https://redhat.atlassian.net/browse/PRODSECRM-226) | Yes (verified via MCP 2026-09-03 — different exception type from -227) |
| 5 | PRODSECRM-269 (OKP Solr CVE Exception — Resolved) | JIRA | [PRODSECRM-269](https://redhat.atlassian.net/browse/PRODSECRM-269) | Yes (description verified via MCP 2026-09-03) |
| 6 | CVE-2024-11394 (HuggingFace transformers vulnerability — background context only, does not apply to safetensors) | CVE | [CVE-2024-11394](https://nvd.nist.gov/vuln/detail/CVE-2024-11394) | Yes |
| 7 | RHOKP-1744 ("determine if sentence-transformers embeddings match tract embeddings" — Closed, Michael Clayton) | JIRA | [RHOKP-1744](https://redhat.atlassian.net/browse/RHOKP-1744) | Partial (summary does not confirm target model name; model name `ibm-granite/granite-embedding-30m-english` sourced from PRODSECRM-304 description and interactive session) |
| 8 | RHOKP-1681 (internalization migration — To Do, Jared Sprague) | JIRA | [RHOKP-1681](https://redhat.atlassian.net/browse/RHOKP-1681) | Yes (status verified via MCP 2026-09-03) |
| 9 | RHOKP-1801 (ProdSec/Konflux process work) | JIRA | [RHOKP-1801](https://redhat.atlassian.net/browse/RHOKP-1801) | Unverified |
| 10 | RHOKP-1799 (ProdSec/Konflux process work) | JIRA | [RHOKP-1799](https://redhat.atlassian.net/browse/RHOKP-1799) | Unverified |
