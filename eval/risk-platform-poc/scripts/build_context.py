#!/usr/bin/env python3
"""Assemble the full risk assessment prompt from frozen inputs.

Runs as a before_each hook in the eval harness. Reads intelligence.json from
the case workspace, calls Risk Platform's build_unattended_context() to
assemble prompt variables, modifies the unattended_draft_analysis.md template
to remove [HUMAN REQUIRED] stubs, and writes the assembled prompt into
input.yaml for the runner to consume.

Environment variables (set by eval.yaml hooks):
    CASE_WORKSPACE  -- absolute path to the case workspace directory
    RP_PATH         -- absolute path to the risk-platform repository root
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

# ── Context truncation caps ─────────────────────────────────────────────
# Keep assembled prompts under ~40K chars so claude --print doesn't stall.
# The gold-standard assessments were produced interactively with selective
# context loading, not by dumping the entire intelligence graph into one
# prompt.  These caps approximate that behaviour.
_MAX_COMMENT_EXCERPTS = 50       # number of comments to keep (most recent)
_MAX_COMMENT_CHARS = 15_000      # hard cap on comment_excerpts total chars
_MAX_LINKED_ISSUES = 30          # number of linked-issue summary lines
_MAX_LINKED_CHARS = 5_000        # hard cap on linked_issue_summaries chars
_MAX_BRIEFING_CHARS = 8_000      # hard cap on briefing_text chars
_MAX_DESCRIPTION_CHARS = 4_000   # hard cap on root_description chars


def main() -> None:
    ws = Path(os.environ["CASE_WORKSPACE"])
    case_source_dir = Path(os.environ.get("CASE_SOURCE_DIR", ""))

    # ── Validate RP_PATH ────────────────────────────────────────────────
    rp_raw = os.environ.get("RP_PATH", "")
    if not rp_raw:
        print(
            "ERROR: RP_PATH environment variable is not set.\n"
            "The before_all hook should propagate it via .hook-outputs.yaml.\n"
            "If running manually, export RP_PATH=/path/to/risk-platform",
            file=sys.stderr,
        )
        sys.exit(1)
    rp_path = Path(rp_raw)
    if not (rp_path / "src" / "risk_platform").is_dir():
        print(
            f"ERROR: RP_PATH={rp_path} does not contain src/risk_platform/.\n"
            "Check that RP_PATH points to the risk-platform repo root.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Add Risk Platform source to import path
    rp_src = rp_path / "src"
    if str(rp_src) not in sys.path:
        sys.path.insert(0, str(rp_src))

    # Set RISK_PLATFORM_PATH for risk_platform.config (needed by regulatory.py)
    os.environ.setdefault("RISK_PLATFORM_PATH", str(rp_path))

    from risk_platform.cli import build_unattended_context
    from risk_platform.quality_gates import detect_data_gaps
    from risk_platform.regulatory import scope_frameworks
    from risk_platform.triage_classify import parse_description_metadata

    input_path = ws / "input.yaml"
    input_data = yaml.safe_load(input_path.read_text(encoding="utf-8"))

    # ── Load frozen intelligence from source dataset ───────────────────
    # The gold-standard directory is in the source dataset, not the workspace
    intel_path = case_source_dir / "gold-standard" / "intelligence.json"
    with intel_path.open(encoding="utf-8") as f:
        intel_data = json.load(f)

    root_key = intel_data.get("meta", {}).get("root_issue", input_data["risk_id"])
    root_issue = intel_data.get("issues", {}).get(root_key, {})

    # ── Deterministic regulatory scoping ────────────────────────────────
    issue_data_for_scoping = {
        "labels": root_issue.get("labels", []),
        "components": root_issue.get("components", []),
        "summary": root_issue.get("summary", ""),
    }
    try:
        scoping_result = scope_frameworks(issue_data_for_scoping)
    except Exception:
        scoping_result = None

    regulatory_results_list: list[dict] = []
    regulatory_framework_ids: list[str] = []
    if scoping_result is not None:
        regulatory_results_list = [
            {
                "framework_id": fw.framework_id,
                "framework": fw.framework_id,
                "full_name": fw.full_name,
                "fired_categories": fw.fired_categories,
            }
            for fw in scoping_result.matched_frameworks
        ]
        regulatory_framework_ids = [
            fw.framework_id for fw in scoping_result.matched_frameworks
        ]

    # ── Detect data gaps (deterministic) ────────────────────────────────
    desc_metadata = parse_description_metadata(root_issue.get("description"))
    gaps = detect_data_gaps(
        issue_data=root_issue,
        intel_data=intel_data,
        regulatory_frameworks=regulatory_framework_ids,
        analyst_name="eval-benchmark",
        description_metadata=desc_metadata,
    )

    # Format gaps table (matches cli.py call-site format)
    if gaps:
        gap_rows = [
            f"| {g['gap_id']} | {g['category']} | {g['owner']} "
            f"| {g.get('priority', 'medium').capitalize()} |"
            for g in gaps
        ]
        data_gaps_table = (
            "| Gap | Category | Owner | Priority |\n"
            "|-----|----------|-------|----------|\n"
            + "\n".join(gap_rows)
        )
    else:
        data_gaps_table = "No data gaps identified."

    # ── Build prompt context ────────────────────────────────────────────
    briefing_path = case_source_dir / "gold-standard" / "briefing.txt"
    context = build_unattended_context(
        intel_path=intel_path,
        briefing_path=briefing_path if briefing_path.exists() else None,
        issue_data=root_issue,
        regulatory_results=regulatory_results_list,
    )
    context["data_gaps_table"] = data_gaps_table

    # ── Truncate context to stay within prompt budget ───────────────────
    context = _truncate_context(context)

    # ── Build lean benchmark prompt ─────────────────────────────────────
    # Instead of loading the full 267-line unattended_draft_analysis.md
    # template (designed for interactive multi-turn use), build a focused
    # benchmark prompt that asks only for what the 8 judges score.
    prompt = _build_benchmark_prompt(context, input_data)

    # ── Write assembled prompt back into input.yaml ─────────────────────
    input_data["prompt"] = prompt
    input_path.write_text(
        yaml.dump(input_data, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )


def _truncate_context(context: dict) -> dict:
    """Cap context field sizes to keep the assembled prompt manageable.

    The gold-standard assessments were produced interactively over multiple
    turns with selective context loading.  Dumping everything (up to 802
    comments / 177 linked issues) into a single prompt causes claude --print
    to stall.  These caps approximate the real interactive context budget.
    """
    # ── comment_excerpts: keep the last N comments (most recent) ────────
    comments = context.get("comment_excerpts", "")
    if comments:
        lines = comments.split("\n")
        if len(lines) > _MAX_COMMENT_EXCERPTS:
            lines = lines[-_MAX_COMMENT_EXCERPTS:]
        text = "\n".join(lines)
        if len(text) > _MAX_COMMENT_CHARS:
            # Trim from the front to keep the most recent comments
            text = text[-_MAX_COMMENT_CHARS:]
            nl = text.find("\n")
            if nl > 0:
                text = text[nl + 1:]
        context["comment_excerpts"] = text

    # ── linked_issue_summaries: keep the first N issues ─────────────────
    linked = context.get("linked_issue_summaries", "")
    if linked:
        lines = linked.split("\n")
        if len(lines) > _MAX_LINKED_ISSUES:
            lines = lines[:_MAX_LINKED_ISSUES]
        text = "\n".join(lines)
        if len(text) > _MAX_LINKED_CHARS:
            text = text[:_MAX_LINKED_CHARS]
            nl = text.rfind("\n")
            if nl > 0:
                text = text[:nl]
        context["linked_issue_summaries"] = text

    # ── briefing_text: truncate at a paragraph boundary ─────────────────
    briefing = context.get("briefing_text", "")
    if len(briefing) > _MAX_BRIEFING_CHARS:
        truncated = briefing[:_MAX_BRIEFING_CHARS]
        para = truncated.rfind("\n\n")
        if para > _MAX_BRIEFING_CHARS // 2:
            truncated = truncated[:para]
        context["briefing_text"] = (
            truncated + "\n\n[... truncated for context budget]"
        )

    # ── root_description: truncate at a word boundary ───────────────────
    desc = context.get("root_description", "")
    if len(desc) > _MAX_DESCRIPTION_CHARS:
        truncated = desc[:_MAX_DESCRIPTION_CHARS]
        space = truncated.rfind(" ")
        if space > _MAX_DESCRIPTION_CHARS // 2:
            truncated = truncated[:space]
        context["root_description"] = truncated + " [... truncated]"

    return context


def _build_benchmark_prompt(context: dict, input_data: dict) -> str:
    """Build a lean benchmark prompt focused on what the 8 judges score.

    Instead of the full 267-line unattended_draft_analysis.md template
    (designed for interactive multi-turn sessions that produce 30K-82K
    char outputs), this builds a focused prompt that:

    - Keeps all 6 section headers (required for QC-2 structural gate)
    - Asks for FULL content in scored sections (D1-D8)
    - Asks for BRIEF content in unscored sections
    - Pre-fills the Analyst Assessment (not generated by the model)

    Expected output: ~8K-15K chars vs 30K-82K chars from the full template.
    """
    risk_id = input_data.get("risk_id", "UNKNOWN")
    decision = input_data.get("analyst_decision", "CONCUR")
    changes = input_data.get("analyst_changes", "None")
    rationale = input_data.get("analyst_rationale", "N/A")
    reg_scoping = context.get("regulatory_scoping", "No frameworks matched")

    # Build the prompt in parts
    parts: list[str] = []

    # ── System instructions ─────────────────────────────────────────────
    parts.append(f"""\
