# Risk Assessment: PRODSECRM-316

## Metadata

```yaml
jira_key: "PRODSECRM-316"
title: "OCP mixed el8/el9 images on a single Konflux advisory CPE (temporary skip of check-labels CPE match)"
status: draft
severity: "High"
likelihood: "Likely"
impact: "Major"
created: "2026-09-10"
updated: "2026-09-10"
analyst: "Aleksandra Haklik"
session_id: "2026-09-10-135555"
adversarial_mode: pending
adversarial_disposition: pending
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-10)"
    added: "2026-09-10"
```

---

## Executive Summary [AI-GENERATED]

Red Hat has granted a time-boxed exception allowing OpenShift Container Platform (OCP) z-stream releases to skip a release-pipeline check that verifies each container image's product identifier (CPE) matches the identifier on its security advisory, because OCP still ships mixed RHEL 8/RHEL 9 images under a single advisory. This is not a hypothetical gap: Red Hat's own published vulnerability data (VEX) for CVE-2025-65637 already shows RHEL 8 images incorrectly attributed to an RHEL 9 product identifier, which can cause vulnerability scanners that key off product identifiers to report a fixed image as still vulnerable, or vice versa — undermining the accuracy of Red Hat's public security advisories for customers who rely on them, including regulated customers. The permanent fixes (splitting advisories per RHEL version, or supporting multiple product identifiers per advisory) both remain in "New" status with no committed delivery date, and the parent engineering program has slipped its delivery date three times and was recently deprioritized — raising real doubt that the exception will be resolved, rather than renewed, by its 2026-10-03 expiration. The most important recommended action is to require a committed remediation date on ART-14748 (or KONFLUX-6854) as a hard condition of any renewal, and to correct the ticket's exception-category labeling so it is subject to the standard Conforma-exception governance cadence. PSRR escalation is not currently recommended, but should be revisited if the exception is renewed past 2026-10-03 without a committed remediation date.

---

## Section 1: Risk Identification [AI-GENERATED]

**Maps to:** JIRA Summary, Description

| Field | Value |
|-------|-------|
| Risk Type | Technical / Process (release-pipeline compliance gate exception with product-integrity consequences) |
| Title | OCP mixed el8/el9 container images share one Konflux advisory CPE, causing incorrect CPE attribution in published CSAF/VEX security advisories |
| Description | Konflux's release pipeline requires every image's CPE label to match the single CPE declared on its advisory (`check-labels`, part of the `enforceContainerFirstSecurityLabels` control). OCP z-stream releases ship both el8 and el9 images under one advisory, so they fail this check. A scoped, time-boxed exception lets OCP mixed-stream release pipelines skip this specific check while continuing to enforce name and timestamp label checks. |

