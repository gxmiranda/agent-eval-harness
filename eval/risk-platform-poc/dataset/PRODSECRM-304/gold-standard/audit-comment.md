---
## Risk Assessment -- PRODSECRM-304
**Analyst:** Aleksandra Haklik | **Date:** 2026-09-04T08:30:00Z
**Tool:** Claude Code /risk-assess v{version} | **Mode:** Interactive
**Session:** 2026-09-02-125403
**Full analysis:** [PRODSECRM-304/2026-09-02-125403/analysis.md](https://gitlab.cee.redhat.com/imurphy/risk-docs/-/blob/main/sessions/PRODSECRM-304/2026-09-02-125403/analysis.md)

### Evidence Gathered
- **JIRA:** status, priority, comments, linked issues (1 issues visited, depth 0, 0 URLs extracted)
- **Gmail:** 0 threads (none)
- **Drive:** 0 documents (none)
- **CVE Intelligence:** No CVEs detected
- **External:** None

### AI Analysis [AI-GENERATED]

| Field | AI Recommendation | Confidence |
|-------|-------------------|------------|
| Severity | Medium | medium |
| Likelihood | Unlikely | medium |
| Impact | Moderate | medium |

**Key findings:** Supply chain exception for OKP to consume ibm-granite/granite-embedding-30m-english from HuggingFace at build time. No draft EC Policy YAML or SHA256 pinning attached to the ticket. The RHEL AI precedent's scanning pipeline has documented gaps (PRODSECRM-118: Snyk scans pipeline files not model files, ClamAV fails >2GB, Clair times out — confirmed current April 2026). The prior OLS exception (-227) named OKP internalization as the remediation, but -227 was closed as duplicate of an unrelated ticket (-226, hermetic building) and the internalization is tracked only in RHOKP-1681 (status: To Do, not started).

**Why this matters:** If a compromised model ships in OKP, customers receive retrieval results steered by an attacker-chosen embedding space with no detection mechanism. The model itself is low-threat (30M-param safetensors, no executable code), but the governance gaps — missing artifact, orphaned remediation, unvalidated scanning — mean the approval process cannot confirm supply chain integrity. Impact deferred pending OKP team confirmation of content domain (general documentation vs. security-relevant content).

**Recommended mitigations:**
1. Produce draft EC Policy YAML with repo-level + sha256 pinning — Owner: OKP team (Paula Wambui / mclayton)
2. Document compensating controls for PRODSECRM-118 scanning gaps — Owner: OKP team + PSAI
3. Cross-reference -227/226 remediation status — Owner: ProdSec / OKP team
4. Complete internalization migration (RHOKP-1681) — Owner: OKP team (Jared Sprague)

**Escalation recommendation:** PSRR promotion NOT WARRANTED. PRODSECRM-118 is the escalation vehicle for the systemic model supply chain problem.

### Adversarial Review [AI-GENERATED]
- **Mode:** full (escalated from garth)
- **Challenges raised:** 20
- **Challenges resolved:** 16
- **Final disposition:** MAX ROUNDS
- **Rating changes from review:** Medium → High (Garth escalation); analyst overrode back to Medium (see Analyst Decision)

### Analyst Decision [HUMAN]
**Action:** MODIFY
**Changes from AI recommendation:** AI recommended High severity. Analyst changed to **Medium** because High conflates a bounded product exception (standalone factors: stalled remediation, missing EC Policy artifact) with the systemic PRODSECRM-118 program risk (scanning gaps, unowned AIBOM work). The scanning gaps are real but they are -118's problem, not -304's. -304's standalone severity is Medium: the submission is directionally sound, has RHEL AI precedent, and the target model (30M-param safetensors embedding) has a bounded threat surface. The team hasn't yet produced the EC Policy artifact or confirmed security-relevant use cases, which are governance gaps, not architectural ones.
**Rationale for overrides:** N/A
**Sign-off:** Aleksandra Haklik | 2026-09-04

_Note: "CONCUR" records the analyst's concurrence with the AI recommendation. This is NOT a risk acceptance decision -- risk acceptance is a business owner decision, not an analyst action._
---