You are producing a risk assessment for {risk_id}. Analyze the source \
data below and generate a structured markdown document.

IMPORTANT constraints:
- Every section header MUST start with "## Section N:" exactly as shown.
- Label generated sections with [AI-GENERATED].
- Cite specific JIRA keys and evidence. Do not fabricate citations.
- Do NOT reproduce JIRA description text verbatim -- summarize in your own words.
- Keep Sections 1, 3, 4, and 6 BRIEF (tables + 1-2 sentences each).
- Write Sections 2 and 5 in FULL DETAIL -- these are the core of the assessment.
- The Executive Summary must contain concrete business consequences.
- Include a Sources table at the end listing every JIRA key you cite.""")

    # ── Source data ─────────────────────────────────────────────────────
    parts.append(f"""
<jira_data>
Issue Summary: {context.get('issue_summary', '')}
Status: {context.get('issue_status', '')}
Priority: {context.get('issue_priority', '')}
Labels: {context.get('issue_labels', '')}
Components: {context.get('issue_components', '')}
Assignee: {context.get('issue_assignee', '')}
</jira_data>

<root_description>
{context.get('root_description', '')}
</root_description>

<briefing>
{context.get('briefing_text', '')}
</briefing>

<regulatory_scoping>
{reg_scoping}
</regulatory_scoping>

