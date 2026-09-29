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
from string import Template

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
    rp_path = Path(os.environ["RP_PATH"])

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

    # ── Load and modify prompt template ─────────────────────────────────
    prompt_template_path = (
        rp_path / "src" / "risk_platform" / "prompts" / "unattended_draft_analysis.md"
    )
    raw_template = prompt_template_path.read_text(encoding="utf-8")

    # Strip YAML frontmatter
    parts = raw_template.split("---", 2)
    if len(parts) >= 3:
        template_body = parts[2]
    else:
        template_body = raw_template

    # Modify the template to remove [HUMAN REQUIRED] stubs so the candidate
    # model fills ALL sections, including Section 2, Section 6, and Analyst
    # Assessment.
    template_body = _modify_template_for_benchmark(template_body, input_data)

    # Substitute $variables with context values
    prompt = Template(template_body).safe_substitute(context)

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


def _modify_template_for_benchmark(
    template_body: str, input_data: dict
) -> str:
    """Remove [HUMAN REQUIRED] stubs and instruct model to fill all sections.

    Replaces the Section 2, Section 6, and Analyst Assessment stubs with
    instructions for the candidate model to generate these sections using
    its own analytical judgment.
    """
    # ── Replace Section 2 stub ──────────────────────────────────────────
    section2_stub = (
        "## Section 2: Risk Assessment [HUMAN REQUIRED]\n"
        "\n"
        "**This section requires human analyst judgment. The automated pipeline "
        "does not produce severity ratings, likelihood assessments, or impact "
        "ratings.**\n"
        "\n"
        "### Severity Rating\n"
        "\n"
        "| Dimension | Rating | Evidence |\n"
        "|-----------|--------|----------|\n"
        "| Severity | [HUMAN REQUIRED] | [Analyst must evaluate and cite specific "
        "evidence] |\n"
        "| Likelihood | [HUMAN REQUIRED] | [Analyst must evaluate and cite specific "
        "evidence] |\n"
        "| Impact | [HUMAN REQUIRED] | [Analyst must evaluate and cite specific "
        "evidence] |\n"
        "\n"
        "### Rating Rationale\n"
        "\n"
        "**Severity justification:** [HUMAN REQUIRED]\n"
        "\n"
        "**Likelihood justification:** [HUMAN REQUIRED]\n"
        "\n"
        "**Impact justification:** [HUMAN REQUIRED]\n"
        "\n"
        "### CVE Landscape\n"
        "\n"
        "[HUMAN REQUIRED -- analyst must determine whether CVEs are relevant "
        "and assess any applicable CVE data]"
    )

    section2_replacement = (
        "## Section 2: Risk Assessment [AI-GENERATED]\n"
        "\n"
        "Analyze the available intelligence and produce severity, likelihood, "
        "and impact ratings with full evidence-based justification. Use the "
        "standard rating scales:\n"
        "- Severity: Critical / High / Medium / Low\n"
        "- Likelihood: Almost Certain / Likely / Possible / Unlikely / Rare\n"
        "- Impact: Catastrophic / Major / Moderate / Minor / Insignificant\n"
        "\n"
        "### Severity Rating\n"
        "\n"
        "| Dimension | Rating | Evidence |\n"
        "|-----------|--------|----------|\n"
        "| Severity | {Your assessment} | {Cite specific evidence from the "
        "intelligence data} |\n"
        "| Likelihood | {Your assessment} | {Cite specific evidence} |\n"
        "| Impact | {Your assessment} | {Cite specific evidence} |\n"
        "\n"
        "### Rating Rationale\n"
        "\n"
        "Provide detailed justification for each rating. Reference specific "
        "JIRA issues, comments, dates, and technical evidence. Do not use "
        "generic risk language -- tie each justification to concrete factors "
        "from the intelligence data.\n"
        "\n"
        "### CVE Landscape\n"
        "\n"
        "If any CVEs are referenced in the intelligence data, assess their "
        "relevance and impact. If no CVEs are relevant, state so explicitly."
    )

    template_body = template_body.replace(section2_stub, section2_replacement)

    # ── Replace Section 6 stub ──────────────────────────────────────────
    # Match from "## Section 6" header through the end of the PSRR table
    section6_start = template_body.find("## Section 6: Escalation Analysis [HUMAN REQUIRED]")
    section6_end = template_body.find("---", section6_start + 1) if section6_start != -1 else -1

    if section6_start != -1 and section6_end != -1:
        section6_replacement = (
            "## Section 6: Escalation Analysis [AI-GENERATED]\n"
            "\n"
            "Evaluate all 8 PSRR promotion criteria based on the analysis "
            "in Sections 1-5. For each criterion, determine whether it is "
            "Met, Not Met, or Partially Met, and cite specific evidence.\n"
            "\n"
            "### PSRR Promotion Assessment\n"
            "\n"
            "| # | Requirement | Met? | Evidence |\n"
            "|---|-------------|------|----------|\n"
            "| 1 | Quantified risk | {Met/Not Met/Partial} | {evidence} |\n"
            "| 2 | Actionable path | {Met/Not Met/Partial} | {evidence} |\n"
            "| 3 | Context provided | {Met/Not Met/Partial} | {evidence} |\n"
            "| 4 | Tied to an objective | {Met/Not Met/Partial} | {evidence} |\n"
            "| 5 | Named accountable risk owner | {Met/Not Met/Partial} | "
            "{evidence} |\n"
            "| 6 | Consequence of inaction | {Met/Not Met/Partial} | "
            "{evidence} |\n"
            "| 7 | Risk posture requested | {Met/Not Met/Partial} | "
            "{evidence} |\n"
            "| 8 | Acceptance timebox | {Met/Not Met/Partial} | {evidence} |\n"
            "\n"
            "**Promotion recommendation:** {READY / NOT READY / CONDITIONAL}\n"
            "**Rationale:** {Justify your recommendation}\n"
            "\n"
        )
        template_body = (
            template_body[:section6_start]
            + section6_replacement
            + template_body[section6_end:]
        )

    # ── Replace Analyst Assessment stub ─────────────────────────────────
    analyst_start = template_body.find("## Analyst Assessment [HUMAN REQUIRED]")
    analyst_end = template_body.find("---", analyst_start + 1) if analyst_start != -1 else -1

    if analyst_start != -1 and analyst_end != -1:
        decision = input_data.get("analyst_decision", "CONCUR")
        changes = input_data.get("analyst_changes", "None")
        rationale = input_data.get("analyst_rationale", "N/A")

        analyst_replacement = (
            "## Analyst Assessment [HUMAN]\n"
            "\n"
            f"**Action:** {decision}\n"
            "\n"
            f"**Changes from AI recommendation:** {changes}\n"
            "\n"
            f"**Rationale for overrides:** {rationale}\n"
            "\n"
            "**Sign-off:** Benchmark evaluation | Automated\n"
            "\n"
        )
        template_body = (
            template_body[:analyst_start]
            + analyst_replacement
            + template_body[analyst_end:]
        )

    return template_body


if __name__ == "__main__":
    main()
