h2. Risk Assessment -- [PRODSECRM-309]

*Analyst:* Aleksandra Haklik | *Date:* 2026-09-07
*Tool:* Claude Code /risk-assess | *Mode:* Interactive
*Session:* 2026-09-07-093958
*Full analysis:* [PRODSECRM-309/2026-09-07-093958/analysis.md|https://gitlab.cee.redhat.com/imurphy/risk-docs/-/blob/ahaklik/prodsecrm-305-assessment/sessions/PRODSECRM-309/2026-09-07-093958/analysis.md]

h3. Evidence Gathered

* *JIRA:* 177 issues visited (depth 3), 802 comments, 999 URLs extracted
* *Gmail:* Unavailable; no email evidence used
* *Drive:* No matching documents
* *CVE:* No direct CVE mapped to this risk

h3. AI Analysis [AI-GENERATED]

||*Field*||*AI Recommendation*||*Confidence*||
|Severity|High|medium|
|Likelihood|Likely|medium|
|Impact|Major|medium|

*Key findings:* RHOAI 3.6 EA1/EA2 still requires temporary exceptions for hermetic-build and approved RPM-signature controls across MLMD, OpenVINO, and vLLM CPU. NeMo Guardrails and OGX Core have moved away from direct external model downloads, but five modelcar images still depend on the staging registry. Production exception [MR 22104|https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104] has not been verified as merged and active; stage [MR 22103|https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22103] has also not been independently verified as applied. Remediation timelines have slipped: MLMD moved to GA, OpenVINO targets GA or later, and vLLM moved to EA2. Exceptions expire on 2026-09-30, 2026-10-21, and 2026-12-31. No active compromise or customer exploit was evidenced, but customer and business exposure remains unquantified.

*Why this matters:* Without an effective exception, valid RHOAI artifacts may be blocked or delayed. With the exception, artifacts may ship while build inputs, RPM provenance, package signatures, and model-image promotion controls remain weaker than required. This affects release availability, product integrity, customer trust, and vulnerability-remediation confidence. The staging-registry dependency also creates availability and change-control risk for model content.

*Recommended mitigations:*

# Confirm that [MR 22104|https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104] is approved, merged, and active in production, including its merge commit and policy evaluation result -- *Owner:* RHOAI release integration / ProdSec policy owner
# Create a component-level exception register covering MLMD, OpenVINO, vLLM CPU, NeMo Guardrails, and OGX Core -- *Owner:* RHOAI release integration lead
# Verify modelcar image digests, promotion controls, registry availability, immutability, and rollback procedures -- *Owner:* RHAI model validation team
# Complete approved-source and hermetic-build remediation for MLMD, OpenVINO, and vLLM, and remove the stage-registry exception -- *Owners:* Component engineering, AIPCC, RHAI model validation

*Escalation recommendation:* PSRR promotion *NOT READY*. Promotion requires quantified customer/release/business impact, a named director-level accountable risk owner, and proof that production [MR 22104|https://gitlab.cee.redhat.com/releng/konflux-release-data/-/merge_requests/22104] is merged and active.

h3. Adversarial Review [AI-GENERATED]

* *Mode:* Full adversarial loop
* *Rounds:* 5
* *Challenges raised:* 9
* *Challenges resolved:* 9
* *Final disposition:* EXHAUSTED
* *Rating changes from review:* None

h3. Analyst Decision [HUMAN]

*Action:* CONCUR
*Changes from AI recommendation:* None -- concurred as-is.
*Sign-off:* Aleksandra Haklik | 2026-09-07

_CONCUR records the analyst's concurrence with the recommendation. It is not a business-owner risk acceptance decision._
