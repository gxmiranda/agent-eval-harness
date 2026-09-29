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
adversarial_mode: full
adversarial_disposition: MAX ROUNDS
input_sources:
  - type: interactive_session
    label: "Interactive Analysis (2026-09-03)"
    added: "2026-09-03"
---

# Risk Assessment: PRODSECRM-306

## Executive Summary [AI-GENERATED]

If Red Hat's RHEL package signing keys are compromised, the delivery pipeline cannot re-sign and re-publish existing RPM packages within a timeframe customers would expect — recovery estimates range from weeks (single-key packages via an untested auxiliary key path) to months (multi-key PQC packages requiring full rebuilds at a median 13.7-day build-to-ship time per package), during which Red Hat cannot ship CVE fixes for any affected RHEL release, exposing every enterprise customer to unpatched vulnerabilities and active harm if a Critical CVE coincides with the recovery window. Severity is rated **High** / **Unlikely** / **Major** — the triggering condition (uncontainable compromise forcing portfolio-wide key rotation) is a strict subset of the 15–30% annual pipeline compromise probability, and impact is RHEL-scoped with growing blast radius as PQC multi-key adoption increases; financial exposure is material but unquantified. The primary recommended action is to prioritize [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646) to remove the RPM immutability constraint and validate the existing auxiliary key rotation path. PSRR promotion is **not ready** — deferred pending financial quantification and named director+ risk owner; sibling risk [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) is the promotion candidate for the portfolio-wide framing.

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

