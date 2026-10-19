#!/usr/bin/env python3
"""Fill LLM analysis sections in a comparison report.

Reads discovery data and per-run summary.yaml files, calls Claude Opus
via Vertex AI to generate four HTML analysis sections, and patches the
comparison index.html to replace placeholder content.

Usage:
    python3 eval/risk-platform-poc/scripts/fill_comparison_analysis.py \
      eval/runs/comparison

Requires:
    ANTHROPIC_VERTEX_PROJECT_ID and CLOUD_ML_REGION (or gcloud ADC)
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import yaml


# ── Truncation limits for summary data ──────────────────────────────────
_MAX_RATIONALE_CHARS = 500
_MAX_CASES_PER_RUN = 10


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: fill_comparison_analysis.py <comparison-dir>", file=sys.stderr)
        sys.exit(1)

    comparison_dir = Path(sys.argv[1])
    index_path = comparison_dir / "index.html"
    if not index_path.exists():
        print(f"ERROR: {index_path} not found. Run compare.py generate first.", file=sys.stderr)
        sys.exit(1)

    project_id = os.environ.get("ANTHROPIC_VERTEX_PROJECT_ID", "")
    if not project_id:
        print("ERROR: ANTHROPIC_VERTEX_PROJECT_ID not set.", file=sys.stderr)
        sys.exit(1)

    # ── Step 1: Discover runs ───────────────────────────────────────────
    project_root = Path.cwd()
    discover_script = project_root / "skills" / "eval-compare" / "scripts" / "compare.py"
    # Find the input dir (parent of the comparison output, or same dir)
    runs_dir = _find_runs_dir(comparison_dir, project_root)

    result = subprocess.run(
        [sys.executable, str(discover_script), "discover", str(runs_dir)],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"ERROR: discover failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    discovery = json.loads(result.stdout)
    runs = discovery.get("runs", [])
    if not runs:
        print("ERROR: No runs discovered.", file=sys.stderr)
        sys.exit(1)

    print(f"Discovered {len(runs)} runs", file=sys.stderr)

    # ── Step 2: Read and truncate summaries ─────────────────────────────
    run_summaries = []
    for run in runs:
        summary_path = Path(run["dir"]) / "summary.yaml"
        if not summary_path.exists():
            run_summaries.append({"name": run["name"], "model": run.get("model", "?"), "error": "summary.yaml missing"})
            continue
        with summary_path.open() as f:
            summary = yaml.safe_load(f) or {}
        truncated = _truncate_summary(summary, run["name"], run.get("model", "?"))
        run_summaries.append(truncated)

    # ── Step 3: Build prompt ────────────────────────────────────────────
    prompt = _build_prompt(discovery, run_summaries)
    print(f"Prompt size: {len(prompt)} chars", file=sys.stderr)

    # ── Step 4: Call Vertex AI ──────────────────────────────────────────
    from anthropic import AnthropicVertex

    region = os.environ.get("CLOUD_ML_REGION", "us-east5")
    client = AnthropicVertex(project_id=project_id, region=region)

    print("Calling Claude Opus via Vertex AI...", file=sys.stderr)
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    analysis_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            analysis_text += block.text

    if not analysis_text:
        print("ERROR: Empty response from LLM.", file=sys.stderr)
        sys.exit(1)

    print(f"Response size: {len(analysis_text)} chars", file=sys.stderr)

    # ── Step 5: Parse and patch HTML ────────────────────────────────────
    sections = _parse_sections(analysis_text)
    html = index_path.read_text(encoding="utf-8")
    patched = _patch_html(html, sections)

    index_path.write_text(patched, encoding="utf-8")
    filled = [k for k in sections if sections[k]]
    print(f"Patched {len(filled)}/4 sections: {filled}", file=sys.stderr)
    print(f"Report: {index_path}", file=sys.stderr)


def _find_runs_dir(comparison_dir: Path, project_root: Path) -> Path:
    """Find the runs directory that comparison.py should scan."""
    # If comparison_dir is inside eval/runs/, scan eval/runs/
    runs_dir = project_root / os.environ.get("AGENT_EVAL_RUNS_DIR", "eval/runs")
    if runs_dir.is_dir():
        return runs_dir
    # Fallback: parent of comparison dir
    return comparison_dir.parent


def _truncate_summary(summary: dict, name: str, model: str) -> dict:
    """Extract and truncate per-case scores from a summary."""
    result = {"name": name, "model": model, "judges": {}, "cases": []}

    # Judge-level means
    for judge_name, judge_data in (summary.get("judges") or {}).items():
        if isinstance(judge_data, dict):
            result["judges"][judge_name] = {
                "mean": judge_data.get("mean"),
                "pass_rate": judge_data.get("pass_rate"),
            }

    # Per-case scores (truncated rationales)
    per_case = summary.get("per_case") or {}
    for i, (case_id, case_data) in enumerate(per_case.items()):
        if i >= _MAX_CASES_PER_RUN:
            break
        if not isinstance(case_data, dict):
            continue
        case_entry = {"case_id": case_id, "scores": {}}
        for judge_name, judge_result in case_data.items():
            if not isinstance(judge_result, dict):
                continue
            score = judge_result.get("value", judge_result.get("score"))
            rationale = judge_result.get("rationale", "")
            if len(rationale) > _MAX_RATIONALE_CHARS:
                rationale = rationale[:_MAX_RATIONALE_CHARS] + "..."
            case_entry["scores"][judge_name] = {
                "score": score,
                "rationale": rationale,
            }
        result["cases"].append(case_entry)

    # Cost
    result["cost_usd"] = summary.get("total_cost_usd")

    # Judge cost estimation from token counts (Vertex pricing)
    # Vertex Opus: $15/Mtok input, $75/Mtok output
    # OpenAI Astra: approximate similar pricing
    ju = summary.get("judge_usage") or {}
    prompt_tokens = ju.get("prompt_tokens", 0) or 0
    completion_tokens = ju.get("completion_tokens", 0) or 0
    judge_cost = ju.get("judge_cost_usd")
    if judge_cost is None and (prompt_tokens or completion_tokens):
        # Estimate using Opus Vertex pricing as default
        judge_cost = (prompt_tokens * 15.0 / 1_000_000
                      + completion_tokens * 75.0 / 1_000_000)
    result["judge_cost_usd"] = round(judge_cost, 4) if judge_cost else None
    result["judge_requests"] = ju.get("requests", 0)
    result["judge_prompt_tokens"] = prompt_tokens
    result["judge_completion_tokens"] = completion_tokens

    return result


def _build_prompt(discovery: dict, run_summaries: list[dict]) -> str:
    """Assemble the LLM prompt for analysis generation."""
    # Compact discovery data (just scores, no full paths)
    compact_runs = []
    for run in discovery.get("runs", []):
        compact_runs.append({
            "name": run["name"],
            "model": run.get("model", "?"),
            "cost_usd": run.get("cost_usd"),
            "judges": run.get("judges", {}),
        })

    parts = [
        "You are writing the analysis sections for a multi-provider benchmark "
        "comparison report for the Risk Platform (PRODSECRM risk assessments).\n"
        "\n"
        "Three model configurations were benchmarked against 5 gold-standard "
        "risk assessments across 8 quality dimensions (D1-D8). The scores "
        "range from 1 (unusable) to 5 (equivalent to gold standard). D1 is "
        "a boolean pass/fail gate (1.0 = 100% pass).\n",

        "## Benchmark Scores Summary\n\n"
        f"```json\n{json.dumps(compact_runs, indent=2)}\n```\n",

        "## Per-Run Detailed Scores\n",
    ]

    for run_data in run_summaries:
        parts.append(f"\n### {run_data['name']} ({run_data['model']})\n")
        if "error" in run_data:
            parts.append(f"Error: {run_data['error']}\n")
            continue
        parts.append(f"Judge means: {json.dumps(run_data['judges'])}\n")
        if run_data.get("cost_usd"):
            parts.append(f"Cost: ${run_data['cost_usd']}\n")
        for case in run_data.get("cases", []):
            parts.append(f"\n**{case['case_id']}:**\n")
            for judge, result in case["scores"].items():
                parts.append(f"- {judge}: {result['score']}")
                if result.get("rationale"):
                    parts.append(f" -- {result['rationale']}")
                parts.append("\n")

    parts.append("""
