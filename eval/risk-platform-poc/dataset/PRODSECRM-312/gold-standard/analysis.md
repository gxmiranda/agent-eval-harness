---
jira_key: "PRODSECRM-312"
title: "Add trusted third-party RPM signature verification keys to Conforma's global allowed_list (Mellanox, Habanalabs/Intel, CentOS, Intel OpenVINO, Fedora/EPEL)"
status: draft
severity: "High"
likelihood: "Likely"
impact: "Major"
created: "2026-09-14"
updated: "2026-09-14"
analyst: "Aleksandra Haklik"
session_id: "2026-09-14-093350"
adversarial_mode: "full (escalated from garth)"
adversarial_disposition: EXHAUSTED
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-14)"
    added: "2026-09-14"
  - type: jira_intelligence
    label: "JIRA Graph Traversal (30 issues, depth 3)"
    added: "2026-09-14"
---

## Executive Summary [AI-GENERATED]

PRODSECRM-312 requests adding five third-party RPM signing keys to Conforma's global allowed_list, which would disable RPM signature verification for these keys across every Konflux-onboarded product at Red Hat -- not just RHOAI -- because Conforma has no mechanism to scope allowed keys to specific teams (Austin Kimbrell, ProdSec), creating risk of undetected supply chain exposure if any vendor key is compromised and loss of per-release visibility that has caught component retirements and RHEL replacements. This is rated High severity / Major impact [upgraded from Medium/Moderate during adversarial review] because only 1 of 5 vendor legal agreements is confirmed (Mellanox), AIPCC sourcing was abandoned for 3 of 5 vendors ("Won't Do"), making these dependencies persistent, and the blast radius is global across all Konflux products (exact count unquantified -- critical data gap). The recommended action is to decline the global request and extend the per-product EnterpriseContractPolicy exception pattern already proven for AMD and NVIDIA keys (MR !19223), which provides equivalent operational relief while preserving product-scoped controls. PSRR escalation is warranted, conditional on quantifying the Konflux blast radius, given the corrected severity and persistent nature of the dependencies.

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
| Severity | High | Global scope with no scoping mechanism (Austin Kimbrell, ProdSec, per [PRODSECRM-312](https://redhat.atlassian.net/browse/PRODSECRM-312) description); only 1 of 5 vendor legal agreements confirmed (Mellanox); AIPCC sourcing declined for 3 of 5 vendors ("Won't Do"), making the third-party dependency persistent rather than temporary [severity upgraded from Medium during adversarial review -- Garth escalation] |
| Likelihood | Likely | JIRA customfield_10642 set to "Very Likely"; the request has VP approval (jofernan@redhat.com) and active engineering pressure from repeated exception overhead across 4+ RHOAI releases |
| Impact | Major | Removes the only per-release detective control for 5 vendor signing keys across all Konflux-onboarded products; blast radius is global with no scoping mechanism; ProdSec permanently loses visibility into third-party content adoption across the product portfolio [upgraded from Moderate during adversarial review to resolve inconsistency with Severity rating] |

### Rating Rationale

**Severity justification:**

Upgraded to High during adversarial review (originally Medium). The original Medium rationale assumed (a) established vendor partnerships and (b) a self-resolving dependency via AIPCC sourcing. Both assumptions are contradicted by evidence: only 1 of 5 vendor legal agreements is confirmed (Mellanox/RHOAIENG-38398, Closed; remaining 4 are In Progress), and 3 of 5 AIPCC sourcing requests were closed as "Won't Do" (AIPCC-16754 CentOS, AIPCC-16766 Fedora/EPEL, AIPCC-16830 Mellanox), meaning AIPCC has declined to provide alternatives and the third-party RPM dependencies are persistent, not temporary. High because: (a) the blast radius is genuinely global -- every Konflux-onboarded product would silently inherit the exception with no scoping mechanism; (b) the detective control being removed is the only per-release touchpoint that catches unauthorized third-party content entering Red Hat products; (c) with 4 of 5 legal agreements unconfirmed, Red Hat has limited contractual recourse for vendor key compromise scenarios; (d) industry precedent (SolarWinds, Codecov, 3CX) demonstrates that vendor signing key compromise is a realized supply chain threat, not a theoretical one.

**Likelihood justification:**

Likelihood measures two distinct probabilities: (1) likelihood of the global allowed_list request being approved, and (2) likelihood of harm materializing if approved. For (1), rated Likely: the request has VP-level approval, active engineering support from the RHOAI Build & Release team, and a clear operational pain point. The JIRA issue's Risk Probability field is set to "Very Likely." The repeated exception overhead (5 keys x 4+ releases = 20+ exception MRs per release cycle) creates strong incentive to approve. For (2), rated Possible: a vendor signing key compromise is a demonstrated industry threat (SolarWinds, Codecov, 3CX), but the specific vendors in question have not had publicly reported key compromises. The exposure window would be indefinite if approved (no expiration on global allowlist entries), which increases cumulative probability over time. The overall Likely rating reflects the high probability of approval creating a persistent exposure window, not a judgment that compromise is imminent. [Clarified during adversarial review to distinguish approval likelihood from harm likelihood]

**Impact justification:**

Upgraded to Major during adversarial review (originally Moderate) to resolve inconsistency with the Severity rating. The original Moderate rating cited vendor reputation as a mitigating factor, but the Severity upgrade dismissed the same factor -- the ratings must use consistent logic. Impact is Major because: (a) any Konflux-onboarded product could silently include RPMs signed with these 5 vendor keys without triggering a Conforma policy check, meaning ProdSec permanently loses visibility into third-party content adoption across the entire product portfolio; (b) the per-release review touchpoint would be eliminated globally -- note that specific cases where RPMs were replaced by RHEL equivalents (CentOS/ocl-icd) or components retired (Mellanox/Training Operator) were identified during AIPCC sourcing reviews ([AIPCC-16754](https://redhat.atlassian.net/browse/AIPCC-16754), [AIPCC-16830](https://redhat.atlassian.net/browse/AIPCC-16830)), not necessarily by the Conforma exception process itself; however, the Conforma exception process creates the per-release touchpoint that triggers these reviews [corrected during adversarial review: attribution clarified]; (c) the exposure window is indefinite because the dependencies are persistent (AIPCC sourcing abandoned for 3 of 5 vendors). RPM signature verification against the Red Hat key would still function for all other keys, which provides a residual control layer.

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
| AIPCC base image sourcing plan | Corrective (planned) | Partially Effective / Abandoned for 3 of 5 vendors | AIPCC Ecosystems team originally planned to build/provide these packages (Doug Hellmann, [RHAISTRAT-576](https://redhat.atlassian.net/browse/RHAISTRAT-576) comment 2026-06-03). However, 3 of 5 AIPCC sourcing requests were closed as "Won't Do": [AIPCC-16754](https://redhat.atlassian.net/browse/AIPCC-16754) (CentOS), [AIPCC-16766](https://redhat.atlassian.net/browse/AIPCC-16766) (Fedora/EPEL), [AIPCC-16830](https://redhat.atlassian.net/browse/AIPCC-16830) (Mellanox). Only AMD ([AIPCC-16988](https://redhat.atlassian.net/browse/AIPCC-16988)) and NVIDIA ([AIPCC-16842](https://redhat.atlassian.net/browse/AIPCC-16842)) were completed -- neither is among the 5 keys in this request. Component retirements (Mellanox/Training Operator) and RHEL equivalents (CentOS/ocl-icd) may still reduce individual dependencies through separate mechanisms, but the AIPCC sourcing strategy as a comprehensive solution is no longer viable. |
| Conforma-exception AI skill automation | Corrective | Effective | Automates MR creation for exception requests (used by Waldemar Znoinski across all PSX tickets), significantly reducing the mechanical overhead of the per-release exception process |

### Residual Exposure

The per-release exception process works but generates operational overhead: approximately 5 keys x multiple components x 4+ releases = dozens of exception MRs per release cycle. This overhead is the primary driver for the global allowed_list request. However, the conforma-exception AI skill has partially automated MR creation (used by Waldemar Znoinski across all PSX tickets), which substantially reduces the mechanical burden. This automation mitigates the operational urgency argument: the per-release process is no longer as burdensome as when exceptions were entirely manual. [Added during adversarial review: the automation control was documented in Section 4 but not factored into the urgency analysis] Individual component retirements (Mellanox RPMs being removed with Training Operator in 3.6-EA1) and RHEL equivalents (CentOS/ocl-icd, Fedora tini replaced by catatonit) may reduce some dependencies over time, but the AIPCC comprehensive sourcing strategy has been abandoned for 3 of 5 vendors (CentOS, Fedora/EPEL, Mellanox -- all closed as "Won't Do"). The third-party RPM dependency for these vendors is therefore persistent, not temporary. [Corrected during adversarial review: original text characterized the problem as "self-resolving through AIPCC sourcing," which is contradicted by AIPCC ticket resolutions.]

The residual risk is that if the global exception is approved, ProdSec permanently loses visibility into which products adopt these vendor-signed RPMs. Additionally, with only 1 of 5 legal agreements confirmed (Mellanox/RHOAIENG-38398), Red Hat's contractual posture for incident response and key revocation notification is incomplete for 4 vendors. The combination of persistent dependencies and incomplete legal agreements increases the exposure window and limits Red Hat's options in a vendor key compromise scenario.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0-7 days)

- [ ] **Engage with requestor before issuing formal decision** -- **Owner:** ProdSec (Austin Kimbrell / Marek Baluch) -- **Definition of done:** Comment on PRODSECRM-312 acknowledging the request, outlining ProdSec's concerns about global blast radius, and proposing the per-product EnterpriseContractPolicy alternative. PRODSECRM-312 currently has zero ProdSec comments -- the requestor (Florencio Cano Gabarda) should be engaged before a formal decline to ensure their operational constraints are fully understood and the alternative path addresses their needs. [Added during adversarial review: original recommendation jumped to decline without demonstrated engagement]
- [ ] **Confirm per-product EnterpriseContractPolicy path for remaining 5 keys** -- **Owner:** Release Engineering (Chris Kodama) -- **Definition of done:** Confirm that the AMD/NVIDIA pattern (permanent per-product exceptions in RHOAI's EnterpriseContractPolicy with expiration dates) can be extended to Mellanox, Intel, CentOS, Fedora/EPEL, and Habanalabs keys. **Note on legal prerequisite:** The analysis's own evidence suggests completed legal agreements are NOT a prerequisite for EnterpriseContractPolicy exceptions: MR !19223 covers NVIDIA keys, but NVIDIA legals (RHOAIENG-38414) remain In Progress. This means the per-product exception path is likely feasible for all 5 vendors regardless of legal agreement status, strengthening the recommendation's viability. Confirm this interpretation with Release Engineering. [Resolved during adversarial review Round 3: NVIDIA legals precedent]

### Short-Term (1-4 weeks)

- [ ] **Obtain status update on legal agreements for remaining 4 vendors** -- **Owner:** RHOAI Engineering / Legal (Jay Koehler, Tushar Katarki) -- **Definition of done:** Current status report for Intel (RHOAIENG-38388), Fedora/EPEL (RHOAIENG-38389), Habanalabs (RHOAIENG-38427), and CentOS (RHOAIENG-38387) legal agreement epics, including realistic completion timeline and identification of any blockers. Note: these epics have been In Progress for 3+ months; completing them within 1-4 weeks is not realistic. For CentOS specifically, determine whether the signing key (05b555b38483c65d) is a CentOS Stream key (Red Hat controlled) or a legacy CentOS key (community controlled), which materially affects the legal requirement. [Timeline corrected during adversarial review]
- [ ] **Create consolidated per-product exception MR for confirmed keys** -- **Owner:** RHOAI Build & Release (Waldemar Znoinski) -- **Definition of done:** Single EnterpriseContractPolicy MR in konflux-release-data covering all 5 vendor keys for RHOAI, with appropriate expiration dates, following the AMD/NVIDIA pattern from MR !19223.

### Long-Term (1-3 months)

- [ ] **Identify alternative sourcing paths for persistent third-party RPM dependencies** -- **Owner:** RHOAI Build & Release (Waldemar Znoinski) / AIPCC Ecosystems (Lance Barto) -- **Definition of done:** For the 3 vendors where AIPCC sourcing was declined (CentOS/AIPCC-16754, Fedora-EPEL/AIPCC-16766, Mellanox/AIPCC-16830 -- all "Won't Do"), document whether (a) individual component retirements or RHEL equivalents provide an alternative resolution path, or (b) the dependency is truly permanent and the per-product exception is the long-term posture. [Corrected during adversarial review: original recommendation to "complete AIPCC migration" was contradicted by AIPCC "Won't Do" resolutions]
- [ ] **Evaluate Conforma product-scoped allowed_list capability** -- **Owner:** Release Engineering / Conforma team -- **Definition of done:** Assessment of whether Conforma can support product-scoped or team-scoped key allowlists (not just global), which would address the operational burden without the blast radius concern. If feasible, file an enhancement request.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Legal agreement status for Intel, Fedora/EPEL, Habanalabs, CentOS (4 of 5 unconfirmed) | RHOAI Engineering / Legal | Confirm current status and expected completion date for each RHOAIENG legal agreement epic | High |
| Conforma's ability to support product-scoped key allowlists | Release Engineering / Conforma team | Determine whether Conforma has a roadmap for team- or product-level scoping of allowed keys | Medium |
| Count of Konflux-onboarded teams that could be affected by global key addition | Release Engineering (Chris Kodama) | Enumerate teams/products currently using Konflux that would silently inherit the global exception. This is the single most important data point for the severity argument -- the entire "global blast radius" claim is an unquantified assertion without this number. Suggested JIRA query: `project in (KONFLUX, KFLUXBUGS, STONEBLD) AND type = Epic` | **Critical** [upgraded from Medium during adversarial review] |
| AIPCC base image migration timeline for RHOAI components | AIPCC Ecosystems | For the 3 vendors where AIPCC sourcing was declined (CentOS, Fedora/EPEL, Mellanox), confirm whether individual component retirements or RHEL equivalents provide an alternative resolution path, or whether the dependency is permanent | Medium |
| Per-vendor signing key risk differentiation | ProdSec | Differentiate risk profile across three vendor categories: (a) Intel/Habanalabs (Intel ecosystem), (b) Mellanox (NVIDIA ecosystem), (c) CentOS/Fedora-EPEL (Red Hat-adjacent community). Assess key management practices, compromise probability, and Red Hat's influence over signing infrastructure for each | Medium |
| VP scope awareness | ProdSec Lead | Verify whether VP approver (jofernan@redhat.com) was aware the request affects all Konflux products globally, not just RHOAI | High |

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
| 6 | Consequence of inaction (6-12 month degradation) | Yes | If the global request is approved without controls, ProdSec permanently loses per-release visibility into third-party content across all Konflux products. The dependencies are persistent -- AIPCC sourcing was abandoned for 3 of 5 vendors ("Won't Do") and 4 of 5 legal agreements remain unconfirmed after 3+ months. Without the per-release exception touchpoint, component retirements and RHEL replacements would go undetected. [Corrected during adversarial review: original text incorrectly stated "self-resolving through AIPCC sourcing"] |
| 7 | Risk posture requested | Yes | Recommendation: decline global, redirect to per-product exceptions |
| 8 | Acceptance timebox (if applicable) | N/A | Not an acceptance recommendation |

**Promotion recommendation:** WARRANTED (conditional on blast radius quantification)
**Rationale:** Following adversarial review, 5 of 8 promotion requirements are met (Requirements 1-4, 6-7), with 2 partial (Requirements 1, 5) and 1 N/A (Requirement 8). The original "Not Warranted" conclusion rested on two claims that were invalidated during review: (a) the "self-resolving" narrative was contradicted by 3 of 5 AIPCC "Won't Do" resolutions; (b) the "established partnerships" argument was undermined by only 1 of 5 legal agreements being confirmed. With severity and impact both upgraded to High, persistent dependencies, and the blast radius described as global (though unquantified -- the critical remaining data gap), the risk meets the threshold for executive visibility. The per-product EnterpriseContractPolicy mechanism provides a viable containment path that does not require executive intervention to implement, but the systemic nature of the Conforma architectural limitation (no product-level scoping) and the persistent dependency on unconfirmed vendor relationships warrant PSRR awareness. Promotion should proceed once the Konflux product count is obtained to quantify the blast radius. [Revised during adversarial review from "Not Warranted" to "Warranted (conditional)" -- original rationale invalidated by corrected evidence]

---

## Analyst Assessment [HUMAN]

**Action:** CONCUR

**Changes from AI recommendation:**
None -- concurred as-is.

**Rationale for overrides:**
N/A

**Sign-off:** Aleksandra Haklik | 2026-09-14

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
| 25 | Red Hat Third-Party End User Agreements | Internal | [Third-Party Agreements](https://www.redhat.com/en/about/third-party-end-user-agreements) | Yes (referenced in PRODSECRM-312 description as basis for "legally-cleared" claim) |
| 26 | Consolidated Conforma exception MR !19223 | Internal | [MR !19223](https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/19223) | Yes (referenced in PRODSECRM-312 description; Chris Kodama attribution from analyst session notes -- not in JIRA comments) |

**Source verification notes (added during adversarial review):** The following attributions are sourced from the PRODSECRM-312 description (intelligence.json working artifact, omitted from critique context per Safety Rule 11) and were verified by the researcher against the working artifact: (a) Austin Kimbrell confirming Conforma's global-only scoping -- verbatim in description: "Per Austin Kimbrell (ProdSec), Conforma currently has no mechanism to scope an allowed key to specific teams/projects only"; (b) jofernan@redhat.com VP approval -- "Approving VP Email: jofernan@redhat.com" field in description; (c) Doug Hellmann AIPCC comment -- confirmed in RHAISTRAT-576 comments (2026-06-03). Chris Kodama is listed as a watcher (ckodama@redhat.com) but has no JIRA comments; the MR !19223 attribution comes from analyst session context.
