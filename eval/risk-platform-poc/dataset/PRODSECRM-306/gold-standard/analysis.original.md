---
jira_key: "PRODSECRM-306"
title: "Slow recovery from signing key compromise"
status: draft
severity: "High"
likelihood: "Unlikely"
impact: "Major"
created: "2026-09-03"
updated: "2026-09-03"
analyst: "Aleksandra Haklik"
session_id: "2026-09-03-081419"
adversarial_mode: pending
adversarial_disposition: pending
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-03)"
    added: "2026-09-03"
---

# Risk Assessment: PRODSECRM-306

## Executive Summary [AI-GENERATED]

If Red Hat's RHEL package signing keys are compromised, the delivery pipeline cannot re-sign and re-publish existing RPM packages within a timeframe customers would expect — current estimates range from weeks (for single-key packages using an untested auxiliary key path) to months (for multi-key PQC packages requiring full rebuilds, with a median build-to-ship time of 13.7 days per package). During recovery, Red Hat would be unable to ship CVE fixes for any affected RHEL release, directly exposing every enterprise customer running RHEL to unpatched vulnerabilities. Severity is rated **High** with **Unlikely** likelihood (HSM key material is non-exportable, pipeline compromise probability estimated at 15–30% annually by portfolio SBAR) and **Major** impact (RHEL-scoped recovery paralysis with growing blast radius as PQC multi-key adoption increases). The primary recommended action is to prioritize [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646) to remove the RPM immutability constraint and validate the existing auxiliary key rotation path. PSRR promotion is **not ready** — deferred pending financial quantification and named director+ risk owner; sibling risk [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) is the promotion candidate for the portfolio-wide framing.

---

## Section 1: Risk Identification [AI-GENERATED]

**Maps to:** JIRA Summary, Description

| Field | Value |
|-------|-------|
| Risk Type | Operational |
| Title | RHEL delivery pipeline cannot recover from signing key compromise in a reasonable timeframe |
| Description | Red Hat's RHEL RPM delivery pipeline structurally prevents re-signing existing packages without a full rebuild from source. In a signing key compromise scenario, all supported RHEL releases would require complete rebuilds, with observed build-to-ship times making timely recovery infeasible. |

**Context:**

