---
jira_key: "PRODSECRM-312"
title: "Add trusted third-party RPM signature verification keys to Conforma's global allowed_list (Mellanox, Habanalabs/Intel, CentOS, Intel OpenVINO, Fedora/EPEL)"
status: draft
severity: "Medium"
likelihood: "Likely"
impact: "Moderate"
created: "2026-09-14"
updated: "2026-09-14"
analyst: "Aleksandra Haklik"
session_id: "2026-09-14-093350"
adversarial_mode: pending
adversarial_disposition: pending
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-14)"
    added: "2026-09-14"
  - type: jira_intelligence
    label: "JIRA Graph Traversal (30 issues, depth 3)"
    added: "2026-09-14"
---

## Executive Summary [AI-GENERATED]

PRODSECRM-312 requests adding five third-party RPM signing keys (Mellanox, Habanalabs/Intel, CentOS, Intel OpenVINO, Fedora/EPEL) to Conforma's global allowed_list, which would disable RPM signature verification for these keys across every Konflux-onboarded product at Red Hat -- not just RHOAI. If approved, this could result in any Red Hat product silently shipping third-party vendor RPMs without ProdSec review, because Conforma has no mechanism to scope a global allowed key to specific teams or products (confirmed by Austin Kimbrell, ProdSec) -- creating risk of undetected supply chain exposure and loss of customer trust in Red Hat's content integrity assurance. This is rated Medium severity because only 1 of 5 vendor legal agreements is confirmed and the underlying need is self-resolving through AIPCC base image sourcing and component retirement. The recommended action is to decline the global allowed_list request and instead extend the per-product EnterpriseContractPolicy exception pattern already used for AMD and NVIDIA keys, which provides equivalent operational relief while preserving product-scoped build integrity controls. PSRR escalation is not recommended at this time -- the risk is containable through the existing per-product exception mechanism.

---

## Section 1: Risk Identification [AI-GENERATED]

**Maps to:** JIRA Summary, Description

| Field | Value |
|-------|-------|
| Risk Type | Process / Third-Party |
| Title | Global disablement of RPM signature verification control for five third-party vendor keys across all Konflux-onboarded products |
| Description | RHOAI's request to add five vendor signing keys to Conforma's global allowed_list would eliminate the per-release, per-product review control for these keys for every Red Hat product built through Konflux. The exposure is an all-or-nothing architectural limitation in Conforma -- there is no team-level or product-level scoping for the global allowed_list. |

**Context:**