**JIRA field discrepancy:** The JIRA Risk Probability field (`customfield_10642`) is set to "Very Likely," but the same reporter's (Jeremy West) ticket description states "Likelihood: Unlikely" and the SBAR he co-authored explicitly states "the likelihood of this happening is low." The JIRA field changelog confirms the value was set at issue creation (no subsequent manual changes; only two automated field changes appear in the history: ScriptRunner setting Risk Score Assessment, Automation for Jira setting Intelligence Requested). This is an internal discrepancy within the reporter's own submission. The most likely interpretation: "Risk Probability" in the PRODSECRM template may refer to the probability of needing to exercise recovery capability (very likely as PQC rollout progresses and attack sophistication increases), while the description's "Likelihood: Unlikely" refers to the probability of a signing key compromise event itself. This assessment uses the SBAR-sourced "Unlikely" rating for the compromise-event likelihood. The field value is noted but not overridden without reporter clarification.

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
| Severity | High | RHEL package delivery paralysis during recovery; inability to ship CVE fixes for 1+ months for multi-key packages; [RHEL SBAR](https://docs.google.com/document/d/1e9fmjsUmf0zK_K7Nl2hJaBc7KNeEwGBWJWbLUHsr3B8) quantified median 13.7-day build-to-ship time, P90 51.3 days. **Note:** build-to-ship time is one component of total recovery time; total recovery also includes detection/triage time, organizational decision latency (authority to authorize key rotation), key generation/rotation procedure, validation/testing, CDN propagation, and customer notification. Total recovery time is likely longer than build-to-ship alone. |
| Likelihood | Unlikely | HSM key material non-exportable; pipeline compromise estimated 15--30% annual probability ([Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) threat analysis) but this risk's triggering condition (uncontainable compromise) is a strict subset; long operational track record without key compromise (RHEL signing keys are described as "long-lived" with no fixed rotation schedule -- [PRODSECRM-306 description](https://redhat.atlassian.net/browse/PRODSECRM-306)); SBAR author explicitly rates likelihood as "low" |
| Impact | Major | RHEL-scoped (not full portfolio — [PRODSECRM-295](https://redhat.atlassian.net/browse/PRODSECRM-295) covers portfolio); existing single-key recovery path identified by SME (Stanislav Graf, [PRODSECRM-295 comment 2026-08-25](https://redhat.atlassian.net/browse/PRODSECRM-295)); auxiliary DR key exists but unvalidated at scale; multi-key proportion growing with PQC rollout |

### Rating Rationale

**Severity justification:**

High rather than Critical because: (a) SME input from Stanislav Graf (former signing key owner, 10 years) confirms that single-key packages (the current majority of the RHEL portfolio) can be re-signed without rebuilding -- "we have unsigned RPMs and we can sign them with new key and replace packages in pulp/CDN"; (b) an auxiliary disaster recovery key already exists and is distributed in products. **Important caveat:** This rating depends on the auxiliary key rotation path being functional at RHEL repository scale, but the controls assessment (Section 4, Control 2) rates this path as "Unvalidated." The severity rating therefore represents a best-available-evidence judgment based on SME confirmation of mechanism viability, not a confirmed operational capability. The rating would escalate to Critical if: the multi-key proportion exceeds 50% of the RHEL portfolio (PQC rollout trajectory), the auxiliary key path is confirmed non-functional at scale, or the single-key re-sign path fails when tested against the delivery pipeline (pulp/CDN/Satellite chain).

The two-bottleneck model established in the [PRODSECRM-295 Amendment R1](https://redhat.atlassian.net/browse/PRODSECRM-295) (2026-08-25) applies:

- **Bottleneck A -- Rebuild constraint:** Applies to multi-key (release2 + release4) packages where re-signing creates a same-NVR-different-content condition that breaks the delivery pipeline. The 13.7-day median build-to-ship time applies to this path. Tracked in [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646). The prerequisite investigation spike [RHELDST-42989](https://redhat.atlassian.net/browse/RHELDST-42989) ("Enable multi-sig RPMs in rhsm-pulp") remains in Refinement status with no assignee as of 2026-09-03. It defines three goals (cdn_path improvement for multi-key RPMs, IMA/PQC awareness in rhsm-pulp, and re-signed RPM support) but has not produced findings or follow-up JIRAs. This means the structural constraint that forces full rebuilds for multi-key packages is confirmed as unresolved with no active remediation in progress.
- **Bottleneck B — Delivery-chain re-publish:** Even for single-key re-signing without rebuild, pushing re-signed packages at scale through pulp/CDN/Satellite involves cached metadata invalidation, duplicate RPM handling, and CDN storage constraints. Technical decomposition in [RHELDST-43646 comments](https://redhat.atlassian.net/browse/RHELDST-43646) (Daniel Alley, Clemens Lang, Aug 2026) identifies three sub-problems: client metadata checksum invalidation, rhsm-pulp duplicate handling ([RHELDST-37824](https://redhat.atlassian.net/browse/RHELDST-37824)), and CDN layer issues (scope unknown).

**Likelihood justification:**

Unlikely because the risk assessed here is not "pipeline compromise" but specifically "signing key compromise requiring portfolio-wide rotation." The probability structure has three branches:

1. **No compromise** (base case): Pipeline security controls hold. HSM architecture prevents key export -- an attacker with signing infrastructure access can only use keys, not steal them.
2. **Containable compromise** (forged packages can be enumerated and individually blocklisted): Does not trigger the portfolio-wide rotation scenario. Customer impact is bounded to the forged packages. This branch does not require the mass re-sign/rebuild described in this assessment.
3. **Uncontainable compromise** (forged packages cannot be enumerated, forcing full key rotation): This is the scenario this risk assessment covers. It is a strict subset of the already-unlikely compromise scenario.

The [Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) estimates pipeline compromise at 15--30% annually (this figure's derivation methodology -- whether it is a point estimate, expert elicitation range, or threat-model output -- is not specified in the SBAR; the downstream analysis inherits this imprecision). However, this is the probability of *any* pipeline compromise (branch 2 + branch 3), not the probability of the uncontainable subset (branch 3 only). The conditional probability P(uncontainable | compromise) is not quantified in the SBAR but is expected to be low: most realistic attack scenarios (unauthorized signing of a small number of packages, compromised build input) produce enumerable forged packages. The HSM non-exportability means an attacker cannot create forged packages offline after losing access -- they must sign in real time while maintaining access, which limits the scope. Only a prolonged, undetected compromise where the attacker signs enough packages that enumeration becomes infeasible forces branch 3.

The combined probability of branch 3 is therefore substantially lower than the 15--30% pipeline figure. The "Unlikely" rating reflects this conditional probability, not a dismissal of the pipeline compromise estimate. [UNRESOLVED: The conditional probability P(uncontainable | compromise) is not quantified -- this is an acknowledged gap that weakens the likelihood rating's precision.] The likelihood would increase if: supply chain attack sophistication continues to increase (SolarWinds 2020, 3CX 2023, XZ Utils 2024 precedents), the number of authorized signers (168 per Portfolio SBAR) grows without context-aware verification, or a targeted state-level attack against RHEL signing infrastructure occurs.

**Impact justification:**

Major rather than Catastrophic because the assessment scope is RHEL-specific (not portfolio-wide, which is -295), and the single-key recovery path provides a partial mitigation for the majority of current packages. **Key scope note:** The release2 and release4 signing keys are described in the SBAR context as RHEL package signing keys. The [Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y) covers the broader portfolio of signing keys across Red Hat products; this assessment focuses on RHEL delivery pipeline recovery for the RHEL-specific release keys. [UNRESOLVED: Whether the release2/release4 keys are strictly RHEL-exclusive or shared with other products has not been independently verified. Key adjacency concerns: (1) RHEL CoreOS (RHCOS) is the mandatory node OS for OpenShift Container Platform -- if RHCOS content is signed with the same release keys, recovery paralysis extends to OpenShift cluster updates, expanding impact from RHEL subscriptions to Red Hat's strategic hybrid cloud platform. (2) Red Hat Universal Base Images (UBI) are built from RHEL packages -- if RHEL packages cannot be re-signed and re-published, UBI images cannot be rebuilt, cascading into every containerized application built on UBI base layers. (3) Satellite distributes RHEL content and may introduce an independent delivery-chain bottleneck. If shared, the impact scope may exceed RHEL-specific and the Major rating would need re-evaluation. PRODSECRM-295 covers the portfolio-wide framing.] However, concrete consequences if the risk materializes include: (a) inability to ship CVE fixes for RHEL for at minimum 2--3 days (P10 rebuild time) and realistically 2+ weeks (median); (b) all supported RHEL releases affected simultaneously, not just RHEL 10; (c) customer trust in Red Hat's RPM signature -- the fundamental assertion that shipped software is authentic -- materially damaged; (d) potential loss of FedRAMP continuous monitoring compliance for gov-cloud RHEL deployments; (e) **compound scenario risk:** if a Critical CVE is actively exploited during the recovery window, Red Hat cannot ship the fix for any affected RHEL release, transforming a recovery-time problem into active customer harm -- given continuous CVE volume, the probability of at least one Critical CVE coinciding with a multi-week recovery window is non-trivial.

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
| 3 | Regulatory compliance | Yes | **Regulatory scoping note:** CRA and FedRAMP frameworks were manually loaded by analyst override (rationale: CRA -- supply chain integrity relevance; FedRAMP -- incident response and key management controls). Automated applicability matrix triggers did not fire because the risk type is Operational, not Compliance. The regulatory mappings below are exploratory (Low confidence). |

**Regulatory Mapping: CRA — Art. 14 Reporting Obligations**

*Regulatory definition (verbatim, [Art. 14](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng#art_14)):* Manufacturers must submit an early warning within 24 hours of becoming aware of an actively exploited vulnerability contained in their product with digital elements, followed by a 72-hour notification and a 14-day final report to the designated CSIRT and ENISA. [VERIFIED via WebFetch 2026-09-03.]

*Product core functionality:* RHEL is a Linux-based operating system distributed as RPM packages signed with Red Hat's release keys. It is a "product with digital elements" under [Art. 3(1)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng#art_3) (software placed on the EU market in the course of commercial activity). Red Hat is the manufacturer under [Art. 3(12)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng#art_3).

*Explicit match test:* Art. 14 reporting is triggered by an "actively exploited vulnerability" in the *product*. CRA [Art. 3(40)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng#art_3) defines vulnerability as "a weakness, susceptibility or flaw of a product with digital elements that can be exploited by a cyber threat." A signing key compromise is an infrastructure-level event (HSMs, signing pipeline) — it is not a flaw *of* the product itself but rather a flaw in the manufacturer's internal infrastructure that *affects* the product's integrity assurance. Art. 14 therefore does not directly apply to the signing infrastructure compromise scenario. If forged packages containing actual product vulnerabilities are distributed, Art. 14 would apply to those vulnerabilities, not to the key compromise itself.

*Confidence:* Low (infrastructure vs. product distinction makes direct applicability unlikely).

**Regulatory Mapping: FedRAMP — Vulnerability Remediation Timelines**

*Regulatory definition:* FedRAMP operational requirements mandate vulnerability remediation within defined timelines (30 days for Critical/High, 90 days for Moderate, 180 days for Low). [UNVERIFIED — source text not retrieved; FedRAMP operational requirements not in loaded reference files (skeletons only). FedRAMP Vulnerability Scanning Requirements documentation returned HTTP 404.]

*Product core functionality:* RHEL is used as the base OS in FedRAMP-authorized cloud deployments by Cloud Service Providers (CSPs) serving US federal agencies. Under FedRAMP, the CSP (not Red Hat directly) holds the Authorization to Operate (ATO).

*Explicit match test:* FedRAMP remediation timelines apply to the CSP, not the upstream vendor. However, if Red Hat cannot ship CVE fixes during a key recovery period (2+ weeks median), CSPs using RHEL as their base OS cannot remediate RHEL-layer vulnerabilities within the required window, potentially putting their ATO at risk. The exposure is indirect: Red Hat → CSP → ATO. This is a supply chain dependency risk for FedRAMP-authorized CSPs, not a direct FedRAMP obligation on Red Hat.

*Confidence:* Low (indirect supply chain impact; remediation timelines UNVERIFIED). |
| 4 | Revenue / cost | Yes | Inability to ship CVE fixes would generate customer escalations, potential SLA breaches for premium support customers, and reputational damage likely resulting in customer attrition. The RHEL SBAR states: "We would almost certainly lose customers and be subject to various inquiries and investigations." Financial impact not yet quantified — this is a data gap. |
| 5 | Strategic roadmap | Yes | PQC transition program ([PRODSECRM-74](https://redhat.atlassian.net/browse/PRODSECRM-74)) is blocked by the same root cause — cannot achieve a fully PQ-signed RHEL without solving the rebuild/re-sign constraint. RHELDST-43646 is a shared dependency. |
| 6 | Product integrity | Yes | During the recovery period, customers cannot distinguish between legitimate Red Hat-signed packages and any potentially forged packages. No cryptographic revocation mechanism exists — manual blocklists are the only option. |
| 7 | Safety, privacy, and data integrity | Yes (indirect) | RHEL is deployed in safety-critical environments including industrial control systems, medical device infrastructure, automotive infotainment, and defense systems. While the signing key compromise itself does not directly cause a safety event, the inability to ship CVE fixes during the recovery window (2+ weeks median) means safety-critical RHEL deployments cannot receive security patches. If an actively exploited vulnerability targeting these environments coincides with the recovery window, the safety implications are direct. Rated as indirect because the harm requires a concurrent vulnerability, not the compromise alone. |

**Primary objective:** Product availability — the inability to ship security updates during recovery is the most concrete and immediately harmful consequence.

---

## Section 4: Current Mitigations [AI-GENERATED]

**Maps to:** JIRA comments (mitigation tracking)

### Controls in Place

| Control | Type | Effectiveness | Evidence |
|---------|------|--------------|----------|
| HSM key storage (nCipher, IAD2 + RDU2) | Preventive | Effective | Key material is non-exportable from HSMs. Attacker with infrastructure access can use keys to sign but cannot steal the key itself. Keys are long-lived with no fixed rotation schedule ([PRODSECRM-306 description](https://redhat.atlassian.net/browse/PRODSECRM-306)), indicating sustained operational use without compromise. ([Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y)) |
| Auxiliary disaster recovery key | Corrective | Unvalidated | Distributed in Red Hat products as a fallback if primary release key is compromised. SME (Stanislav Graf) confirms existence: "we tell customers that this auxiliary key is our disaster recovery key." Rotation path (release → auxiliary) has not been tested at scale. ([PRODSECRM-295 comment 2026-08-25](https://redhat.atlassian.net/browse/PRODSECRM-295)) |
| RHELWF-14251 fix (ET 4.113) | Corrective | Partially Effective | Prevents re-signing of inherited modular RPMs in Errata Tool, addressing the immediate PQC-triggered modular RPM re-signing incident. Does NOT address the broader key rotation scenario. ([Design doc](https://docs.google.com/document/d/1aj5-u8Ow6fzelWocL9qTfqUKLdxmBOdFW9kRJ-h1e28)) |
| RHELDST-37824 (duplicate RPM prevention in rhsm-pulp) | Preventive | Partially Effective | Prevents accidental co-existence of same-version-different-content RPMs. Status: Release Pending. However, mass re-signing would require temporarily bypassing this safeguard. ([RHELDST-37824](https://redhat.atlassian.net/browse/RHELDST-37824)) |
| Signing operation monitoring and audit logging | Detective | Unknown | [DATA GAP] The analysis has not assessed whether signing operations are monitored with anomaly detection (e.g., unusual signing volume, off-hours signing activity, unauthorized key usage). Detection capability directly affects the likelihood of prolonged undetected compromise (the prerequisite for the uncontainable compromise scenario, branch 3). If robust monitoring is in place, P(uncontainable \| compromise) decreases; if not, the Unlikely likelihood rating may be optimistic. The 168 authorized signers (per [Portfolio SBAR](https://docs.google.com/document/d/1PfICdeAMViux7mUZMvJ7BiWVlp0Xfi4cNyjvQx1DY4Y)) increase the attack surface for credential-based compromise. |

### Residual Exposure

After accounting for current controls, the following exposure remains:

1. **No tested portfolio-scale key rotation procedure.** The auxiliary key exists but has never been exercised for a mass rotation event. The single-key re-sign-and-replace path (Graf) works operationally for individual packages but is untested at RHEL repository scale (thousands of packages).

2. **Multi-key packages have no recovery path short of full rebuild.** Packages signed with both release2 and release4 (PQC) cannot be re-signed at the same NVR without breaking the delivery pipeline. This proportion is growing as PQC rollout continues.

3. **No cryptographic revocation mechanism.** If forged packages cannot be enumerated, there is no way to revoke trust in the compromised key's signatures. Manual customer-side blocklisting is the only option.

4. **Delivery-chain constraints are unquantified.** Even for single-key packages, the time to re-publish through pulp/CDN/Satellite at scale is unknown. Daniel Alley ([RHELDST-43646 comment](https://redhat.atlassian.net/browse/RHELDST-43646)) notes that metadata invalidation will cause temporary client errors regardless of approach.

5. **All supported RHEL releases affected simultaneously.** Recovery is not limited to RHEL 10 -- every supported release signed with the compromised key would require re-signing.

6. **Incident communications workstream not planned.** A signing key compromise requiring portfolio-wide rotation would necessitate a public advisory, coordination with ISACs (government and critical infrastructure customers), and customer communications at scale. This communications workstream runs in parallel with technical recovery and can itself introduce delays, errors, or additional reputational damage. No incident communication plan specific to key compromise exists in the assessed materials.

7. **Organizational decision latency unassessed.** Who has the authority to authorize a portfolio-wide key rotation? What is the decision authority chain? How long does it take to convene decision-makers, assess whether to rotate vs. surgically respond, and commit to a course of action? This organizational latency sits upstream of all technical recovery timelines and could dominate total recovery time. No decision authority or escalation path for key compromise is documented in the assessed materials.

---

## Section 5: Recommended Actions [AI-GENERATED]

**Maps to:** JIRA sub-tasks, action items

**Note:** Several action items below assign team-level owners rather than named individuals. For a High-severity risk, named individual owners are expected. The analyst should resolve team-level assignments to specific individuals during the analyst review step (Section: Analyst Assessment).

### Immediate (0--7 days)

- [ ] **Validate auxiliary key rotation path** -- **Owner:** Signing Infrastructure team lead (current key custodian -- verify with PSRD; Stanislav Graf is a former key owner who may provide SME input but may not have current access/authority) -- **Definition of done:** Documented confirmation of whether the release-to-auxiliary key rotation has ever been tested at scale, and if not, what would be required to test it.
- [ ] **Determine multi-key package proportion** — **Owner:** PSRD / Signing Team — **Definition of done:** Count of RHEL 10 z-stream packages currently dual-signed (release2 + release4) vs. single-signed (release2 only), to quantify the split recovery timeline.

### Short-Term (1–4 weeks)

- [ ] **Confirm Errata Tool re-sign path** — **Owner:** Errata/ET Team — **Definition of done:** Documented confirmation of whether the single-key re-sign-and-replace path works through Errata Tool (steps 5–6 in SBAR), or only at the pulp/CDN layer (skipping steps 5–6).
- [ ] **Prioritize RHELDST-43646** — **Owner:** Software Production Pipeline Team — **Definition of done:** [RHELDST-43646](https://redhat.atlassian.net/browse/RHELDST-43646) has an assigned owner, priority, and target milestone. The spike [RHELDST-42989](https://redhat.atlassian.net/browse/RHELDST-42989) (Refinement) should feed into this.
- [ ] **Map FedRAMP product coverage** — **Owner:** GovCloud Team — **Definition of done:** List of FedRAMP-authorized products that depend on release2/release4 signing keys, to scope regulatory incident response exposure.

### Long-Term (timeline uncertain -- see note)

- [ ] **RHELDST-43646 implementation** -- **Owner:** Software Production Pipeline Team + Satellite Team -- **Definition of done:** RHEL delivery pipeline supports RPM content changes (signature updates) without requiring NVR change and full rebuild. Per the RHEL SBAR recommendation (Option 4). **Timeline note:** The prerequisite investigation spike [RHELDST-42989](https://redhat.atlassian.net/browse/RHELDST-42989) remains in Refinement with no assignee as of 2026-09-03 and has not produced findings. A realistic implementation timeline cannot be estimated until the spike is completed and follow-up JIRAs are filed. The previous 1--3 month estimate was aspirational and is not evidence-based.
- [ ] **NVR-bump tooling (interim)** — **Owner:** PSRD — **Definition of done:** Custom tooling to bump revision of all latest versions in an RPM repository and re-sign without rebuilding from source (SBAR Option 3). Operates as an interim fallback until RHELDST-43646 is complete.
- [ ] **DR rotation drill** — **Owner:** Signing Infrastructure + PSRD — **Definition of done:** End-to-end test of auxiliary key rotation for a representative subset of RHEL packages (single-key and multi-key), with measured recovery time and documented issues.

### Data Gaps

| Gap | Owning Team | Action Needed | Priority |
|-----|-------------|---------------|----------|
| Auxiliary key rotation path test status | Signing Infrastructure (Vincent / Stanislav Graf) | Confirm whether release → auxiliary key rotation has ever been exercised at scale | High |
| Multi-key (release2 + release4) package proportion in RHEL 10 z-stream | PSRD / Signing Team | Count dual-signed vs. single-signed packages to quantify split recovery timeline | High |
| Errata Tool re-sign path scope | Errata/ET Team | Confirm whether single-key re-sign-and-replace works through ET or only at pulp/CDN layer | Medium |
| FedRAMP product-to-key mapping | GovCloud Team | Identify FedRAMP-authorized products depending on release2/release4 | Medium |
| Signing key scope (RHEL-exclusive vs. shared) | Signing Infrastructure / PSRD | Verify whether release2/release4 keys sign only RHEL packages or are shared with other products (RHCOS/OpenShift, Satellite, RHIVOS, etc.) -- affects impact scope. If RHCOS content uses the same keys, OpenShift is in scope. | High |
| Detection controls for signing operations | Signing Infrastructure / Security Engineering | Assess whether signing operations are monitored (anomaly detection, audit logging, unauthorized signing alerts). Detection capability directly affects likelihood of prolonged undetected compromise. | High |
| Satellite content view handling of re-signed RPMs | Satellite Content Management team | Test whether Satellite's content view pipeline treats a re-signed RPM (same NEVRA, different signature) as a new artifact or rejects it as a duplicate. If Satellite introduces an independent bottleneck, recovery timeline extends. | Medium |
| Financial impact quantification | ProdSec / Finance | Estimate revenue exposure from 1-month RHEL update paralysis: customer attrition rate, premium support SLA penalty exposure (specific contractual remediation timelines to be verified against standard Red Hat premium support agreements), and reputational damage multiplier. Required for PSRR promotion readiness (Requirement 1: quantified risk). | High |

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

**Action:** CONCUR

**Changes from AI recommendation:**
None on ratings or substance. Accept Shrike revisions as applied (5 rounds, 43 challenges resolved). Treatment: Mitigate via RHELDST-43646 + auxiliary key validation. PSRR: CONCUR on NOT READY — defer to PRODSECRM-295 as the portfolio-wide promotion candidate.

**Outstanding asks for risk owner (Ian Murphy):**

The following items remain unresolved from the adversarial review. Once the risk owner provides answers, this analysis will be refined via `/risk-amend` and ratings may be adjusted:

1. **Auxiliary key rotation path:** Has the release → auxiliary key rotation ever been tested at scale? What would be required to test it? (Route via Vincent / Stanislav Graf)
2. **Key scope:** Do release2/release4 keys sign only RHEL packages, or are they shared with RHCOS (OpenShift), UBI, or Satellite content? If shared, impact scope expands beyond RHEL and the Major rating needs re-evaluation.
3. **Multi-key proportion:** What percentage of RHEL 10 z-stream packages are currently dual-signed (release2 + release4)? This determines the split between the weeks (single-key) and months (multi-key) recovery timelines.
4. **Detection controls:** Are signing operations monitored with anomaly detection? Detection capability directly affects the likelihood of prolonged undetected compromise (the prerequisite for the uncontainable scenario). If monitoring is weak, the Unlikely rating may be optimistic.
5. **Named individual owners:** Action items currently have team-level owners. Please resolve to named individuals for: RHELDST-43646 prioritization, auxiliary key validation, and DR rotation drill.

**FedRAMP remediation timelines (30/90/180 days) remain UNVERIFIED** — source documentation returned HTTP 404. Not a risk owner ask; will be verified independently.

**Sign-off:** Aleksandra Haklik | 2026-09-03

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
| 14 | CRA Art. 3 Definitions | Regulation | [regulatory/cra/definitions.md](/Users/ahaklik/projects/risk-platform/regulatory/cra/definitions.md) | Yes |
| 15 | FedRAMP Definitions | Regulation | [regulatory/fedramp/definitions.md](/Users/ahaklik/projects/risk-platform/regulatory/fedramp/definitions.md) | Yes |
| 16 | FedRAMP Impact Levels | Regulation | [regulatory/fedramp/impact-levels.md](/Users/ahaklik/projects/risk-platform/regulatory/fedramp/impact-levels.md) | Yes |
