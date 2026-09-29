#!/usr/bin/env python3
"""Run quality gates and Garth critique on candidate output.

Runs as an after_each hook in the eval harness. Locates the candidate's
analysis.md from the output directory (written by Write tool) or from
the conversation stream (when using max_turns=1 / no tool calls),
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

    Search order:
    1. Explicit analysis.md file (written via Write tool)
    2. Extract from stdout.log stream-json (max_turns=1, no tool calls)
    3. Scan any output file for risk assessment markdown content
    """
    # 1. Check for explicit analysis.md file
    for candidate in [output_dir / "analysis.md", ws / "analysis.md"]:
        if candidate.exists() and candidate.stat().st_size > 100:
            return candidate

    # 2. Extract from stdout.log (stream-json from claude --print)
    # With max_turns=1, the model's response text is in the stream-json
    # assistant message events. Extract the last assistant text.
    stdout_path = output_dir / "stdout.log"
    if not stdout_path.exists():
        stdout_path = ws / "stdout.log"
    if stdout_path.exists():
        content = _extract_assistant_text(stdout_path)
        if content and "## Executive Summary" in content:
            analysis_path = output_dir / "analysis.md"
            analysis_path.write_text(content, encoding="utf-8")
            return analysis_path

    # 3. Fallback: scan any output file for markdown content
    if output_dir.exists():
        for path in output_dir.iterdir():
            if not path.is_file() or path.name in ("gates.json", "critique-results.json"):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if "## Executive Summary" in content and "## Section 1" in content:
                analysis_path = output_dir / "analysis.md"
                if path != analysis_path:
                    analysis_path.write_text(content, encoding="utf-8")
                return analysis_path

    return None


def _extract_assistant_text(stdout_path: Path) -> str:
    """Extract the assistant's response text from a stream-json stdout.log.

    Parses the stream-json line by line looking for assistant message
    events (same approach as execute.py::_extract_last_assistant_text,
    but without a size limit since we need the full analysis).
    """
    texts: list[str] = []
    raw_content = stdout_path.read_text(encoding="utf-8", errors="replace")

    for line in raw_content.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            # Not JSON -- might be raw text output (--output-format text)
            continue
        try:
            obj = json.loads(line)
        except (ValueError, TypeError):
            continue

        # stream-json: "result" event has the final text
        if obj.get("type") == "result" and isinstance(obj.get("result"), str):
            texts.append(obj["result"])
        # stream-json: "assistant" message events contain text blocks
        elif obj.get("type") == "assistant" and not obj.get("parent_tool_use_id"):
            msg = obj.get("message") or {}
            for block in msg.get("content") or []:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = (block.get("text") or "").strip()
                    if text:
                        texts.append(text)
        # json output format: single result object
        elif "result" in obj and isinstance(obj.get("result"), str):
            texts.append(obj["result"])

    if texts:
        return texts[-1]

    # If no JSON was found, the output might be raw text (--output-format text)
    if "## Executive Summary" in raw_content:
        return raw_content

    return ""


def _run_garth(
    analysis_path: Path, ws: Path, output_dir: Path, rp_path: Path
) -> None:
    """Run Garth single-pass critique and write results.

    Uses the Risk Platform's run_garth_critique() with an AIService
    instance. Requires Anthropic API credentials. Falls back gracefully
    if the critique cannot run (missing dependencies, auth issues).
    """
    # Force direct Anthropic backend for the critique to avoid
    # google-auth dependency issues with Vertex AI.
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        # Temporarily unset GOOGLE_CLOUD_PROJECT to force direct backend
        gcp_project = os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
    else:
        gcp_project = None

    try:
        from risk_platform.ai_service import AIService
        from risk_platform.critique import run_garth_critique

        ai = AIService()

        # Load JIRA context for the Critic (zero-context adversarial review)
        jira_context = ""
        # Read from source dataset, not workspace
        case_source_dir = Path(os.environ.get("CASE_SOURCE_DIR", ""))
        jira_path = case_source_dir / "gold-standard" / "jira-context.txt"
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
    finally:
        # Restore GOOGLE_CLOUD_PROJECT if we removed it
        if gcp_project is not None:
            os.environ["GOOGLE_CLOUD_PROJECT"] = gcp_project

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
