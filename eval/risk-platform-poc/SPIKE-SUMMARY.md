# GRCAUTO-44: Spike Summary -- Multi-Provider Evaluation Framework

**Date:** 2026-09-29
**Investigator:** Gustavo Miranda
**Epic:** GRCAUTO-1 -- Add Multi-Provider Configuration Capability to Support Cost Optimization
**PoC Branch:** [`risk_platform`](https://github.com/gxmiranda/agent-eval-harness/tree/risk_platform) (14 commits)

---

## 1. Framework Evaluated

**agent-eval-harness** (v1.49.2) -- an internal Red Hat evaluation framework
(opendatahub-io) purpose-built for agent skill and LLM benchmarking. Uses
MLflow as the backbone for tracing, evaluation, datasets, and reporting.

Alternatives considered: Promptfoo, DeepEval, RAGAS. All were evaluated at
the requirements level and found to be a weaker fit (see Section 5 below).

---

## 2. Framework Capabilities vs Risk Platform Requirements

| Requirement (from GRCAUTO-44) | Supported? | Evidence |
|---|---|---|
| Repeatable comparisons between Claude baseline and OpenAI candidates | Yes | Same `eval.yaml` config, swap `--model` flag. Config overlays (`eval-openai.yaml`) switch runner to `responses-api` for OpenAI models with 3 lines of YAML. |
| Evaluation against gold-standard risk assessments | Yes | 5 frozen PRODSECRM sessions (306, 316, 312, 304, 309) used as test fixtures with `analysis.md` as reference output. |
| Risk Platform quality checks (QC-1 through QC-6) | Yes | Two `check` judges invoke `quality_gates.py` directly: D1 (structural completeness, QC-1/2/5) and D4 (consequence framing, QC-6). Zero Risk Platform code changes required. |
| Adversarial review outcomes | Yes | `after_each` hook runs `run_garth_critique()` from the Risk Platform's critique module. Scores D6 (adversarial durability) by comparing new defects found. |
| Custom evaluation criteria (citations, regulatory, ratings, recommendations, gaps) | Yes | 5 LLM judge personas (D2, D3, D5, D7, D8) translated from the GRCAUTO-1 evaluation framework document Section 11.3. Each uses `samples: 2` for inter-rater reliability. |
| Automated, CI-visible quality and cost comparison reporting | Yes | HTML report with per-case details, scoring summary, threshold-based pass/fail gates. JSON summary for CI integration. ANOVA/Pareto for multi-model cost/quality analysis. |

---

## 3. Boundary Definition

| Responsibility | Owner |
|---|---|
| Generating risk assessments | Risk Platform (existing prompts + model invocation) |
| Frozen test fixtures (intelligence.json, gold-standard analysis.md) | Risk Platform team (session data from risk-docs) |
| Quality gate definitions (QC-1 through QC-6) | Risk Platform (`quality_gates.py` -- unchanged) |
| Adversarial critique loop (Garth/Shrike) | Risk Platform (`critique.py` -- unchanged) |
| Benchmark orchestration (workspace, execution, collection) | agent-eval-harness |
| Judge scoring (8 dimensions) | agent-eval-harness (2 deterministic + 5 LLM + 1 critique-based) |
| Regression detection (thresholds, pass/fail) | agent-eval-harness |
| CI reporting (HTML, JSON, MLflow) | agent-eval-harness |
| Multi-model comparison (ANOVA, Pareto) | agent-eval-harness |
| Prompt assembly adapter (frozen inputs -> benchmark prompt) | Integration layer (~200 lines, in eval harness repo) |

**Zero changes to the Risk Platform codebase.** The adapter imports existing
Risk Platform functions (`build_unattended_context`, `check_all_gates`,
`run_garth_critique`, `scope_frameworks`, `detect_data_gaps`) directly.

---

## 4. Suitability Classification

**Suitable with limited Risk Platform integration.**

The framework provides all evaluation infrastructure out of the box. The
integration layer is a small adapter (~200 lines of Python across 2 scripts)
that bridges the Risk Platform's existing functions with the eval harness's
hook system:

- `build_context.py` (before_each hook): Assembles the benchmark prompt from
  frozen `intelligence.json` using the Risk Platform's own
  `build_unattended_context()` function.
- `run_quality_gates.py` (after_each hook): Runs `check_all_gates()` and
  `run_garth_critique()` on candidate output.

Both scripts import directly from the `risk_platform` Python package. No
wrappers, no proxies, no code duplication.

---

## 5. Why agent-eval-harness Over Alternatives

| Criterion | agent-eval-harness | Promptfoo | DeepEval | RAGAS |
|---|---|---|---|---|
| Agent/skill execution (not just prompt-in/text-out) | Yes -- CLI runner, claude-code runner, codex runner, responses-api runner | No -- prompt-focused | No -- API-focused | No -- RAG-focused |
| Deterministic Python judges (invoke existing quality_gates.py) | Yes -- `check` judge type runs inline Python | No -- would need external script wrapping | Partial -- custom metrics possible | No |
| LLM judge personas with structured JSON output | Yes -- `prompt_file` judges with Jinja2, score_range, samples | Yes -- similar capability | Yes -- similar capability | Limited |
| Adversarial critique loop integration | Yes -- `module`/`function` judges, hooks for arbitrary code | No -- would need external orchestration | No | No |
| Multi-model ANOVA/Pareto comparison | Yes -- built-in eval-anova with statistical analysis | No | No | No |
| Cost/quality tradeoff analysis | Yes -- per-model cost tracking, Pareto frontier | Partial -- cost tracking only | No | No |
| OpenShift-ready containerized execution | Yes -- UBI9 images, Kubernetes environment, Harbor integration | No | No | No |
| Internal Red Hat project | Yes -- opendatahub-io, Apache-2.0 | No -- external OSS | No -- external OSS | No -- external OSS |

---

## 6. Integration Estimate

### Effort

| Item | Effort | Status |
|---|---|---|
| Adapter scripts (build_context.py, run_quality_gates.py) | 1 day | Done (PoC) |
| 5 LLM judge prompt files (D2, D3, D5, D7, D8) | 0.5 day | Done (PoC) |
| eval.yaml + overlays (main, triage, OpenAI) | 0.5 day | Done (PoC) |
| Dataset preparation (5 frozen test cases) | 0.5 day | Done (PoC) |
| Environment hardening (RP_PATH, hook propagation) | 0.5 day | Done (PoC) |
| Production hardening (prompt optimization, judge calibration) | 2-3 days | Remaining |
| CI integration (GitHub Actions, PR gating) | 1-2 days | Remaining |
| **Total (PoC to production)** | **~3-5 days** | |

### Risks

1. **Prompt-mode output quality**: Single-prompt risk assessments score
   lower than multi-turn interactive sessions (expected). The benchmark
   measures relative quality between models, not absolute production quality.

2. **Context window limits**: The largest test case (PRODSECRM-309, 177
   JIRA issues) required context truncation to fit in a single prompt.
   Truncation caps are tuned but may need adjustment for different models.

3. **Garth critique dependency**: The D6 adversarial durability judge
   requires Anthropic API credentials and the Risk Platform's `AIService`.
   Falls back gracefully to mid-range scoring when unavailable.

### Prerequisites Before Benchmarking Can Begin

1. Freeze the 5 gold-standard session directories (already in PoC dataset)
2. Export `RP_PATH` or place the risk-platform checkout as a sibling
3. Set `ANTHROPIC_API_KEY` for LLM judges and Garth critique
4. Select candidate OpenAI models to evaluate

---

## 7. PoC Results

### Successful End-to-End Run (2026-09-29)

All 5 test cases executed, scored by 8 judges, HTML report generated.

| Dimension | Judge Type | Score | Threshold | Status |
|---|---|---|---|---|
| D1: Structural Completeness | Deterministic (QC-1/2/5) | 100% pass | 100% | PASS |
| D2: Citation Quality | LLM (Citation Auditor) | 2.0 / 5 | -- | Low |
| D3: Regulatory Mapping | LLM (Regulatory Analyst) | 1.0 / 5 | 3.0 | Below threshold |
| D4: Consequence Framing | Deterministic (QC-6) | 1.0 / 5 | -- | Low |
| D5: Rating Accuracy | LLM (Rating Calibrator) | 3.0 / 5 | 4.0 | Below threshold |
| D6: Adversarial Durability | Check (Garth critique) | 3.0 / 5 | 3.5 | Below threshold |
| D7: Actionability | LLM (Mitigation Reviewer) | 3.0 / 5 | -- | Acceptable |
| D8: Data Gap Detection | LLM (Gap Comparator) | 1.8 / 5 | -- | Low |

**Interpretation:** These scores are expected and correct. The gold-standard
assessments were produced over 2+ hour interactive sessions with multiple
turns, adversarial critique loops, and human analyst oversight. A single-prompt
generation cannot match that quality. The judges correctly discriminate between
single-prompt output and the gold standard. The value of the benchmark is in
*relative* comparisons between candidate models, not absolute scores.

### PoC Code

- **Branch:** [`risk_platform`](https://github.com/gxmiranda/agent-eval-harness/tree/risk_platform)
- **14 commits** covering: frozen fixtures, adapter scripts, judge prompts,
  eval configs, harness features (`max_turns`, `--verify` config discovery),
  and environment hardening

### Artifacts Delivered

```
eval/risk-platform-poc/
  eval.yaml                    # Main eval config (8 judges, hooks, thresholds)
  eval-triage.yaml             # Triage task tier (relaxed thresholds)
  eval-openai.yaml             # OpenAI runner overlay (responses-api)
  scripts/
    build_context.py           # before_each: frozen inputs -> benchmark prompt
    run_quality_gates.py       # after_each: QC gates + Garth critique
  judges/
    d2_citation_auditor.md     # LLM judge: Citation Auditor persona
    d3_regulatory_analyst.md   # LLM judge: Regulatory Analyst persona
    d5_rating_calibrator.md    # LLM judge: Rating Calibrator persona
    d7_mitigation_reviewer.md  # LLM judge: Mitigation Reviewer persona
    d8_gap_comparator.md       # LLM judge: Gap Comparator persona
  dataset/
    PRODSECRM-{304,306,309,312,316}/
      input.yaml + annotations.yaml + gold-standard/
```

---

## 8. Recommendation

### Go -- Adopt agent-eval-harness for a limited pilot.

The framework covers ~95% of the target operating model from the GRCAUTO-1
evaluation framework document with configuration and a small adapter layer.
The remaining ~5% (tiebreaker protocol for inter-rater reliability, full
Shrike multi-round adversarial loop) requires modest integration work.

**Recommended approach:**

1. **Adopt** agent-eval-harness for benchmark orchestration, scoring, and
   CI reporting.
2. **Retain** the Risk Platform's own quality gates (`quality_gates.py`) and
   adversarial critique (`critique.py`) as judge inputs -- the adapter calls
   them directly without modification.
3. **No custom evaluation platform required.** The framework provides the
   runner, judge system, regression detection, cost tracking, and reporting
   infrastructure. The Risk Platform's role is generating assessments and
   providing its domain-specific quality criteria.

**Next step:** Run the benchmark with an OpenAI candidate model
(`eval-openai.yaml` overlay) to produce the first cross-provider comparison.
This validates the full multi-provider path and produces the cost/quality
tradeoff data needed for GRCAUTO-1's acceptance criteria.
