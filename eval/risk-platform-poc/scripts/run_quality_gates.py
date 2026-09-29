#!/usr/bin/env python3
"""Run quality gates and Garth critique on candidate output.

Runs as an after_each hook in the eval harness. Locates the candidate's
analysis.md from the output directory (or extracts it from stdout),
runs check_all_gates() for deterministic QC-1 through QC-6 scoring,
and runs run_garth_critique() for D6 adversarial durability scoring.

Writes:
    {output_dir}/gates.json           -- quality gate results
    {output_dir}/critique-results.json -- Garth critique metrics

Environment variables (set by eval.yaml hooks):
    CASE_WORKSPACE  -- absolute path to the case workspace directory
    RP_PATH         -- absolute path to the risk-platform repository root
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    ws = Path(os.environ["CASE_WORKSPACE"])
    rp_path = Path(os.environ["RP_PATH"])

    # Add Risk Platform source to import path
    rp_src = rp_path / "src"
    if str(rp_src) not in sys.path:
        sys.path.insert(0, str(rp_src))

    # Set RISK_PLATFORM_PATH for risk_platform.config
    os.environ.setdefault("RISK_PLATFORM_PATH", str(rp_path))

    from risk_platform.quality_gates import check_all_gates

    output_dir = ws / "output"
    output_dir.mkdir(exist_ok=True)

    # ── Locate the candidate's analysis output ──────────────────────────
    analysis_path = _find_analysis(output_dir, ws)
    if analysis_path is None:
        _write_error(output_dir, "No analysis.md found in output")
        return

    # ── Run deterministic quality gates (QC-1 through QC-6) ─────────────
    try:
        gates = check_all_gates(str(analysis_path))
        gates_data = [
            {
                "number": g.number,
                "description": g.description,
                "passed": g.passed,
                "details": g.details,
            }
            for g in gates
        ]
    except Exception as exc:
        gates_data = [
            {
                "number": 0,
                "description": "quality_gates.py execution error",
                "passed": False,
                "details": str(exc),
            }
        ]

    (output_dir / "gates.json").write_text(
        json.dumps(gates_data, indent=2), encoding="utf-8"
    )

    # ── Run Garth critique for D6 (adversarial durability) ──────────────
    _run_garth(analysis_path, ws, output_dir, rp_path)


def _find_analysis(output_dir: Path, ws: Path) -> Path | None:
    """Locate the candidate's analysis.md in output artifacts.

    Checks for an explicit analysis.md file first, then attempts to
    extract markdown content from captured stdout.
    """
    # Check explicit file locations
    for candidate in [output_dir / "analysis.md", ws / "analysis.md"]:
        if candidate.exists() and candidate.stat().st_size > 100:
            return candidate

    # If runner captured stdout, extract markdown content
    # The claude-code and responses-api runners write stdout to files
    # in the output directory or capture it in the conversation.
    for path in output_dir.iterdir():
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "## Executive Summary" in content and "## Section 1" in content:
            analysis_path = output_dir / "analysis.md"
            analysis_path.write_text(content, encoding="utf-8")
            return analysis_path

    return None


def _run_garth(
    analysis_path: Path, ws: Path, output_dir: Path, rp_path: Path
) -> None:
    """Run Garth single-pass critique and write results.

    Uses the Risk Platform's run_garth_critique() with an AIService
    instance. Requires Anthropic API credentials (ANTHROPIC_API_KEY or
    GOOGLE_CLOUD_PROJECT for Vertex AI).
    """
    try:
        from risk_platform.ai_service import AIService
        from risk_platform.critique import run_garth_critique

        ai = AIService()

        # Load JIRA context for the Critic (zero-context adversarial review)
        jira_context = ""
        jira_path = ws / "gold-standard" / "jira-context.txt"
        if jira_path.exists():
            jira_context = jira_path.read_text(encoding="utf-8")

        # Create a session directory for critique state files
        session_dir = output_dir / "critique-session"
        session_dir.mkdir(exist_ok=True)

        state = run_garth_critique(analysis_path, session_dir, jira_context, ai)

        results = {
            "challenges_raised": state.total_challenges,
            "challenges_resolved": state.resolved_challenges,
            "disposition": state.disposition,
            "new_defects": state.total_challenges - state.resolved_challenges,
            "mode": state.mode,
            "severity_changes": state.severity_changes,
        }
    except Exception as exc:
        results = {
            "error": str(exc),
            "challenges_raised": 0,
            "challenges_resolved": 0,
            "new_defects": 0,
            "disposition": None,
            "mode": "garth",
        }

    (output_dir / "critique-results.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )


def _write_error(output_dir: Path, msg: str) -> None:
    """Write error state to both output files."""
    output_dir.mkdir(exist_ok=True)
    error_gate = [
        {
            "number": 0,
            "description": msg,
            "passed": False,
            "details": msg,
        }
    ]
    (output_dir / "gates.json").write_text(
        json.dumps(error_gate, indent=2), encoding="utf-8"
    )
    (output_dir / "critique-results.json").write_text(
        json.dumps(
            {"error": msg, "challenges_raised": 0, "new_defects": 0},
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