<linked_issues>
{context.get('linked_issue_summaries', '')}
</linked_issues>

<comment_excerpts>
{context.get('comment_excerpts', '')}
</comment_excerpts>""")

    # ── Output structure ────────────────────────────────────────────────
    parts.append(f"""
---

Produce the following document. Write it exactly as structured below.

# Risk Assessment: {risk_id}

## Metadata

```yaml
jira_key: "{risk_id}"
title: "concise risk statement from the summary"
status: draft
severity: "your assessment -- one of: Critical, High, Medium, Low"
likelihood: "your assessment -- one of: Almost Certain, Likely, Possible, Unlikely, Rare"
impact: "your assessment -- one of: Catastrophic, Major, Moderate, Minor, Insignificant"
analyst: "benchmark-eval"
adversarial_mode: "pending"
```

## Executive Summary [AI-GENERATED]

Write 3-5 sentences: what this risk is, why it matters to the business \
(name specific consequences -- customers, revenue, compliance, availability), \
what the most important next action is, and who should own it. \
Include the [AI-GENERATED] label in the heading above.

## Section 1: Risk Identification [AI-GENERATED]

BRIEF. Produce only the table and one context paragraph.

| Field | Value |
|-------|-------|
| Risk Type | classify as Operational / Technical / Compliance / Strategic / Third-Party / Process |
| Title | concise risk statement |
| Description | 2-3 sentences summarizing the exposure |