## Instructions

Produce exactly four HTML fragments. Wrap each in delimiters exactly
as shown. Use only <p>, <h3>, <ul>, <li>, <table>, <thead>, <tbody>,
<tr>, <th>, <td> tags. No markdown. No code fences.

<!-- SECTION: verdict -->
3 sentences maximum. State which model configuration is the best choice
and why, note any that aren't viable, and call out the most important
tradeoff. Write for a VP who hasn't seen the raw data.
<!-- /SECTION: verdict -->

<!-- SECTION: model-strengths -->
For each model, write a <h3> with the model name and 2-3 sentences
highlighting its unique strengths compared to the others. What
dimensions did it score best on? What patterns show it excelling?
<!-- /SECTION: model-strengths -->

<!-- SECTION: shared-weaknesses -->
An HTML table with columns: Issue | Impact | Affected Cases.
List weaknesses that appear across ALL or most models. Focus on
dimensions where every model scored poorly. These are benchmark or
prompt issues, not model issues.
<!-- /SECTION: shared-weaknesses -->

<!-- SECTION: recommendations -->
3-5 actionable bullet points as <ul><li>. Cover: which model
configuration to use for production risk assessments, when alternatives
make sense, and what to improve in the benchmark methodology.
<!-- /SECTION: recommendations -->
""")

    return "\n".join(parts)


def _parse_sections(text: str) -> dict[str, str]:
    """Extract delimited sections from LLM response."""
    sections = {}
    for section_id in ("verdict", "model-strengths", "shared-weaknesses", "recommendations"):
        pattern = rf"<!-- SECTION: {re.escape(section_id)} -->(.*?)<!-- /SECTION: {re.escape(section_id)} -->"
        match = re.search(pattern, text, re.DOTALL)
        sections[section_id] = match.group(1).strip() if match else ""
        if not sections[section_id]:
            print(f"WARNING: Section '{section_id}' not found in LLM response", file=sys.stderr)
    return sections


def _patch_html(html: str, sections: dict[str, str]) -> str:
    """Replace placeholder tags in the comparison HTML."""
    replacements = {
        "verdict": '<p class="placeholder">Analysis pending — will be replaced with a per-model verdict.</p>',
        "model-strengths": '<p class="placeholder">Analysis pending — will be replaced with per-model strengths.</p>',
        "shared-weaknesses": '<p class="placeholder">Analysis pending — will be replaced with cross-cutting weaknesses.</p>',
        "recommendations": '<p class="placeholder">Analysis pending — will be replaced with actionable recommendations.</p>',
    }
    for section_id, placeholder in replacements.items():
        content = sections.get(section_id, "")
        if content and placeholder in html:
            html = html.replace(placeholder, content)
        elif content:
            print(f"WARNING: Placeholder for '{section_id}' not found in HTML (already filled?)", file=sys.stderr)
    return html


if __name__ == "__main__":
    main()
