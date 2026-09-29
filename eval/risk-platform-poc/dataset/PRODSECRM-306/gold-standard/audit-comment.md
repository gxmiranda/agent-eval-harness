---
## Risk Assessment -- PRODSECRM-306
**Analyst:** Aleksandra Haklik | **Date:** 2026-09-03T10:45:00Z
**Tool:** Claude Code /risk-assess v{version} | **Mode:** Interactive
**Session:** 2026-09-03-081419
**Full analysis:** [PRODSECRM-306/2026-09-03-081419/analysis.md](https://gitlab.cee.redhat.com/imurphy/risk-docs/-/blob/main/sessions/PRODSECRM-306/2026-09-03-081419/analysis.md)

### Evidence Gathered
- **JIRA:** status, priority, comments, linked issues (8 issues visited, depth 3, 128 URLs extracted)
- **Gmail:** 0 threads (none)
- **Drive:** 0 documents (none)
- **CVE Intelligence:** No CVEs detected
- **External:** None
- **Regulatory Reference:** 2 frameworks loaded (cra, fedramp), ref SHA be36031b, 3 staleness warnings

### AI Analysis [AI-GENERATED]

| Field | AI Recommendation | Confidence |
|-------|-------------------|------------|
| Severity | High | medium |
| Likelihood | Unlikely | medium |
| Impact | Major | medium |

**Key findings:** RHEL's delivery pipeline cannot re-sign existing RPM packages without a full rebuild from source (median 13.7 days per package, P90 51.3 days). SME input (Stanislav Graf) identifies a split: single-key packages (current majority) may be re-signable via an existing auxiliary DR key, but multi-key packages (release2 + release4/PQC, growing proportion) require full rebuilds. Neither path has been tested at portfolio scale. No cryptographic revocation mechanism exists. 5 rounds of adversarial review (43 challenges, all resolved) confirmed ratings and added a three-branch probability model, compound scenario analysis, and 8 data gaps.

**Why this matters:** A signing key compromise would paralyze Red Hat's ability to ship CVE fixes for all supported RHEL releases for weeks to months. If a Critical CVE coincides with the recovery window, customers face active harm with no available patch. The PQC transition is increasing the multi-key proportion, worsening recovery timelines over time. RHELDST-43646 (the pipeline fix) remains in New status with no assignee.

**Recommended mitigations:**
1. Prioritize RHELDST-43646 (remove RPM immutability constraint) -- Owner: Software Production Pipeline Team
2. Validate auxiliary key rotation path at scale -- Owner: Signing Infrastructure (via Vincent / Stanislav Graf)
3. Build NVR-bump interim tooling (SBAR Option 3) -- Owner: PSRD
4. Execute DR rotation drill on representative RHEL package subset -- Owner: Signing Infrastructure + PSRD

**Outstanding asks for risk owner:** Auxiliary key test status, key scope (RHEL-exclusive vs. shared), multi-key package proportion, detection controls assessment, named individual owners for action items. Analysis will be refined via /risk-amend once answers are received.

**Escalation recommendation:** PSRR promotion NOT READY for PRODSECRM-306 (RHEL-scoped subset). Sibling risk PRODSECRM-295 is the portfolio-wide promotion candidate, deferred pending financial quantification and director+ risk owner.

### Adversarial Review [AI-GENERATED]
- **Mode:** Full loop (5 rounds)
- **Challenges raised:** 43
- **Challenges resolved:** 43
- **Final disposition:** MAX ROUNDS
- **Rating changes from review:** None

### Analyst Decision [HUMAN]
**Action:** CONCUR
**Changes from AI recommendation:** None on ratings or substance. Accept Shrike revisions as applied (5 rounds, 43 challenges resolved). Treatment: Mitigate via RHELDST-43646 + auxiliary key validation. PSRR: CONCUR on NOT READY — defer to PRODSECRM-295 as the portfolio-wide promotion candidate.
**Rationale for overrides:** N/A
**Sign-off:** Aleksandra Haklik | 2026-09-03

_Note: "CONCUR" records the analyst's concurrence with the AI recommendation. This is NOT a risk acceptance decision -- risk acceptance is a business owner decision, not an analyst action._
---