**Context:** One paragraph on how this risk was identified. Cite JIRA keys.

## Section 2: Risk Assessment [AI-GENERATED]

FULL DETAIL. This is the core analytical section.

### Severity Rating

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| Severity | your rating | cite specific evidence |
| Likelihood | your rating | cite specific evidence |
| Impact | your rating | cite specific evidence |

### Rating Rationale

**Severity justification:** Detailed justification referencing specific \
JIRA issues, comments, dates, and technical evidence. Tie to concrete \
factors, not generic risk language.

**Likelihood justification:** Same standard -- specific evidence.

**Impact justification:** Same standard -- specific evidence.

### CVE Landscape

Assess any CVEs referenced in the data. If none are relevant, state so.

## Section 3: Objective Alignment [AI-GENERATED]

BRIEF. Table only, no long explanations.

| # | Objective | Affected? |
|---|-----------|-----------|
| 1 | Product availability | Yes/No/Uncertain |
| 2 | Customer trust | Yes/No/Uncertain |
| 3 | Regulatory compliance | Yes/No/Uncertain |
| 4 | Revenue / cost | Yes/No/Uncertain |
| 5 | Strategic roadmap | Yes/No/Uncertain |
| 6 | Product integrity | Yes/No/Uncertain |
| 7 | Safety, privacy, data integrity | Yes/No/Uncertain |

## Section 4: Current Mitigations [AI-GENERATED]

BRIEF. Summarize known controls in 1-2 short paragraphs based on the \
comment excerpts and linked issues. If no mitigation data is available, \
state that.

## Section 5: Recommended Actions [AI-GENERATED]

FULL DETAIL. This section is critically scored.

### Immediate (0-7 days)

List 1-3 actions. Each MUST have: a named owner (not "the team"), \
a concrete timeline, and a definition of done.

### Short-Term (1-4 weeks)

List 1-3 actions with the same specificity.

### Long-Term (1-3 months)

List 1-2 actions.

### Data Gaps

{context.get('data_gaps_table', 'No data gaps identified.')}

## Section 6: Escalation Analysis [AI-GENERATED]

BRIEF. PSRR table with Met/Not Met, one-line evidence each.

| # | Requirement | Met? | Evidence |
|---|-------------|------|----------|
| 1 | Quantified risk | Met/Not Met | brief |
| 2 | Actionable path | Met/Not Met | brief |
| 3 | Context provided | Met/Not Met | brief |
| 4 | Tied to an objective | Met/Not Met | brief |
| 5 | Named risk owner | Met/Not Met | brief |
| 6 | Consequence of inaction | Met/Not Met | brief |
| 7 | Risk posture requested | Met/Not Met | brief |
| 8 | Acceptance timebox | Met/Not Met | brief |

**Promotion recommendation:** READY / NOT READY / CONDITIONAL

## Analyst Assessment [HUMAN]

**Action:** {decision}

**Changes from AI recommendation:** {changes}

**Rationale for overrides:** {rationale}

**Sign-off:** Benchmark evaluation | Automated

## Sources

| Source | Type | Link |
|--------|------|------|
| List every JIRA key, URL, or document you cited | jira / url / doc | link or key |
""")

    return "\n".join(parts)


if __name__ == "__main__":
    main()