**Context:**
This risk was created on 2026-09-10 by Hardik Vyas as a ProdSec exception request, approved by VP Scott Cuppett (scuppett@redhat.com), expiring 2026-10-03. The trigger was the merge of [release-service-catalog PR #2451](https://github.com/konflux-ci/release-service-catalog/pull/245) (~7 Sep 2026), which made `enforceContainerFirstSecurityLabels` mandatory (previously it could be disabled). This enforcement change is itself tracked as part of the "container-first vulnerability reporting" program ([KONFLUX-6210](https://redhat.atlassian.net/browse/KONFLUX-6210), [RELEASE-1670](https://redhat.atlassian.net/browse/RELEASE-1670)), which per [KONFLUX-8496](https://redhat.atlassian.net/browse/KONFLUX-8496) is coordinated with the Konflux Conforma team and governed by [EC-1297](https://redhat.atlassian.net/browse/EC-1297) ("Enforce Required Image Labels") — i.e., this is an Enterprise Contract (Conforma) policy gate, tracked in Konflux's own "Conforma" backlog category per bot comments on KONFLUX-6210.

OCP cannot currently split its single payload advisory per RHEL version — that is tracked separately in [ART-14748](https://redhat.atlassian.net/browse/ART-14748), which per its 2026-09-09 comment thread requires cross-team negotiation (ART tooling, Cincinnati, ERT, Release Controller, docs) and is not a same-week fix.

### Supplementary Intelligence Sources [HUMAN]

No email or Drive intelligence was found for this risk (Gmail search: 0 threads; Drive search: 0 files). No supplementary intelligence was provided by the analyst during this session.

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| N/A | No supplementary sources identified | N/A |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields (Risk Type, Severity, Likelihood, Impact)

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | High | Advisory/CSAF product-identifier accuracy is already wrong in a shipped, public artifact (CVE-2025-65637 VEX for RHSA-2026:6493 lists `ose-openshift-apiserver-rhel8` under the Konflux 4.12 product CPE `cpe:/a:redhat:openshift:4.12::el9`, per the ticket description); combined with a documented precedent (KONFLUX-11654, 2026-07-06 comment) that OCP images have shipped with incorrect label data without the release being stopped, and a stalled/deprioritized permanent-fix program (see Likelihood). Not rated Critical because the underlying container image content and digest-level identity remain correct — this is a metadata/advisory-accuracy defect, not an exploitable vulnerability or a wrong-bits-shipped defect. |
| Likelihood | Likely | The CPE mismatch is not a future risk — it is already occurring in production (CVE-2025-65637/RHSA-2026:6493 is cited as a live example in the ticket's own risk analysis). Given OCP has multiple z-streams (4.12-4.18 mentioned as needing this exception) and will continue shipping mixed el8/el9 releases for the duration of the exception (through at least 2026-10-03), further instances of CPE misattribution in CSAF/VEX data are near-certain to occur during the exception window. The likelihood that a misattribution actually causes a scanner to miss a real fix (versus mismatch-with-no-consequence) is somewhat lower and depends on scanner CPE-matching behavior — [ROX-27482](https://redhat.atlassian.net/browse/ROX-27482) (Priority: Critical, open since Dec 2024, linked customer cases) documents that ACS scanners already have gaps detecting vulnerabilities in Konflux-built images unrelated to this specific defect, indicating the scanner ecosystem around Konflux images is not fully robust to metadata irregularities of this kind. |
| Impact | Major | If a CPE-first scanner treats a patched image as still vulnerable (or the reverse) because of this mismatch, the consequence is either erosion of trust in Red Hat's published CSAF/VEX feeds (which regulated customers use for vulnerability management and compliance attestation) or a missed/false vulnerability alert for a shipped security fix. Not rated Catastrophic because the ticket's own analysis states the underlying image content and digest are correct — no wrong bits ship, and the defect is scoped to metadata/reporting rather than the security posture of the running workload itself. |

### Rating Rationale

**Severity justification:**
High severity is warranted by three compounding factors, not any single one: (1) the defect is not theoretical — it is documented as already present in a published, customer-facing security artifact (the CVE-2025-65637 VEX document); (2) the org has a track record, evidenced in KONFLUX-11654, of OCP image label defects shipping to production without the release being halted, which undercuts confidence that the "name and timestamp checks remain enforced" compensating control in this exception will reliably catch adjacent problems; and (3) the two permanent remediation paths are both stalled (see Likelihood/Section 4), meaning this is not a short, contained gap. It is not Critical because the exposure is explicitly bounded to advisory/CSAF metadata — the actual container images ship with correct content and correct per-image CPE labels.

**Likelihood justification:**
The event that defines this risk (a mismatched CPE appearing in a published advisory) is already recurring, not speculative — OCP has multiple z-streams in flight during the exception window (4.12-4.18 cited) and will continue triggering this condition on every mixed-stream release until either the exception expires or a permanent fix lands. Controls partially reducing likelihood of *harm* (as opposed to the metadata error itself): the scoped, OCP-only CI constraint (not a global override) and continued enforcement of name/timestamp checks. Controls that do not appear robust: reliance on downstream scanners to correctly handle a known-mismatched CPE, given ROX-27482's evidence that Konflux-image scanner accuracy already has open gaps.

**Impact justification:**
Quantification is limited by available evidence — the ticket documents one concrete instance (CVE-2025-65637/RHSA-2026:6493) but does not enumerate how many other CVEs or z-streams have been affected, how many customers consume the affected CSAF/VEX documents, or whether any customer has yet acted on a mismatched entry. This is a material data gap for full impact quantification (see Section 5, Data Gaps). Qualitatively, the impact is concentrated on the accuracy and trustworthiness of Red Hat's public vulnerability disclosure data (CSAF/VEX) for OpenShift, which is a product-integrity and customer-trust exposure, and — for customers in regulated environments who consume CSAF/VEX for compliance attestation — a potential downstream compliance-accuracy issue for the *customer*, though this analysis found no evidence that Red Hat itself has a direct regulatory obligation triggered by this specific defect (see Section 3, Objective 3).

### CVE Landscape

| CVE ID | Impact | CVSS 3.1 | Components | Confidence |
|--------|--------|----------|------------|------------|
| [CVE-2025-65637](https://nvd.nist.gov/vuln/detail/CVE-2025-65637) | Denial-of-service in `github.com/sirupsen/logrus` (`Entry.Writer()` fails on payloads >64KB without newlines, closing the writer pipe and causing application unavailability) | 7.5 HIGH | Affects versions of the `logrus` Go module; relevant here only as the concrete example CVE whose [VEX document](https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-65637.json) demonstrates the CPE-misattribution defect for [RHSA-2026:6493](https://access.redhat.com/errata/RHSA-2026:6493) | High (confirmed via NVD; the CPE-mismatch pattern itself is confirmed by the ticket author's direct inspection of the VEX document, not independently re-verified by this analyst) |

**Data Source:** NVD (queried live for CVE-2025-65637). The CPE-misattribution claim for this CVE's VEX document is sourced from the PRODSECRM-316 ticket description and was not independently re-fetched and verified against the live VEX JSON during this session — flagged as a data gap (Section 5).

---

## Section 3: Objective Alignment [AI-GENERATED]

**Maps to:** Risk Council governance model — 7 risk objectives

| # | Objective | Affected? | Explanation |
|---|-----------|-----------|--------------|
| 1 | Product availability | No | The exception does not affect whether OCP images build, release, or run correctly; it affects advisory metadata accuracy only. |
| 2 | Customer trust | Yes | Customers and downstream tooling rely on Red Hat's CSAF/VEX feeds as an authoritative, accurate vulnerability-disclosure source. A documented CPE misattribution in a published advisory (CVE-2025-65637 case) directly undermines that trust if discovered by a customer or auditor. |
| 3 | Regulatory compliance | Partial | Deterministic regulatory scoping (CRA, FedRAMP, PCI-DSS, SOC 2 applicability matrix) found no strong trigger for this risk directly. However, customers operating in regulated environments who consume CSAF/VEX for their own compliance attestations could be indirectly affected by inaccurate source data. This is a customer-side compliance risk, not a directly evidenced Red Hat regulatory obligation — flagged as Partial rather than Yes. |
| 4 | Revenue / cost | No | No direct financial exposure was identified in available evidence. |
| 5 | Strategic roadmap | Yes | This exception exists because of tension between the container-first vulnerability-reporting rollout (KONFLUX-6210/RELEASE-1670) and OCP's product-architecture readiness (single payload advisory field, ART-14748). The rollout proceeded ahead of OCP's readiness to comply, and the parent program has since been deprioritized (Major → Normal, 2026-08-12), indicating a strategic sequencing problem, not just a one-off. |
| 6 | Product integrity | Yes | CSAF/VEX security-advisory accuracy is itself a product-integrity concern for Red Hat's security data products, independent of the underlying container image integrity (which the ticket asserts remains correct). |
| 7 | Safety, privacy, and data integrity | Partial | No safety or privacy data is implicated. Data integrity is implicated narrowly — the integrity of published security-advisory metadata, not customer data. |

**Primary objective:** Customer trust (accuracy and reliability of Red Hat's published CSAF/VEX vulnerability-disclosure data).

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| Scoped, OCP-only CI constraint (not a global RPA toggle) | Preventive | Partially Effective | The ticket description states the workaround is implemented as an OCP-scoped pipeline/CI constraint rather than a global disable, limiting blast radius to OCP mixed-stream RPAs. Not independently verified against the actual pipeline configuration during this session. |
| Name-label and timestamp checks remain enforced | Preventive | Partially Effective | Per the ticket, only the CPE-match check is skipped; name and timestamp checks continue. However, KONFLUX-11654 (2026-07-06 comment) documents that OCP images have shipped with incorrect `name` label values in production without the release being stopped — this weakens confidence that the "remains enforced" claim provides reliable protection against related label defects on the OCP pipeline specifically. |
| Time-boxed expiration (2026-10-03) with stated re-review intent | Corrective/Governance | Ineffective as currently configured | The exception ties expiration to two remediation tickets (ART-14748, KONFLUX-6854) landing in production, but neither has a committed target date, and the ticket carries none of the standard exception labels (`conforma`, `exception`, `risk-assessed`) used on comparable exceptions, placing it outside the org's standard 60-day mandatory re-review guardrail (`docs/conforma-exception-grouping.md`). Historical precedent (PRODSECRM-213, Resolved — "Renewing Recently Expired Exceptions"; PRODSECRM-309, In Progress — extends PRODSECRM-213's remediation timeline) shows that committed remediation dates for exceptions of this kind have previously slipped and required renewal. |
| Broader container-first vulnerability reporting program | Corrective (long-term) | Ineffective (stalled) | The parent epic KONFLUX-6210 has slipped its target end date three times (2026-06-30 → 07-31 → 08-26, still undelivered as of 2026-09-10) and was downgraded from Major to Normal priority on 2026-08-12 (now ranked 12th of 84 in the Security backlog). Its active child, RELEASE-1670, was still "WIP" as of 2026-08-25. |

### Residual Exposure

After accounting for current controls, the residual exposure is: (1) any CVE affecting an OCP mixed el8/el9 z-stream released during the exception window will produce a CSAF/VEX document with a potentially misattributed CPE, exactly as already occurred for CVE-2025-65637; (2) neither of the two structural fixes (ART-14748 split-advisory design; KONFLUX-6854 multi-CPE advisory support) has a committed delivery date, so there is a real possibility the exception is renewed past 2026-10-03 rather than resolved, consistent with this organization's documented precedent of exception renewals (PRODSECRM-213 → PRODSECRM-309); and (3) because the ticket is not labeled or categorized as a standard Conforma exception, it is not currently subject to the 60-day mandatory re-review, severity-ratchet, or remediation-plan-required guardrails that would otherwise apply and that were purpose-built to prevent this exact renewal pattern.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0-7 days)

- [ ] Correct the exception categorization/labeling on PRODSECRM-316 to reflect that the bypassed check (`check-labels`/`enforceContainerFirstSecurityLabels`) is an Enterprise Contract (Conforma) policy gate per EC-1297/KONFLUX-8496, and apply standard labels (`conforma`, `exception`, `risk-assessed`) so the ticket is captured by the org's standard 60-day re-review guardrail. — **Owner:** ProdSec GRC / risk program (per `docs/conforma-exception-grouping.md` lifecycle) — **Definition of done:** ticket carries the standard labels and is included in the next Conforma-exception review cycle.
- [ ] Independently re-verify the CVE-2025-65637 VEX document against the live CSAF feed to confirm the CPE-misattribution claim as stated, and check for additional CVEs affected during the exception window to date. — **Owner:** ProdSec / PSIRT — **Definition of done:** documented count of affected CVE/advisory pairs since the exception was granted.

### Short-Term (1-4 weeks)

- [ ] Obtain a committed target date on ART-14748 (currently has an owner, Fabio Gallotti, but no target date/fix version) as a hard precondition for any renewal of this exception past 2026-10-03. — **Owner:** ART team (Fabio Gallotti) — **Definition of done:** ART-14748 has a fix version/target date recorded in JIRA.
- [ ] Confirm with the ACS/scanner teams (ROX-27482 owners) whether CPE-first scanning paths are actually exposed to this specific mismatch pattern, to convert the Likelihood/Impact rating from qualitative to evidence-quantified. — **Owner:** ACS scanning team — **Definition of done:** written confirmation of scanner CPE-matching behavior for Konflux-built OCP images.

### Long-Term (1-3 months)

- [ ] Land a permanent fix — either ART-14748 (split RPAs/advisories per RHEL version) or KONFLUX-6854 (multi-CPE-per-advisory support) — before the next exception renewal decision point. — **Owner:** ART / Konflux Release engineering — **Definition of done:** OCP mixed-stream releases no longer require the check-labels CPE-match exception.
- [ ] Re-baseline the container-first vulnerability reporting program (KONFLUX-6210/RELEASE-1670) delivery date given three prior slips and a recent priority downgrade, and assess whether the priority downgrade is compatible with the urgency implied by this and similar exceptions. — **Owner:** Konflux Release/Security program leadership — **Definition of done:** a credible, stakeholder-reviewed delivery date is recorded.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| No count of how many CVEs/advisories have been affected by this CPE-misattribution pattern since the exception took effect (~7 Sep 2026) | PSIRT | Query CSAF/VEX feed for OCP mixed-stream advisories issued during the exception window and check for CPE-attribution errors | High |
| No confirmation of whether any customer-facing scanner has actually produced an incorrect vulnerability status (missed fix or false alarm) as a result of this defect | ACS / scanning ecosystem teams | Cross-reference known Konflux-image scanner gaps (ROX-27482) against the specific CPE-mismatch pattern | High |
| ART-14748 has no committed target date despite being the "preferred near-term" remediation path | ART team (Fabio Gallotti) | Set a fix version/target date | High |
| No confirmation of the correct release-service-catalog PR number — the ticket's own link for "PR #2451" resolves to `pull/245`, a likely transcription error | ProdSec GRC (ticket author/reporter) | Correct the source ticket's PR reference | Low |

### Conditional Acceptance Prerequisites

| Prerequisite | Status | Evidence Required | Owner |
|-------------|--------|-------------------|-------|
| Remediation plan documented with committed target date and owner (per `docs/conforma-exception-grouping.md` "Remediation Plan Required" guardrail) | Not Met | ART-14748 fix version/target date | ART team (Fabio Gallotti) |
| Exception correctly categorized/labeled as a Conforma exception and entered into the standard 60-day re-review cycle | Not Met | Standard labels applied; ticket linked into the Conforma-exception review process | ProdSec GRC |
| Confirmation of blast radius (CVE/advisory count affected, scanner exposure) | Not Met | PSIRT and ACS findings per Data Gaps above | PSIRT / ACS |

**Acceptance blocked until:** All prerequisites show "Met" or "Waived" status, or the accept authority (VP-level minimum for High severity — already satisfied by VP Scott Cuppett's approval for the *initial, time-boxed* grant) explicitly waives the prerequisite with documented rationale for any *renewal* beyond 2026-10-03.

---

## Section 6: Escalation Analysis [AI-GENERATED]

**Maps to:** PSRR issue creation, PRODSECRM-to-PSRR link

### PSRR Promotion Assessment

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk (concrete numbers, real-world consequences) | Partial | One concrete instance documented (CVE-2025-65637/RHSA-2026:6493); no aggregate count of affected CVEs/customers (Data Gap). |
| 2 | Actionable path (systemic fix, root cause analysis) | Partial | Two remediation paths exist (ART-14748, KONFLUX-6854) but neither has a committed date. |
| 3 | Context provided (summary + recommendation) | Yes | Full context documented in this analysis and the source ticket. |
| 4 | Tied to an objective (one of the 7) | Yes | Customer trust (primary), product integrity, strategic roadmap. |
| 5 | Named accountable risk owner (director+) | Partial | VP Scott Cuppett approved the exception, but no director+ owner is named for the underlying systemic risk (mixed-CPE architecture gap) itself — the JIRA assignee (Bart Kulaga) does not appear to be director-level. |
| 6 | Consequence of inaction (6-12 month degradation) | Partial | Plausible degradation path exists (repeated exception renewal, growing CSAF/VEX inaccuracy) but is not quantified over a 6-12 month horizon in available evidence. |
| 7 | Risk posture requested (mitigation/acceptance/prioritization/transfer) | Yes | Accept-with-conditions (time-boxed exception) is the posture already requested and granted. |
| 8 | Acceptance timebox (if applicable) | Yes | Explicit expiration: 2026-10-03. |

**Promotion recommendation:** NOT READY

**Rationale:** The risk is real and reasonably well-documented, but two of the PSRR promotion requirements most relevant to executive decision-making — quantified blast radius and a named director+ risk owner for the underlying architectural gap (as distinct from the VP who approved the time-boxed exception) — are not yet met. If the exception is renewed past 2026-10-03 without a committed remediation date on ART-14748 or KONFLUX-6854, or if the Data Gap queries reveal a larger-than-expected blast radius (multiple affected CVEs/customers), this recommendation should be revisited toward PROMOTE, since a pattern of un-remediated, un-owned exception renewals is itself the kind of systemic risk this platform's own governance model (`docs/conforma-exception-grouping.md`) was built to surface to leadership rather than let recur as isolated 1:1 tickets.

---

## Analyst Assessment [HUMAN]

{This section is completed by the human analyst, NOT the AI. It records the analyst's judgment after reviewing the AI analysis and adversarial review.}

**Action:** {CONCUR | MODIFY | OVERRIDE | DEFER}

_Note: "CONCUR" records the analyst's concurrence with the AI recommendation. This is NOT a risk acceptance decision -- risk acceptance is a business owner decision, not an analyst action. This field records the analyst's response to the AI recommendation only._

**Changes from AI recommendation:**
{List specific modifications to AI-recommended ratings, mitigations, or escalation. Or "None -- concurred as-is."}

**Rationale for overrides:**
{Required if action is OVERRIDE. Explain why the AI recommendation was changed.}

**Sign-off:** {Analyst name} | {Date}

---

## Supporting Evidence

No evidence files were uploaded during this session.

| File | Description | Date Added |
|------|-------------|------------|
| N/A | No evidence files uploaded | N/A |

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-316 (root issue) | JIRA | [PRODSECRM-316](https://redhat.atlassian.net/browse/PRODSECRM-316) | Yes |
| 2 | ART-14748 — Split RPAs for OCP versions with mixed el8/el9 images | JIRA | [ART-14748](https://redhat.atlassian.net/browse/ART-14748) | Yes |
| 3 | KONFLUX-6854 — advisory task supports multiple cpes | JIRA | [KONFLUX-6854](https://redhat.atlassian.net/browse/KONFLUX-6854) | Yes |
| 4 | KONFLUX-6210 — container-first vulnerability reporting (parent epic) | JIRA | [KONFLUX-6210](https://redhat.atlassian.net/browse/KONFLUX-6210) | Yes |
| 5 | RELEASE-1670 — Container-first vulnerability reporting (active child epic) | JIRA | [RELEASE-1670](https://redhat.atlassian.net/browse/RELEASE-1670) | Yes |
| 6 | KONFLUX-11654 — Get enforceContainerFirstSecurityLabels RPA changes merged (label-defect precedent) | JIRA | [KONFLUX-11654](https://redhat.atlassian.net/browse/KONFLUX-11654) | Yes |
| 7 | KONFLUX-8496 — Notify Conforma team when policy checks should be enforced | JIRA | [KONFLUX-8496](https://redhat.atlassian.net/browse/KONFLUX-8496) | Yes |
| 8 | EC-1297 — Enforce Required Image Labels | JIRA | [EC-1297](https://redhat.atlassian.net/browse/EC-1297) | Yes |
| 9 | ROX-27482 — ACS Scanners unable to detect vulnerabilities in Konflux-generated images | JIRA | [ROX-27482](https://redhat.atlassian.net/browse/ROX-27482) | Yes |
| 10 | PSIRT-2797 — Container CVE Affectedness (broader accuracy program) | JIRA | [PSIRT-2797](https://redhat.atlassian.net/browse/PSIRT-2797) | Yes |
| 11 | PRODSECRM-213 — Renewing Recently Expired Exceptions (RHOAI 3.5-ea.1) — exception-renewal precedent | JIRA | [PRODSECRM-213](https://redhat.atlassian.net/browse/PRODSECRM-213) | Yes |
| 12 | PRODSECRM-309 — RHOAI 3.6-ea.1/ea.2 Conforma exceptions: extended remediation timelines — exception-renewal precedent | JIRA | [PRODSECRM-309](https://redhat.atlassian.net/browse/PRODSECRM-309) | Yes |
| 13 | Conforma Exception Grouping Strategy (governance/guardrail reference) | Internal | [$RISK_DOCS_PATH-adjacent: docs/conforma-exception-grouping.md](/Users/ahaklik/projects/risk-platform-claude/risk-platform/docs/conforma-exception-grouping.md) | Yes |
| 14 | release-service-catalog PR (cited in ticket as "#2451"; link resolves to pull/245 — likely transcription error, see Data Gaps) | External | [https://github.com/konflux-ci/release-service-catalog/pull/245](https://github.com/konflux-ci/release-service-catalog/pull/245) | Unverified |
| 15 | release-service-catalog PR #2537 (global-override PR, explicitly out of scope of this exception) | External | [https://github.com/konflux-ci/release-service-catalog/pull/2537](https://github.com/konflux-ci/release-service-catalog/pull/2537) | Yes |
| 16 | CVE-2025-65637 VEX document (demonstrates CPE misattribution) | External | [https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-65637.json](https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-65637.json) | Unverified (cited by ticket author; not independently re-fetched this session) |
| 17 | RHSA-2026:6493 | External | [https://access.redhat.com/errata/RHSA-2026:6493](https://access.redhat.com/errata/RHSA-2026:6493) | Unverified |
| 18 | CVE-2025-65637 (NVD) | CVE | [https://nvd.nist.gov/vuln/detail/CVE-2025-65637](https://nvd.nist.gov/vuln/detail/CVE-2025-65637) | Yes |