This risk was identified when the RHOAI Build & Release team ([PRODSECRM-312](https://redhat.atlassian.net/browse/PRODSECRM-312), filed 2026-09-07 by Florencio Cano Gabarda) requested ProdSec confirm whether five vendor RPM signing keys could be added to Conforma's global allowed_list. The request is motivated by operational overhead: RHOAI currently files per-component, per-release, time-boxed Conforma exception MRs for these same keys every release cycle, generating repeated PSX/PRODSECRM tickets (PSX-1098, PSX-1099, PSX-1101, PSX-1106, PSX-1110). The strategic context is tracked under [RHAISTRAT-576](https://redhat.atlassian.net/browse/RHAISTRAT-576) ("AI Platform -- Third-Party Content Compliance & Release Requirements"), which is rated Critical priority and has been in Refinement since November 2025. A prior spike ([RHOAIENG-38497](https://redhat.atlassian.net/browse/RHOAIENG-38497)) identified and cataloged all third-party RPM usage across RHOAI releases.

### Supplementary Intelligence Sources [HUMAN]

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| *(No supplementary intelligence provided by analyst)* | | |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields (Risk Type, Severity, Likelihood, Impact)

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | Medium | Global scope with no scoping mechanism (Austin Kimbrell, ProdSec, per [PRODSECRM-312](https://redhat.atlassian.net/browse/PRODSECRM-312) description), but only applies to known vendor keys with existing legal relationships, not arbitrary third parties |
| Likelihood | Likely | JIRA customfield_10642 set to "Very Likely"; the request has VP approval (jofernan@redhat.com) and active engineering pressure from repeated exception overhead across 4+ RHOAI releases |
| Impact | Moderate | Removes a detective control for 5 specific signing keys across all Konflux products; mitigated by the fact that these are known, established hardware/software vendors (Mellanox/NVIDIA, Intel, CentOS, Fedora) |

### Rating Rationale

**Severity justification:**

Medium rather than High because: (a) the keys in question belong to known, established technology vendors with existing Red Hat partnerships, not unknown or untrusted sources; (b) the actual RPM content is already shipping in RHOAI releases under per-release exceptions, so the content risk is unchanged; (c) the risk is to the *control layer* (loss of per-product review touchpoint), not to the content itself. However, it is not Low because the blast radius is genuinely global -- every Konflux-onboarded team would inherit the exception silently.

**Likelihood justification:**

Rated Likely because the request has VP-level approval, active engineering support from the RHOAI Build & Release team, and a clear operational pain point. The JIRA issue's Risk Probability field is set to "Very Likely." The repeated exception overhead (5 keys x 4+ releases = 20+ exception MRs per release cycle) creates strong incentive to approve.

**Impact justification:**

Rated Moderate because if approved: (a) any Konflux product could silently include RPMs signed with these 5 vendor keys without triggering a Conforma policy check, meaning ProdSec loses visibility into which products use third-party content from these vendors; (b) the per-release review touchpoint -- which has already caught cases where RPMs were replaced by RHEL equivalents (CentOS/ocl-icd per [AIPCC-16754](https://redhat.atlassian.net/browse/AIPCC-16754)) or components retired (Mellanox/Training Operator per [AIPCC-16830](https://redhat.atlassian.net/browse/AIPCC-16830)) -- would be eliminated; (c) however, RPM signature verification against the Red Hat key would still function for all other keys, and these specific vendor keys are not arbitrary but are tied to specific hardware enablement ecosystems.

### CVE Landscape

No CVE associations identified for this risk.

**Data Source:** Manual analysis. Findings require validation by a human expert.

---

## Section 3: Objective Alignment [AI-GENERATED]

**Maps to:** Risk Council governance model -- 7 risk objectives

| # | Objective | Affected? | Explanation |
|---|-----------|-----------|-------------|
| 1 | Product availability | Yes | RHOAI releases are currently blocked by Conforma policy checks for these keys; the global exception would resolve the blocking but at the cost of removing the control for all products |
| 2 | Customer trust | Yes | Customers rely on Red Hat's signature verification as assurance that shipped content meets Red Hat's quality and security standards; globally allowing third-party keys weakens this assurance |
| 3 | Regulatory compliance | No | No specific regulatory framework was scoped as applicable to this risk |
| 4 | Revenue / cost | No | Operational cost savings from reduced exception overhead are real but modest |
| 5 | Strategic roadmap | Yes | RHAISTRAT-576 tracks this as a Critical-priority strategic initiative for the AI Platform; the AIPCC long-term sourcing plan is the intended resolution |
| 6 | Product integrity | Yes | The core concern: globally allowing vendor keys removes a build integrity control that ensures ProdSec review of third-party content entering Red Hat products |
| 7 | Safety, privacy, and data integrity | No | No direct data safety or privacy implications identified |

**Primary objective:** Product integrity -- the risk centers on whether a build-time content integrity control should be removed globally to resolve a single product's operational burden.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| Conforma rpm_signature.allowed policy check | Detective / Preventive | Effective | Blocks releases with non-Red Hat-signed RPMs; currently catching all 5 vendor keys per release. Per-release exception MRs required to bypass, creating an audit trail. |
| Per-release, per-component exception MR process | Corrective | Effective | Each exception is time-bounded (effectiveUntil dates ranging from 2026-08-19 to 2027-05-03), product-scoped, and requires a GitLab MR in konflux-release-data. Creates a reviewable, auditable record. |
| Per-product EnterpriseContractPolicy exceptions | Preventive | Effective | Used for AMD and NVIDIA keys (MR !19223, confirmed by Chris Kodama 2026-09-08, expiring 2026-12-31). Provides permanent exception scoped to RHOAI only -- other Konflux products are not affected. |
| Legal agreement tracking (RHOAIENG epics) | Detective | Partially Effective | Tracks vendor legal agreements per key, but only 1 of 5 is confirmed (Mellanox, closed 2026-07-07 per RHOAIENG-38398). Remaining 4 are In Progress with limited visibility into timeline. |
| AIPCC base image sourcing plan | Corrective (planned) | Not Yet Effective | AIPCC Ecosystems team plan to build/provide these packages for future releases (Doug Hellmann, [RHAISTRAT-576](https://redhat.atlassian.net/browse/RHAISTRAT-576) comment 2026-06-03). Several AIPCC tickets already closed as components retired or RHEL equivalents identified. |
| Conforma-exception AI skill automation | Corrective | Effective | Automates MR creation for exception requests (used by Waldemar Znoinski across all PSX tickets), significantly reducing the mechanical overhead of the per-release exception process |

### Residual Exposure

The per-release exception process works but generates significant operational overhead: approximately 5 keys x multiple components x 4+ releases = dozens of exception MRs per release cycle. This overhead is the primary driver for the global allowed_list request. However, the conforma-exception AI skill has partially automated MR creation, and the AIPCC sourcing plan is reducing the number of keys that will actually need exceptions in future releases (Mellanox RPMs being removed with Training Operator in 3.6-EA1, CentOS RPM available in RHEL, Fedora tini replaced by catatonit).

The residual risk is that if the global exception is approved, ProdSec permanently loses visibility into which products adopt these vendor-signed RPMs, and the self-resolving nature of the problem (components retiring, AIPCC providing alternatives) would not be captured because the control that detects the usage would be removed.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0-7 days)

- [ ] **Decline the global allowed_list request** -- **Owner:** ProdSec (Austin Kimbrell / Marek Baluch) -- **Definition of done:** PRODSECRM-312 updated with ProdSec position: global allowed_list is not the appropriate mechanism; per-product EnterpriseContractPolicy exceptions are the recommended path.
- [ ] **Confirm per-product EnterpriseContractPolicy path for remaining 5 keys** -- **Owner:** Release Engineering (Chris Kodama) -- **Definition of done:** Confirm that the AMD/NVIDIA pattern (permanent per-product exceptions in RHOAI's EnterpriseContractPolicy with expiration dates) can be extended to Mellanox, Intel, CentOS, Fedora/EPEL, and Habanalabs keys.

### Short-Term (1-4 weeks)

- [ ] **Close legal agreements for remaining 4 vendors** -- **Owner:** RHOAI Engineering / Legal (Jay Koehler, Tushar Katarki) -- **Definition of done:** Legal agreements confirmed for Intel (RHOAIENG-38388), Fedora/EPEL (RHOAIENG-38389), Habanalabs (RHOAIENG-38427), and CentOS (RHOAIENG-38387), or determination that specific keys do not require legal agreements (e.g., CentOS as a Red Hat project).
- [ ] **Create consolidated per-product exception MR for confirmed keys** -- **Owner:** RHOAI Build & Release (Waldemar Znoinski) -- **Definition of done:** Single EnterpriseContractPolicy MR in konflux-release-data covering all 5 vendor keys for RHOAI, with appropriate expiration dates, following the AMD/NVIDIA pattern from MR !19223.

### Long-Term (1-3 months)

- [ ] **Complete AIPCC base image migration for remaining third-party RPMs** -- **Owner:** AIPCC Ecosystems team (Lance Barto, Christian Heimes) -- **Definition of done:** RHOAI components that currently depend on third-party RPMs are migrated to AIPCC-provided base images or RHEL equivalents. Tracked under RHAISTRAT-576.
- [ ] **Evaluate Conforma product-scoped allowed_list capability** -- **Owner:** Release Engineering / Conforma team -- **Definition of done:** Assessment of whether Conforma can support product-scoped or team-scoped key allowlists (not just global), which would address the operational burden without the blast radius concern. If feasible, file an enhancement request.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Legal agreement status for Intel, Fedora/EPEL, Habanalabs, CentOS (4 of 5 unconfirmed) | RHOAI Engineering / Legal | Confirm current status and expected completion date for each RHOAIENG legal agreement epic | High |
| Conforma's ability to support product-scoped key allowlists | Release Engineering / Conforma team | Determine whether Conforma has a roadmap for team- or product-level scoping of allowed keys | Medium |
| Count of Konflux-onboarded teams that could be affected by global key addition | Release Engineering | Enumerate teams/products currently using Konflux that would silently inherit the global exception | Medium |
| AIPCC base image migration timeline for RHOAI components | AIPCC Ecosystems | Confirm which RHOAI components will migrate to AIPCC base images in 3.6 and beyond, and which third-party RPM dependencies will be eliminated | Medium |

### Conditional Acceptance Prerequisites

N/A -- not an acceptance decision. The recommended posture is to decline the global request and redirect to per-product exceptions.

**Acceptance blocked until:** N/A.

---

## Section 6: Escalation Analysis [AI-GENERATED]

**Maps to:** PSRR issue creation, PRODSECRM-to-PSRR link

### PSRR Promotion Assessment

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk (concrete numbers, real-world consequences) | Partial | Blast radius identified (all Konflux-onboarded teams) but not quantified (how many teams, how many products) |
| 2 | Actionable path (systemic fix, root cause analysis) | Yes | Per-product EnterpriseContractPolicy exception pattern exists and is proven (AMD/NVIDIA precedent) |
| 3 | Context provided (summary + recommendation) | Yes | This analysis provides full context and recommendation |
| 4 | Tied to an objective (one of the 7) | Yes | Product integrity (Objective 6) |
| 5 | Named accountable risk owner (director+) | Partial | VP approver (jofernan@redhat.com) identified but not confirmed as risk owner; ProdSec ownership unclear between Austin Kimbrell and Marek Baluch |
| 6 | Consequence of inaction (6-12 month degradation) | No | If declined, status quo continues with manageable operational overhead; the problem is self-resolving through AIPCC sourcing |
| 7 | Risk posture requested | Yes | Recommendation: decline global, redirect to per-product exceptions |
| 8 | Acceptance timebox (if applicable) | N/A | Not an acceptance recommendation |

**Promotion recommendation:** NOT WARRANTED
**Rationale:** The risk is containable through the existing per-product EnterpriseContractPolicy mechanism without executive intervention. The operational burden that motivated the request is being reduced by the conforma-exception AI skill and will be further reduced by AIPCC base image migration. The risk does not meet the threshold for executive escalation because a proven, product-scoped solution exists and the underlying problem is self-resolving over the next 1-2 release cycles.

---

## Analyst Assessment [HUMAN]

**Action:**

**Changes from AI recommendation:**

**Rationale for overrides:**

**Sign-off:** |

---

## Supporting Evidence

| File | Description | Date Added |
|------|-------------|------------|
| intelligence.json | JIRA graph traversal: 30 issues, 155 comments, 128 URLs across PRODSECRM, PSX, RHOAIENG, RHAISTRAT, AIPCC projects | 2026-09-14 |

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-312 (root issue) | JIRA | [PRODSECRM-312](https://redhat.atlassian.net/browse/PRODSECRM-312) | Yes |
| 2 | PSX-1098 (Intel exception) | JIRA | [PSX-1098](https://redhat.atlassian.net/browse/PSX-1098) | Yes |
| 3 | PSX-1099 (Mellanox exception) | JIRA | [PSX-1099](https://redhat.atlassian.net/browse/PSX-1099) | Yes |
| 4 | PSX-1101 (Fedora/EPEL exception) | JIRA | [PSX-1101](https://redhat.atlassian.net/browse/PSX-1101) | Yes |
| 5 | PSX-1106 (Habanalabs/Intel exception) | JIRA | [PSX-1106](https://redhat.atlassian.net/browse/PSX-1106) | Yes |
| 6 | PSX-1110 (CentOS exception) | JIRA | [PSX-1110](https://redhat.atlassian.net/browse/PSX-1110) | Yes |
| 7 | RHAISTRAT-576 (strategic feature) | JIRA | [RHAISTRAT-576](https://redhat.atlassian.net/browse/RHAISTRAT-576) | Yes |
| 8 | RHOAIENG-38388 (Intel legal agreement) | JIRA | [RHOAIENG-38388](https://redhat.atlassian.net/browse/RHOAIENG-38388) | Yes |
| 9 | RHOAIENG-38398 (Mellanox legal -- Closed) | JIRA | [RHOAIENG-38398](https://redhat.atlassian.net/browse/RHOAIENG-38398) | Yes |
| 10 | RHOAIENG-38389 (Fedora/EPEL legal) | JIRA | [RHOAIENG-38389](https://redhat.atlassian.net/browse/RHOAIENG-38389) | Yes |
| 11 | RHOAIENG-38427 (Habanalabs legal) | JIRA | [RHOAIENG-38427](https://redhat.atlassian.net/browse/RHOAIENG-38427) | Yes |
| 12 | RHOAIENG-38387 (CentOS legal) | JIRA | [RHOAIENG-38387](https://redhat.atlassian.net/browse/RHOAIENG-38387) | Yes |
| 13 | RHOAIENG-38426 (AMD legal -- Resolved) | JIRA | [RHOAIENG-38426](https://redhat.atlassian.net/browse/RHOAIENG-38426) | Yes |
| 14 | RHOAIENG-42317 (3rd party RPM plan) | JIRA | [RHOAIENG-42317](https://redhat.atlassian.net/browse/RHOAIENG-42317) | Yes |
| 15 | RHOAIENG-38497 (RPM usage spike) | JIRA | [RHOAIENG-38497](https://redhat.atlassian.net/browse/RHOAIENG-38497) | Yes |
| 16 | AIPCC-16754 (CentOS sourcing -- Won't Do) | JIRA | [AIPCC-16754](https://redhat.atlassian.net/browse/AIPCC-16754) | Yes |
| 17 | AIPCC-16766 (Fedora/EPEL sourcing -- Won't Do) | JIRA | [AIPCC-16766](https://redhat.atlassian.net/browse/AIPCC-16766) | Yes |
| 18 | AIPCC-16830 (Mellanox sourcing -- Won't Do) | JIRA | [AIPCC-16830](https://redhat.atlassian.net/browse/AIPCC-16830) | Yes |
| 19 | AIPCC-16842 (NVIDIA sourcing -- Done) | JIRA | [AIPCC-16842](https://redhat.atlassian.net/browse/AIPCC-16842) | Yes |
| 20 | AIPCC-16988 (AMD sourcing -- Done) | JIRA | [AIPCC-16988](https://redhat.atlassian.net/browse/AIPCC-16988) | Yes |
| 21 | PSX-1097 (AMD exception) | JIRA | [PSX-1097](https://redhat.atlassian.net/browse/PSX-1097) | Yes |
| 22 | PSX-1035 (Intel extension) | JIRA | [PSX-1035](https://redhat.atlassian.net/browse/PSX-1035) | Yes |
| 23 | RHOAIENG-51409 (Habanalabs vllm-gaudi) | JIRA | [RHOAIENG-51409](https://redhat.atlassian.net/browse/RHOAIENG-51409) | Yes |
| 24 | RHOAIENG-38414 (NVIDIA legal) | JIRA | [RHOAIENG-38414](https://redhat.atlassian.net/browse/RHOAIENG-38414) | Yes |
| 25 | Red Hat Third-Party End User Agreements | Internal | [Third-Party Agreements](https://www.redhat.com/en/about/third-party-end-user-agreements) | Yes |
| 26 | Consolidated Conforma exception MR !19223 | Internal | [MR !19223](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/19223) | Yes |
