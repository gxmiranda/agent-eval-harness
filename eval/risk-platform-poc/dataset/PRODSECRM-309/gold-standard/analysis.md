---
template: risk-assessment-output
version: 1.0.0
jira_key: "PRODSECRM-309"
title: "RHOAI 3.6-ea.1/ea.2 Conforma exceptions: extended hermetic/RPM-signature remediation timelines + new RHAI ModelCar stage-registry base image exception"
status: draft
severity: "High"
likelihood: "Likely"
impact: "Major"
created: "2026-09-07"
updated: "2026-09-07"
analyst: "Aleksandra Haklik"
session_id: "2026-09-07-093958"
adversarial_mode: full
adversarial_disposition: EXHAUSTED
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-07)"
    added: "2026-09-07"
  - type: jira_intelligence
    label: "JIRA dependency graph (depth 3, 177 issues)"
    added: "2026-09-07"
---

# Risk Assessment: PRODSECRM-309

## Metadata

```yaml
jira_key: "PRODSECRM-309"
title: "RHOAI 3.6-ea.1/ea.2 Conforma exceptions: extended hermetic/RPM-signature remediation timelines + new RHAI ModelCar stage-registry base image exception"
status: draft
severity: "High"
likelihood: "Likely"
impact: "Major"
created: "2026-09-07"
updated: "2026-09-07"
analyst: "Aleksandra Haklik"
session_id: "2026-09-07-093958"
adversarial_mode: full
adversarial_disposition: EXHAUSTED
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-07)"
    added: "2026-09-07"
```

---

## Executive Summary [AI-GENERATED]

`PRODSECRM-309` covers a release-blocking control gap in RHOAI 3.6: three components still require temporary exceptions for hermetic-build and RPM-signature controls, while two additional components are replacing unapproved model downloads with five model images currently served from the staging registry. The preliminary rating is **High severity, Likely likelihood, and Major impact** because the violations are observed in current build evidence, the production policy merge request remains open, and failure to resolve or safely time-box the exceptions can block releases while weakening provenance and future vulnerability-remediation confidence. The most important action is to make the production exception MR and its expiration semantics an explicit release gate, with named owners and evidence for each component-level remediation path. PSRR promotion is **NOT READY** until the team quantifies affected customer/release scope, names a director-level accountable owner, and confirms whether the production policy change has been approved and applied.

---

## Section 1: Risk Identification [AI-GENERATED]

**Maps to:** JIRA Summary, Description

| Field | Value |
|-------|-------|
| Risk Type | Technical / Operational / Supply Chain / Compliance |
| Title | RHOAI 3.6 release artifacts may ship or be blocked while required build-provenance and source-integrity controls remain excepted |
| Description | RHOAI 3.6 EA1 and EA2 contain component builds that do not currently satisfy hermetic-build and approved RPM-signature controls. In parallel, modelcar packaging removes direct external model downloads for `odh-trustyai-nemo-guardrails-server` and `odh-ogx-core`, but the replacement images are sourced from `registry.stage.redhat.io`, creating a separate production-policy exception. The exposure is controlled by time-bounded Enterprise Contract policy exceptions, but the underlying remediation is distributed across AIPCC, RHOAI engineering, RHAI model validation, and release-integration work. |

**Context:**

