## Adversarial Critique Summary -- PRODSECRM-304

**Mode:** Full adversarial loop (escalated from Garth single-pass)
**Rounds:** 4 (plus 1 Garth pre-round)
**Challenges raised:** 20 (unique, after deduplication across rounds)
**Challenges resolved:** 16
**Consecutive clean rounds:** 0 (but Round 4 had only 1 borderline-new challenge; convergence trend: 10 -> 4 -> 4 -> 1)
**Final disposition:** MAX ROUNDS (practical convergence — remaining challenges are structural or already acknowledged in the analysis)
**Rating changes from review:** Medium -> High (Garth escalation, Round 0); risk matrix tension between High severity and Unlikely x Moderate acknowledged

### Round-by-Round Summary

**Garth (Pre-round):** 6 material issues identified. Credibility High. Escalated to full loop. Key finding: weight poisoning threat bypasses safetensors mitigant; circular remediation with -227; QC-6 framing rated GENERIC.

**Round 1:** 10 challenges raised, 4 resolved. Key challenges: PSRR/severity internal contradiction (resolved), -227 remediation quote unverified (resolved — verified via JIRA MCP, discovered -226 is unrelated hermetic building exception), Objective 7 dismissal premature (resolved — made content-domain-dependent). 6 challenges remained open (mostly structural).

**Round 2:** 11 challenges raised (4 genuinely new, 7 rephrased). 7 resolved this round. Key new challenges: likelihood/severity contradiction on weight poisoning (resolved — likelihood restructured), -269 pattern claim unverified (resolved — verified via MCP), downstream consumers unsourced (added to data gaps). Key investigation: RHOKP-1681 confirmed "To Do" status. PRODSECRM-269 verified as properly resolved.

**Round 3:** 12 challenges raised (4 genuinely new, 8 rephrased). 5 resolved this round. Key new challenges: day-one EC Policy absence inconsistency (resolved — reclassified as context), risk matrix coherence (resolved — standalone vs inherited factors separated), PSRR double-counting (resolved — tension acknowledged). Key investigation: PRODSECRM-118 comments retrieved (17 comments). Snyk bug confirmed current as of April 2026. Ian Murphy's July 2026 assessment confirmed High/Likely/Major.

**Round 4:** 12 challenges raised (1 genuinely new, 11 rephrased). Key new challenge: RHOKP-1681 "updated 2026-08-31" could indicate active planning (resolved — language softened). Critic rated QC-6 as CONCRETE with qualification (improved from GENERIC in Rounds 1-2).

### Unresolved Challenges

The following challenges remain open at exit. All are structural limitations that cannot be resolved within this critique session:

1. **OKP team not consulted** (R1-C4): Paula Wambui (reporter), Jared Sprague (RHOKP-1681 assignee), and other stakeholders were not consulted. Content domain, architecture, downstream consumers, and compensating controls are unknown.

2. **OKP content domain not established** (R1-C5): The single most important unresolved variable. Determines whether impact is Moderate (general documentation) or Major (security-relevant content). Flagged as [UNRESOLVED] throughout the analysis and as a Critical data gap.

3. **Weight poisoning threat model not substantiated** (R1-C6): No citations to academic research, threat intelligence, or incident reports for small embedding model weight poisoning. Theoretical basis described; no WebSearch available in critique context.

4. **Downstream consumers not verified** (R2-C5): Whether OKP's retrieval results are consumed by other products via API is unknown. "No cross-product contamination" is flagged as an unsourced assumption.

5. **Ownership unconfirmed** (R2-C6): All recommended action owners are marked preliminary. Cannot confirm without stakeholder engagement.

6. **RHEL AI precedent controls not assessed** (R2-C10): Whether RHEL AI's ibm-granite approval includes controls (SHA256 pinning, repo-level scoping) that -304 should match is unknown.

7. **5-month scanning evidence staleness** (R3-C8): Last verified scanning pipeline status is April 2026. Garak scanning may have been deployed in the intervening 5 months.

8. **CRA regulatory framework not assessed** (R3-C9): Supply chain obligations under the CRA are potentially relevant but no frameworks were loaded. Analyst override declined.

### Key Findings from Adversarial Review

1. **PRODSECRM-226/-227 mismatch:** -227 (embedding models) was Closed as Duplicate of -226 (hermetic building) — two completely different exception types. The internalization remediation commitment is tracked in RHOKP-1681 (product backlog, To Do) but not in any PRODSECRM issue. (Discovered Round 1, verified Round 2)

2. **Scanning gaps confirmed current:** PRODSECRM-118 comments (Emily Fox, April 2026) confirm Snyk scans pipeline files not model files, ClamAV fails on >2GB, Clair times out. AIBOM work is unowned. Ian Murphy rated -118 High/Likely/Major with PSRR escalation recommended (July 2026). (Discovered Round 2-3)

3. **RHOKP-1681 internalization not started:** The ticket is in "To Do" status (assigned to Jared Sprague, updated 2026-08-31). The internalization path exists but has not begun. (Discovered Round 2)

4. **Severity rating tension:** The High rating compounds standalone factors (stalled remediation, missing artifact) with inherited systemic factors (scanning gaps from -118). The analysis explicitly acknowledges the risk matrix tension (Unlikely x Moderate = Medium in standard frameworks) and the PSRR double-counting concern. The analyst should assess whether standalone factors alone justify High.

5. **QC-6 improved:** Consequence framing upgraded from GENERIC (Rounds 1-2) to CONCRETE with qualification (Rounds 3-4). The primary consequence chain is concrete and causal; the escalated consequence (customers following incorrect security guidance) is conditional on the unresolved content domain question.
