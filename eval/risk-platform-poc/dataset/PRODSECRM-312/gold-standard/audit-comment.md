---

## Risk Assessment -- PRODSECRM-312

**Analyst:** Aleksandra Haklik | **Date:** 2026-09-14T11:50:00Z
**Tool:** Claude Code /risk-assess | **Mode:** Interactive
**Session:** 2026-09-14-093350
**Full analysis:** [PRODSECRM-312/2026-09-14-093350/analysis.md](https://gitlab.cee.redhat.com/imurphy/risk-docs/-/blob/main/sessions/PRODSECRM-312/2026-09-14-093350/analysis.md)

### Evidence Gathered

- **JIRA:** status, priority, comments, linked issues (30 issues visited, depth 3, 128 URLs extracted)
- **Gmail:** 0 threads (none)
- **Drive:** 0 documents (none)
- **CVE Intelligence:** No CVEs detected
- **External:** None

### AI Analysis [AI-GENERATED]

| Field | AI Recommendation | Confidence |
|-------|-------------------|------------|
| Severity | High | medium |
| Likelihood | Likely | medium |
| Impact | Major | medium |

**Key findings:**

1. Conforma has no mechanism to scope a global allowed key to specific teams/products -- adding these 5 keys affects every Konflux-onboarded product, not just RHOAI
2. Only 1 of 5 vendor legal agreements is confirmed (Mellanox); 4 remain In Progress after 3+ months
3. AIPCC sourcing abandoned for 3 of 5 vendors (CentOS, Fedora/EPEL, Mellanox -- all "Won't Do"), making dependencies persistent

**Why this matters:** Approving the global allowed_list request would silently disable a build integrity control for every Red Hat product built through Konflux. A proven per-product alternative exists (AMD/NVIDIA EnterpriseContractPolicy precedent via MR !19223) that provides equivalent operational relief without the global blast radius.

**Recommended mitigations:**

1. Engage with requestor, then decline global allowed_list request -- **Owner:** ProdSec (Austin Kimbrell / Marek Baluch), **Timeline:** 0-7 days
2. Extend per-product EnterpriseContractPolicy exceptions for all 5 keys (AMD/NVIDIA pattern) -- **Owner:** Release Engineering (Chris Kodama), **Timeline:** 1-4 weeks
3. Quantify Konflux blast radius (critical data gap for PSRR promotion) -- **Owner:** Release Engineering, **Timeline:** 1-2 weeks

**Escalation recommendation:** PSRR escalation is warranted, conditional on quantifying the Konflux blast radius, given the corrected severity and persistent nature of the dependencies

### Adversarial Review [AI-GENERATED]

- **Mode:** full (escalated from garth)
- **Challenges raised:** 22
- **Challenges resolved:** 20
- **Final disposition:** EXHAUSTED
- **Rating changes from review:** Severity Medium→High, Impact Moderate→Major, PSRR Not Warranted→Warranted (conditional)

### Analyst Decision [HUMAN]

**Action:** CONCUR
**Changes from AI recommendation:** None -- concurred as-is.
**Rationale for overrides:** N/A
**Sign-off:** Aleksandra Haklik | 2026-09-14

*Note: "CONCUR" records the analyst's concurrence with the AI recommendation. This is NOT a risk acceptance decision -- risk acceptance is a business owner decision, not an analyst action.*

---