The risk was opened on 2026-09-04 after the production policy exception work was separated from the earlier [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213) risk. The current production policy change is [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104); the JIRA task [RHOAIENG-88509](https://redhat.atlassian.net/browse/RHOAIENG-88509) is in Review, and the directly checked MR page is reachable but does not establish a merge commit or production policy application. Its EA1 exceptions expire on 2026-09-30, EA2 exceptions expire on 2026-10-21, and the five modelcar registry exceptions expire on 2026-12-31. The stage task [RHOAIENG-88510](https://redhat.atlassian.net/browse/RHOAIENG-88510) is Resolved and [MR !22103](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22103) is reachable, but merge and policy application are not independently verified.

The dependency graph traversed 177 issues and 802 comments. The strongest dependency chain is: [RHOAIENG-84639](https://redhat.atlassian.net/browse/RHOAIENG-84639) release integration work -> [RHOAIENG-88509](https://redhat.atlassian.net/browse/RHOAIENG-88509) production exception task -> [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104), with component remediation and modelcar adoption blocking the release-integration epic. The graph also identifies the broader initiative [RHAISTRAT-2096](https://redhat.atlassian.net/browse/RHAISTRAT-2096), the AIPCC compliance directive [RHAISTRAT-2046](https://redhat.atlassian.net/browse/RHAISTRAT-2046), and the prior risk [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213) as systemic context rather than independent fixes.

The component-level picture is mixed:

- ML Metadata: [AIPCC-18390](https://redhat.atlassian.net/browse/AIPCC-18390) is still In Progress; MLMD offboarding moved from EA2 to 3.6 GA, so the hermetic exception remains needed beyond the original remediation commitment.
- OpenVINO Model Server: [RHOAIENG-67702](https://redhat.atlassian.net/browse/RHOAIENG-67702) is still In Progress and targets 3.6 GA or later. The work has a large Bazel and dependency-closure problem, and the RPM-source transition is not proven complete.
- vLLM CPU: [RHAISTRAT-2304](https://redhat.atlassian.net/browse/RHAISTRAT-2304) is In Progress. The RHOAI-to-RHAII migration was delayed to EA2, so the EA1 exception was not merely a historical carry-over.
- NeMo Guardrails: [RHOAIENG-85372](https://redhat.atlassian.net/browse/RHOAIENG-85372) records 92 source and binary-attribute violations; [RHOAIENG-85748](https://redhat.atlassian.net/browse/RHOAIENG-85748) is in Review for modelcar adoption.
- OGX Core: [RHOAIENG-85373](https://redhat.atlassian.net/browse/RHOAIENG-85373) records 81 disallowed-source violations; [RHAIENG-6977](https://redhat.atlassian.net/browse/RHAIENG-6977) is Closed, but the production modelcar registry dependency remains represented in the policy exception.

The component spike issues for MLMD, vLLM, OpenVINO, NeMo Guardrails, and OGX Core are marked Resolved in the intelligence artifact, but that status does not by itself prove that the RHOAI 3.6 artifact passed Conforma without an exception. The current evidence therefore treats those records as violation evidence and uses the separate remediation and policy tasks to assess whether the exposure is closed.

### Supplementary Intelligence Sources [HUMAN]

No email or meeting intelligence was available. Gmail retrieval failed because the local Google token refresh file was unavailable; Google Drive search returned no matching documents. No analyst-supplied supplementary facts have been recorded.

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| Gmail | Unavailable during this session; no email facts used | N/A |
| Google Drive | No matching documents returned | N/A |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields (Risk Type, Severity, Likelihood, Impact)

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | High | The production policy MR explicitly covers release-blocking controls for three components and five modelcar images; [PRODSECRM-309](https://redhat.atlassian.net/browse/PRODSECRM-309) has no JIRA priority or severity set. |
| Likelihood | Likely | JIRA's current custom field is `Very Likely`; this assessment normalizes it to the template's allowed `Likely` value. The exception is based on observed Conforma violations, not a hypothetical scenario: [RHOAIENG-85379](https://redhat.atlassian.net/browse/RHOAIENG-85379), [RHOAIENG-85380](https://redhat.atlassian.net/browse/RHOAIENG-85380), and [RHOAIENG-85381](https://redhat.atlassian.net/browse/RHOAIENG-85381) document the relevant failures; the component remediation issues remain open or target GA. |
| Impact | Major | Without the exception, the production policy gate can block EA1/EA2 release artifacts; with the exception, the product retains weaker provenance, source-control, and patch-turnaround properties for multiple components and relies on a staging registry for five model images. |

### Rating Rationale

**Severity justification:**

High is appropriate because the risk affects release eligibility and software supply-chain assurance across multiple components, but current evidence does not establish an active compromise, customer exploit, or broad production outage. A Critical rating would require evidence of active exploitation, materially exposed customers, a confirmed inability to patch, or a release-wide failure that cannot be bounded by policy and component controls. A Medium rating would require proof that the policy exceptions are already approved, all affected components are rebuilt and verified, and the remaining exposure is limited to administrative cleanup.

**Likelihood justification:**

Likely reflects the present state, not an attacker probability estimate. The underlying Conforma violations are documented, remediation is incomplete or delayed, and the production exception change has not been shown to be merged and active. The rated operational event is that an affected release path either remains blocked without an active exception or proceeds under the documented control deviation while remediation is incomplete. The main control reducing likelihood is the Conforma gate itself, which detects and blocks non-compliant artifacts. The policy exception reduces release blockage but does not remove the underlying build and provenance exposure. [UNRESOLVED: the session intelligence does not quantify release-event frequency or establish which supported customer channels consume the affected artifacts.]

**Impact justification:**

The direct operational impact is release blockage or delay for affected RHOAI artifacts. The security impact is weaker evidence that all build inputs were fetched from controlled, reproducible sources and that all packages can be remediated through Red Hat-controlled channels. The modelcar path also introduces an availability and change-control dependency on a staging registry. The number of explicitly affected image groups is at least three component exceptions plus five named modelcar images; customer count, revenue exposure, and whether any GA customer path depends on these images are not quantified and remain data gaps.

### CVE Landscape

No CVE is directly associated with `PRODSECRM-309` in the root issue. The dependency graph includes the earlier [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213) risk and its historical CVE-remediation context. The session intelligence does not contain the older-release OpenVINO CVE tickets referenced in the preliminary assessment, so they are not used as evidence here. [UNRESOLVED: version-specific SBOM and CVE applicability for the RHOAI 3.6 OpenVINO artifact remain unverified.]

| CVE ID | Impact | CVSS 3.1 | Components | Confidence |
|--------|--------|----------|------------|------------|
| None directly mapped | N/A | N/A | PRODSECRM-309 scope | High |

**Data Source:** manual analysis; no direct CVE was mapped to the root risk. Findings require validation by a human expert.

---

## Section 3: Objective Alignment [AI-GENERATED]

**Maps to:** Risk Council governance model -- 7 risk objectives

| # | Objective | Affected? | Explanation |
|---|-----------|-----------|-------------|
| 1 | Product availability | Yes | Conforma exceptions are release gates. A missing, unmerged, expired, or incorrectly scoped exception can block RHOAI release artifacts; staging-registry dependence can also disrupt builds or releases. |
| 2 | Customer trust | Yes | Shipping artifacts under temporary provenance and source-control exceptions can reduce confidence in reproducibility, SBOM completeness, and vulnerability response even without a known exploit. |
| 3 | Regulatory compliance | No | No specific regulatory framework matched the applicability matrix. The issue is a Product Security policy and Enterprise Contract control matter; regulatory applicability was accepted as not matched. |
| 4 | Revenue / cost | Partial | Release delay, rework, and extended engineering effort are plausible, but customer, revenue, and cost impact is not quantified. |
| 5 | Strategic roadmap | Yes | The risk intersects RHOAI 3.6 delivery, AIPCC onboarding, RHAI modelcar publication, and the RHOAI-to-RHAII migration path. |
| 6 | Product integrity | Yes | Non-hermetic inputs, non-Red-Hat RPM signing keys, and temporary stage-registry model inputs weaken the assurance that release content is reproducible and controlled. |
| 7 | Safety, privacy, and data integrity | Partial | The modelcar content and build inputs can affect data and model integrity, but no privacy or safety-specific failure has been evidenced in this session. |

**Primary objective:** Product integrity.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| Conforma / Enterprise Contract policy checks | Detective / Preventive | Partially Effective | The checks detect and block the violations, preventing silent release of non-compliant artifacts, but approved exceptions can bypass the control for defined components and dates. |
| Time-bounded production exceptions in MR !22104 | Compensating | Ineffective until merged; partially effective after approval | The MR defines component-specific exception values and expiration dates, but the production task is in Review and merge/application are not verified, so production-policy activation is not established. |
| Stage exceptions associated with MR !22103 | Compensating | Effectiveness not verified | The stage task is Resolved and the MR link is reachable, but merge/application and the resulting stage evaluation are not independently verified. |
| AIPCC package and base-image onboarding | Corrective | Partially Effective | AIPCC work exists for Fedora/EPEL and CentOS packages, but affected component tickets indicate that consuming the approved artifacts remains incomplete. |
| MLMD offboarding and vLLM migration | Corrective | Partially Effective | MLMD offboarding moved to 3.6 GA and vLLM migration moved to EA2, extending the exception window rather than closing it. |
| Modelcar migration from external sources | Corrective | Partially Effective | Modelcars reduce direct Hugging Face/ModelScope downloads, but five images currently depend on the staging registry and still require a production policy exception. |

### Residual Exposure

The residual exposure has four distinct paths:

1. **Release-control path:** If [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104) is not merged and applied before the affected release gates, valid business-required artifacts may be blocked. If it is merged without component verification, the exception can permit artifacts whose remediation status is not current.
2. **Build-provenance path:** MLMD and OpenVINO retain non-hermetic or incompletely controlled build inputs until GA-oriented work is completed. The observed Bazel, MediaPipe, and dependency-closure complexity makes schedule slippage credible.
3. **Package-integrity path:** OpenVINO and vLLM retain RPMs signed by non-approved vendor keys until they consume AIPCC-provided packages. The policy exception records the deviation but does not independently validate package provenance or future patch turnaround.
4. **Model-content path:** Modelcar adoption improves source control relative to direct external downloads, but stage-registry publication creates a production availability and promotion/change-control dependency until the model validation team publishes the images to the production registry.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0-7 days)

- [ ] Confirm whether [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104) is approved, merged, and active in the production EC policy; record the merge commit and policy evaluation result -- **Owner:** RHOAI release integration / ProdSec policy owner -- **Definition of done:** production Conforma evaluation passes for the intended EA1/EA2 components with the exact exception references and expiration dates.
- [ ] Build a component-by-component exception register for MLMD, OpenVINO, vLLM CPU, NeMo Guardrails, and OGX Core -- **Owner:** RHOAI release integration lead -- **Definition of done:** each row has current build result, exception rule, effective expiration, remediation owner, next release target, and evidence URL.
- [ ] Confirm the five modelcar image digests, promotion controls, registry availability expectations, and whether stage content can change after release approval -- **Owner:** RHAI model validation team -- **Definition of done:** immutable digests, publication owner, promotion procedure, and rollback procedure are documented.

### Short-Term (1-4 weeks)

- [ ] Close the MLMD exception path by either completing [AIPCC-18390](https://redhat.atlassian.net/browse/AIPCC-18390) or documenting and approving the GA extension with a dated offboarding plan -- **Owner:** AIPCC MLMD owner -- **Definition of done:** MLMD is removed from the affected release path or a VP-approved, time-boxed extension has a verified end condition.
- [ ] Complete the OpenVINO approved-source migration under [RHOAIENG-67702](https://redhat.atlassian.net/browse/RHOAIENG-67702) -- **Owner:** OpenVINO Model Server engineering / AIPCC -- **Definition of done:** hermetic build passes offline, all dependencies are pinned and reproducible, approved RPM sources replace the exception keys, and Conforma passes without exception.
- [ ] Resolve the vLLM CPU transition under [RHAISTRAT-2304](https://redhat.atlassian.net/browse/RHAISTRAT-2304) -- **Owner:** RHAI/RHOAI platform owners -- **Definition of done:** RHOAI no longer builds or ships the affected vLLM CPU artifact, or the replacement image passes release and security validation for all intended architectures.
- [ ] Publish modelcars to the production registry and remove the stage-registry exception -- **Owner:** RHAI model validation team -- **Definition of done:** all five images are available in the approved production registry, referenced by immutable digest, and the production policy no longer requires the stage exception.

### Long-Term (1-3 months)

- [ ] Convert the recurring exception pattern into a release-readiness control with a single dependency dashboard linking [RHAISTRAT-2046](https://redhat.atlassian.net/browse/RHAISTRAT-2046), [RHAISTRAT-2096](https://redhat.atlassian.net/browse/RHAISTRAT-2096), component remediation, policy MRs, and release milestones -- **Owner:** AIPCC/RHOAI Product Security governance -- **Definition of done:** no exception can be renewed without current evidence, an accountable owner, a remediation milestone, and an explicit expiration review.
- [ ] Establish a standard hermetic-build readiness test before code freeze for all RHOAI components -- **Owner:** RHOAI build/release engineering -- **Definition of done:** the test covers offline dependency prefetch, approved source registries, RPM signatures, modelcar availability, SBOM/provenance generation, and multi-architecture parity.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Current merge/approval/application state of production MR !22104 | ProdSec policy owner / RHOAI release integration | Confirm merge commit and live policy evaluation | High |
| Customer and release scope affected by each exception | RHOAI product/release management | Quantify affected images, customers, release channels, and delay cost | High |
| Named director-level accountable owner for the combined risk | AI BU / RHOAI leadership | Assign one accountable owner across component and policy dependencies | High |
| Whether stage modelcars are immutable and promotion-controlled | RHAI model validation | Provide digest, publication, retention, access-control, and rollback evidence | High |
| Whether known vulnerabilities affect the RHOAI 3.6 OpenVINO artifact lineage | OpenVINO engineering / Product Security | Perform version-specific SBOM and CVE applicability review | Medium |
| Completion evidence for approved RPM-source consumption | AIPCC and component owners | Attach successful Conforma results and package provenance for OpenVINO and vLLM | High |

### Conditional Acceptance Prerequisites

N/A -- the preliminary recommendation is Mitigate / time-box the compensating exception, not accept the residual risk. If the business chooses acceptance, the prerequisites below must be met before acceptance sign-off.

| Prerequisite | Status | Evidence Required | Owner |
|-------------|--------|-------------------|-------|
| Production exception MR merged and active | Not Met | [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104) merge commit and policy evaluation | ProdSec policy owner |
| Component-level remediation plan with owners and dates | Not Met | Exception register and linked remediation tickets | RHOAI release integration |
| Stage modelcar integrity and rollback controls verified | Not Met | Image digests, registry controls, and rollback test | RHAI model validation |
| VP-level acceptance authority explicitly time-boxes residual risk | Not Met | Recorded approval with expiration and review trigger | AI BU leadership |

**Acceptance blocked until:** all prerequisites show `Met` or are explicitly waived by the required authority with documented rationale.

---

## Section 6: Escalation Analysis [AI-GENERATED]

**Maps to:** PSRR issue creation, PRODSECRM-to-PSRR link

### PSRR Promotion Assessment

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk (concrete numbers, real-world consequences) | Partial | At least three component exception paths and five modelcar images are identified; customer, revenue, and release-delay values are not quantified. |
| 2 | Actionable path (systemic fix, root cause analysis) | Yes | Component remediation, production registry publication, policy activation, and governance actions are identified with linked work. |
| 3 | Context provided (summary + recommendation) | Yes | The dependency graph and exception MR provide context; the risk is explicitly separated from [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213). |
| 4 | Tied to an objective (one of the 7) | Yes | Product integrity is primary; product availability and customer trust are also affected. |
| 5 | Named accountable risk owner (director+) | No | JIRA assignee is Ian Murphy, but no director-level business risk owner is documented for the combined dependency chain. |
| 6 | Consequence of inaction (6-12 month degradation) | Partial | Continued exception renewal could normalize non-hermetic and non-approved-source release paths; the 6-12 month customer and operational consequence is not quantified. |
| 7 | Risk posture requested (mitigation/acceptance/prioritization/transfer) | Partial | Mitigation and time-boxing are clear, but the executive decision owner and requested prioritization are not confirmed. |
| 8 | Acceptance timebox (if applicable) | Yes | Exception dates are specified through 2026-09-30, 2026-10-21, and 2026-12-31, but policy activation is not verified. |

**Promotion recommendation:** NOT READY

**Rationale:** The risk is potentially executive-relevant because it combines release blocking, software supply-chain assurance, and repeated remediation slippage across a strategic AI product. It is not ready for PSRR promotion because the current record lacks a quantified customer/business consequence, a named director-level accountable owner, and proof that the production exception MR is active. Complete those three data gaps first; promote if the quantified exposure exceeds working-register tolerance or if the exception requires executive acceptance beyond the existing approval boundary.

---

## Analyst Assessment [HUMAN]

**Action:** CONCUR

**Changes from AI recommendation:** None -- concurred as-is.

**Rationale for overrides:** N/A.

**Sign-off:** Aleksandra Haklik | 2026-09-07

---

## Supporting Evidence

No analyst-uploaded evidence files. The primary working artifact is the JIRA intelligence file generated during this session.

| File | Description | Date Added |
|------|-------------|------------|
| `intelligence.json` | JIRA dependency graph, issue metadata, comments, and extracted links; session-internal working artifact | 2026-09-07 |

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-309 | JIRA | [PRODSECRM-309](https://redhat.atlassian.net/browse/PRODSECRM-309) | Yes |
| 2 | Prior related risk | JIRA | [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213) | Yes |
| 3 | Production exception task | JIRA | [RHOAIENG-88509](https://redhat.atlassian.net/browse/RHOAIENG-88509) | Yes |
| 4 | Stage exception task | JIRA | [RHOAIENG-88510](https://redhat.atlassian.net/browse/RHOAIENG-88510) | Yes |
| 5 | RHOAI 3.6 EA1 Conforma work | JIRA | [RHOAIENG-84639](https://redhat.atlassian.net/browse/RHOAIENG-84639) | Yes |
| 6 | MLMD hermetic build support | JIRA | [AIPCC-18390](https://redhat.atlassian.net/browse/AIPCC-18390) | Yes |
| 7 | OpenVINO hermetic build | JIRA | [RHOAIENG-67702](https://redhat.atlassian.net/browse/RHOAIENG-67702) | Yes |
| 8 | vLLM CPU migration | JIRA | [RHAISTRAT-2304](https://redhat.atlassian.net/browse/RHAISTRAT-2304) | Yes |
| 9 | MLMD violation spike | JIRA | [RHOAIENG-85379](https://redhat.atlassian.net/browse/RHOAIENG-85379) | Yes |
| 10 | vLLM violation spike | JIRA | [RHOAIENG-85380](https://redhat.atlassian.net/browse/RHOAIENG-85380) | Yes |
| 11 | OpenVINO violation spike | JIRA | [RHOAIENG-85381](https://redhat.atlassian.net/browse/RHOAIENG-85381) | Yes |
| 12 | NeMo Guardrails violation spike | JIRA | [RHOAIENG-85372](https://redhat.atlassian.net/browse/RHOAIENG-85372) | Yes |
| 13 | OGX Core violation spike | JIRA | [RHOAIENG-85373](https://redhat.atlassian.net/browse/RHOAIENG-85373) | Yes |
| 14 | NeMo modelcar adoption | JIRA | [RHOAIENG-85748](https://redhat.atlassian.net/browse/RHOAIENG-85748) | Yes |
| 15 | OGX OCI/modelcar consumption | JIRA | [RHAIENG-6977](https://redhat.atlassian.net/browse/RHAIENG-6977) | Yes |
| 16 | Non-hermetic builds initiative | JIRA | [RHAISTRAT-2096](https://redhat.atlassian.net/browse/RHAISTRAT-2096) | Yes |
| 17 | AIPCC compliance directive | JIRA | [RHAISTRAT-2046](https://redhat.atlassian.net/browse/RHAISTRAT-2046) | Yes |
| 18 | Production exception policy MR | Internal / GitLab MR | [MR !22104](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104) | Yes |
| 19 | Stage exception policy MR | Internal / GitLab MR | [MR !22103](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22103) | Yes |
| 20 | Session intelligence artifact | Internal | [`intelligence.json`](/Users/ahaklik/projects/prodsecrm/risk-docs/sessions/PRODSECRM-309/2026-09-07-093958/intelligence.json) | Yes |