This risk was filed by Jeremy West (PSRD) on 2026-09-02 as [PRODSECRM-306](https://redhat.atlassian.net/browse/PRODSECRM-306), with Ian Murphy as assignee. It originates from the same root cause identified in the [RHEL SBAR](https://docs.google.com/document/d/1e9fmjsUmf0zK_K7Nl2hJaBc7KNeEwGBWJWbLUHsr3B8) (Jeremy West / Clemens Lang, Aug 2026) and the [Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) (Emily Fox, Aug 2026). The risk sits within a broader program of work on signing infrastructure modernization, with sibling risk [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) covering portfolio-wide key rotation capability.

The risk was prompted by real operational incidents: the PQC transition to release4 (ML-DSA-87 & Ed448) introduced multi-key signing for modular RPMs, which caused pulp, CDN, and customer-facing failures when the delivery pipeline encountered the same NVR with different signatures ([RHELDST-37695](https://redhat.atlassian.net/browse/RHELDST-37695), 203 comments, Blocker priority — resolved). The fix for the immediate modular RPM re-signing issue was implemented in Errata Tool 4.113 ([RHELWF-14251](https://redhat.atlassian.net/browse/RHELWF-14251)), but the underlying pipeline immutability constraint remains.

**JIRA field discrepancy:** The JIRA Risk Probability field is set to "Very Likely," but the ticket description states "Likelihood: Unlikely" and the SBAR explicitly states "the likelihood of this happening is low." This assessment uses the SBAR-sourced and description-sourced "Unlikely" rating. The JIRA field value appears to be a data entry error or refers to a different dimension.

### Supplementary Intelligence Sources [HUMAN]

| Source | Key Facts | Referenced Issues/Docs |
|--------|-----------|----------------------|
| *To be populated by analyst* | | |

---

## Section 2: Risk Assessment [AI-GENERATED]

**Maps to:** JIRA Priority, custom fields

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | High | RHEL package delivery paralysis during recovery; inability to ship CVE fixes for 1+ months for multi-key packages; [RHEL SBAR](https://docs.google.com/document/d/1e9fmjsUmf0zK_K7Nl2hJaBc7KNeEwGBWJWbLUHsr3B8) quantified median 13.7-day build-to-ship time, P90 51.3 days |
| Likelihood | Unlikely | HSM key material non-exportable; pipeline compromise estimated 15–30% annual probability ([Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) threat analysis); 19-year operational track record without key compromise; SBAR author explicitly rates likelihood as "low" |
| Impact | Major | RHEL-scoped (not full portfolio — [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) covers portfolio); existing single-key recovery path identified by SME (Stanislav Graf, [PRODSECRM-295 comment 2026-08-25](https://redhat.atlassian.net/browse/PRODSECRM-295)); auxiliary DR key exists but unvalidated at scale; multi-key proportion growing with PQC rollout |

### Rating Rationale

**Severity justification:**

High rather than Critical because: (a) SME input from Stanislav Graf (former signing key owner, 10 years) confirms that single-key packages (the current majority of the RHEL portfolio) can be re-signed without rebuilding — "we have unsigned RPMs and we can sign them with new key and replace packages in pulp/CDN"; (b) an auxiliary disaster recovery key already exists and is distributed in products. The rating would escalate to Critical if the multi-key proportion exceeds 50% of the RHEL portfolio (PQC rollout trajectory) or if the auxiliary key path is confirmed non-functional at scale.

The two-bottleneck model established in the [PRODSECRM-295 Amendment R1](https://redhat.atlassian.net/browse/PRODSECRM-295) (2026-08-25) applies:

- **Bottleneck A — Rebuild constraint:** Applies to multi-key (release2 + release4) packages where re-signing creates a same-NVR-different-content condition that breaks the delivery pipeline. The 13.7-day median build-to-ship time applies to this path. Tracked in [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646).
- **Bottleneck B — Delivery-chain re-publish:** Even for single-key re-signing without rebuild, pushing re-signed packages at scale through pulp/CDN/Satellite involves cached metadata invalidation, duplicate RPM handling, and CDN storage constraints. Technical decomposition in [RHELDST-43646 comments](https://redhat.atlassian.net/browse/RHELDST-43646) (Daniel Alley, Clemens Lang, Aug 2026) identifies three sub-problems: client metadata checksum invalidation, rhsm-pulp duplicate handling ([RHELDST-37824](https://redhat.atlassian.net/browse/RHELDST-37824)), and CDN layer issues (scope unknown).

**Likelihood justification:**

Unlikely because: (a) HSM architecture prevents key export — an attacker with signing infrastructure access can only use keys, not steal them; (b) the specific scenario requiring portfolio-wide key rotation (inability to enumerate forged packages) is a subset of the already-unlikely compromise scenario; (c) no revocation mechanism exists, so only an uncontainable compromise forces rotation. The likelihood would increase if: supply chain attack sophistication continues to increase (SolarWinds 2020, 3CX 2023, XZ Utils 2024 precedents), the number of authorized signers (168 per Portfolio SBAR) grows without context-aware verification, or a targeted state-level attack against RHEL signing infrastructure occurs.

**Impact justification:**

Major rather than Catastrophic because the assessment scope is RHEL-specific (not portfolio-wide, which is -295), and the single-key recovery path provides a partial mitigation for the majority of current packages. However, concrete consequences if the risk materializes include: (a) inability to ship CVE fixes for RHEL for at minimum 2–3 days (P10 rebuild time) and realistically 2+ weeks (median); (b) all supported RHEL releases affected simultaneously, not just RHEL 10; (c) customer trust in Red Hat's RPM signature — the fundamental assertion that shipped software is authentic — materially damaged; (d) potential loss of FedRAMP continuous monitoring compliance for gov-cloud RHEL deployments.

### CVE Landscape

No CVE associations identified for this risk. The risk concerns signing infrastructure recovery capability, not a specific vulnerability.

**Data Source:** CVE intelligence unavailable — no CVEs detected in JIRA fields or working file.

---

## Section 3: Objective Alignment [AI-GENERATED]

**Maps to:** Risk Council governance model — 7 risk objectives

| # | Objective | Affected? | Explanation |
|---|-----------|-----------|-------------|
| 1 | Product availability | Yes | RHEL cannot ship updates (CVE fixes, errata, z-stream releases) during key rotation recovery. Estimated minimum 2–3 days (P10), median ~2 weeks, worst case months. All supported RHEL releases affected simultaneously. |
| 2 | Customer trust | Yes | RPM signature is the foundational trust assertion. A compromised key with no timely recovery undermines customer confidence in the authenticity and integrity of every package signed with that key. |
| 3 | Regulatory compliance | Yes | FedRAMP-authorized RHEL deployments have incident response and continuous monitoring requirements (NIST SP 800-53 IR family). Inability to patch within expected remediation windows may breach authorization conditions. CRA Art. 14 reporting relevance is contextual (infrastructure compromise → product impact chain is indirect). |
| 4 | Revenue / cost | Yes | Inability to ship CVE fixes would generate customer escalations, potential SLA breaches for premium support customers, and reputational damage likely resulting in customer attrition. The RHEL SBAR states: "We would almost certainly lose customers and be subject to various inquiries and investigations." Financial impact not yet quantified — this is a data gap. |
| 5 | Strategic roadmap | Yes | PQC transition program ([PRODSECRM-74](https://redhat.atlassian.net/browse/PRODSECRM-74)) is blocked by the same root cause — cannot achieve a fully PQ-signed RHEL without solving the rebuild/re-sign constraint. RHELDST-43646 is a shared dependency. |
| 6 | Product integrity | Yes | During the recovery period, customers cannot distinguish between legitimate Red Hat-signed packages and any potentially forged packages. No cryptographic revocation mechanism exists — manual blocklists are the only option. |
| 7 | Safety, privacy, and data integrity | No | No direct safety, privacy, or personal data implications specific to this risk. |

**Primary objective:** Product availability — the inability to ship security updates during recovery is the most concrete and immediately harmful consequence.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| HSM key storage (nCipher, IAD2 + RDU2) | Preventive | Effective | Key material is non-exportable from HSMs. Attacker with infrastructure access can use keys to sign but cannot steal the key itself. 19-year operational track record. ([Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y)) |
| Auxiliary disaster recovery key | Corrective | Unvalidated | Distributed in Red Hat products as a fallback if primary release key is compromised. SME (Stanislav Graf) confirms existence: "we tell customers that this auxiliary key is our disaster recovery key." Rotation path (release → auxiliary) has not been tested at scale. ([PRODSECRM-295 comment 2026-08-25](https://redhat.atlassian.net/browse/PRODSECRM-295)) |
| RHELWF-14251 fix (ET 4.113) | Corrective | Partially Effective | Prevents re-signing of inherited modular RPMs in Errata Tool, addressing the immediate PQC-triggered modular RPM re-signing incident. Does NOT address the broader key rotation scenario. ([Design doc](https://docs.google.com/document/d/1aj5-u8Ow6fzelWocL9qTfqUKLdxmBOdFW9kRJ-h1e28)) |
| RHELDST-37824 (duplicate RPM prevention in rhsm-pulp) | Preventive | Partially Effective | Prevents accidental co-existence of same-version-different-content RPMs. Status: Release Pending. However, mass re-signing would require temporarily bypassing this safeguard. ([RHELDST-37824](https://redhat.atlassian.net/browse/RHELDST-37824)) |

### Residual Exposure

After accounting for current controls, the following exposure remains:

1. **No tested portfolio-scale key rotation procedure.** The auxiliary key exists but has never been exercised for a mass rotation event. The single-key re-sign-and-replace path (Graf) works operationally for individual packages but is untested at RHEL repository scale (thousands of packages).

2. **Multi-key packages have no recovery path short of full rebuild.** Packages signed with both release2 and release4 (PQC) cannot be re-signed at the same NVR without breaking the delivery pipeline. This proportion is growing as PQC rollout continues.

3. **No cryptographic revocation mechanism.** If forged packages cannot be enumerated, there is no way to revoke trust in the compromised key's signatures. Manual customer-side blocklisting is the only option.

4. **Delivery-chain constraints are unquantified.** Even for single-key packages, the time to re-publish through pulp/CDN/Satellite at scale is unknown. Daniel Alley ([RHELDST-43646 comment](https://redhat.atlassian.net/browse/RHELDST-43646)) notes that metadata invalidation will cause temporary client errors regardless of approach.

5. **All supported RHEL releases affected simultaneously.** Recovery is not limited to RHEL 10 — every supported release signed with the compromised key would require re-signing.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

### Immediate (0–7 days)

- [ ] **Validate auxiliary key rotation path** — **Owner:** Stanislav Graf / Vincent (Signing Infrastructure) — **Definition of done:** Documented confirmation of whether the release → auxiliary key rotation has ever been tested at scale, and if not, what would be required to test it.
- [ ] **Determine multi-key package proportion** — **Owner:** PSRD / Signing Team — **Definition of done:** Count of RHEL 10 z-stream packages currently dual-signed (release2 + release4) vs. single-signed (release2 only), to quantify the split recovery timeline.

### Short-Term (1–4 weeks)

- [ ] **Confirm Errata Tool re-sign path** — **Owner:** Errata/ET Team — **Definition of done:** Documented confirmation of whether the single-key re-sign-and-replace path works through Errata Tool (steps 5–6 in SBAR), or only at the pulp/CDN layer (skipping steps 5–6).
- [ ] **Prioritize RHELDST-43646** — **Owner:** Software Production Pipeline Team — **Definition of done:** [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646) has an assigned owner, priority, and target milestone. The spike [RHELDST-42989](https://redhat.atlassian.net/browse/RHELDST-42989) (Refinement) should feed into this.
- [ ] **Map FedRAMP product coverage** — **Owner:** GovCloud Team — **Definition of done:** List of FedRAMP-authorized products that depend on release2/release4 signing keys, to scope regulatory incident response exposure.

### Long-Term (1–3 months)

- [ ] **RHELDST-43646 implementation** — **Owner:** Software Production Pipeline Team + Satellite Team — **Definition of done:** RHEL delivery pipeline supports RPM content changes (signature updates) without requiring NVR change and full rebuild. Per the RHEL SBAR recommendation (Option 4).
- [ ] **NVR-bump tooling (interim)** — **Owner:** PSRD — **Definition of done:** Custom tooling to bump revision of all latest versions in an RPM repository and re-sign without rebuilding from source (SBAR Option 3). Operates as an interim fallback until RHELDST-43646 is complete.
- [ ] **DR rotation drill** — **Owner:** Signing Infrastructure + PSRD — **Definition of done:** End-to-end test of auxiliary key rotation for a representative subset of RHEL packages (single-key and multi-key), with measured recovery time and documented issues.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Auxiliary key rotation path test status | Signing Infrastructure (Vincent / Stanislav Graf) | Confirm whether release → auxiliary key rotation has ever been exercised at scale | High |
| Multi-key (release2 + release4) package proportion in RHEL 10 z-stream | PSRD / Signing Team | Count dual-signed vs. single-signed packages to quantify split recovery timeline | High |
| Errata Tool re-sign path scope | Errata/ET Team | Confirm whether single-key re-sign-and-replace works through ET or only at pulp/CDN layer | Medium |
| FedRAMP product-to-key mapping | GovCloud Team | Identify FedRAMP-authorized products depending on release2/release4 | Medium |
| Financial impact quantification | ProdSec / Finance | Estimate revenue exposure from 1-month RHEL update paralysis (customer attrition, SLA penalties) | Medium |

### Conditional Acceptance Prerequisites

N/A — not an acceptance decision. Recommended posture is **Mitigate** via RHELDST-43646 (primary) and auxiliary key validation (fallback).

---

## Section 6: Escalation Analysis [AI-GENERATED]

**Maps to:** PSRR issue creation, PRODSECRM-to-PSRR link

### PSRR Promotion Assessment

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk (concrete numbers) | Partial | Recovery timelines quantified (13.7-day median, P90 51.3d, P99 111.8d). Financial impact not quantified. |
| 2 | Actionable path (systemic fix) | Yes | RHELDST-43646 (RPM immutability removal), Portfolio SBAR 3-phase program, NVR-bump interim tooling |
| 3 | Context provided (summary + recommendation) | Yes | Two SBARs, JIRA graph with 8 issues and 272 comments, SME input |
| 4 | Tied to an objective | Yes | Product availability (primary), customer trust, product integrity |
| 5 | Named accountable risk owner (director+) | No | Assignee is Ian Murphy (ProdSec lead). No director+ risk owner named for the delivery pipeline dependency. |
| 6 | Consequence of inaction (6–12 month degradation) | Yes | PQC rollout increasing multi-key proportion → recovery time worsens. No rotation capability tested → preparedness degrades with time. |
| 7 | Risk posture requested | Yes | Mitigate via RHELDST-43646 + auxiliary key validation |
| 8 | Acceptance timebox | N/A | Not an acceptance request |

**Promotion recommendation:** NOT READY

**Rationale:** PRODSECRM-306 is a RHEL-scoped subset of [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295), which is the portfolio-wide signing key governance risk and the appropriate PSRR promotion candidate. -295 was assessed as a PSRR promotion candidate (5/8 requirements met, deferred pending financial quantification and director+ risk owner — [PRODSECRM-295 audit comment 2026-08-24](https://redhat.atlassian.net/browse/PRODSECRM-295)). Promoting -306 separately would create duplicate executive register entries for the same root cause. The recommended path is to promote -295 when financial framing and risk owner are resolved, with -306's RHEL-specific recovery timeline data incorporated as supporting evidence.

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
| intelligence.json | JIRA graph traversal: 8 issues, 272 comments, 128 URLs (depth 3) | 2026-09-03 |

---

## Sources

| # | Source | Type | Link | Verified |
|---|--------|------|------|----------|
| 1 | PRODSECRM-306 (primary risk) | JIRA | [PRODSECRM-306](https://redhat.atlassian.net/browse/PRODSECRM-306) | Yes |
| 2 | PRODSECRM-295 (sibling: portfolio-wide key rotation) | JIRA | [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) | Yes |
| 3 | PRODSECRM-74 (sibling: PQC Sigstore capability) | JIRA | [PRODSECRM-74](https://redhat.atlassian.net/browse/PRODSECRM-74) | Yes |
| 4 | RHELDST-43646 (RPM immutability fix epic) | JIRA | [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646) | Yes |
| 5 | RHELDST-42989 (multi-sig RPMs spike) | JIRA | [RHELDST-42989](https://redhat.atlassian.net/browse/RHELDST-42989) | Yes |
| 6 | RHELDST-37824 (duplicate RPM prevention in rhsm-pulp) | JIRA | [RHELDST-37824](https://redhat.atlassian.net/browse/RHELDST-37824) | Yes |
| 7 | RHELWF-14251 (modular RPM re-signing fix, Closed) | JIRA | [RHELWF-14251](https://redhat.atlassian.net/browse/RHELWF-14251) | Yes |
| 8 | RHELDST-37695 (RPM checksum validation incident, Closed) | JIRA | [RHELDST-37695](https://redhat.atlassian.net/browse/RHELDST-37695) | Yes |
| 9 | RHELDST-38946 (remediation procedure investigation, Resolved) | JIRA | [RHELDST-38946](https://redhat.atlassian.net/browse/RHELDST-38946) | Yes |
| 10 | RHELDST-43495 (KonfluxSource multi-sig RPMs) | JIRA | [RHELDST-43495](https://redhat.atlassian.net/browse/RHELDST-43495) | Yes |
| 11 | RHEL SBAR: Slow recovery from key compromise in RHEL | Drive | [Google Doc](https://docs.google.com/document/d/1e9fmjsUmf0zK_K7Nl2hJaBc7KNeEwGBWJWbLUHsr3B8) | Yes |
| 12 | Portfolio SBAR: Product Security Signing Workflow and Key Management Capabilities | Drive | [Google Doc](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) | Yes |
| 13 | Design doc: Prevent re-signing of inherited modular RPMs in Errata Tool | Drive | [Google Doc](https://docs.google.com/document/d/1aj5-u8Ow6fzelWocL9qTfqUKLdxmBOdFW9kRJ-h1e28) | Yes |
| 14 | CRA Art. 3 Definitions | Regulation | [regulatory/cra/definitions.md](~/projects/risk-platform/regulatory/cra/definitions.md) | Yes |
| 15 | FedRAMP Definitions | Regulation | [regulatory/fedramp/definitions.md](~/projects/risk-platform/regulatory/fedramp/definitions.md) | Yes |
| 16 | FedRAMP Impact Levels | Regulation | [regulatory/fedramp/impact-levels.md](~/projects/risk-platform/regulatory/fedramp/impact-levels.md) | Yes |
