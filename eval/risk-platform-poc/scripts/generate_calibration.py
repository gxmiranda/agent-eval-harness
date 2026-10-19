#!/usr/bin/env python3
"""Generate calibration test cases for judge validation.

Creates two types of calibration cases from an existing gold-standard
assessment:

1. Self-eval: gold-standard analysis.md used as both reference AND
   candidate output. Judges should score 4-5 on all dimensions. If any
   score < 4, the judge prompt needs recalibration.

2. Degradation: programmatically weakened version of the gold-standard
   output. Judges should score 2-3 on degraded dimensions. If judges
   don't catch the degradation, the judge prompts need strengthening.

Usage:
    python3 generate_calibration.py <dataset_dir> <output_dir>

    dataset_dir: Path to the existing dataset (e.g., eval/risk-platform-poc/dataset)
    output_dir:  Path for calibration dataset (e.g., eval/risk-platform-poc/dataset-calibration)

The script picks the richest case (most adversarial challenges) as the
source for calibration.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import yaml


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: generate_calibration.py <dataset_dir> <output_dir>",
              file=sys.stderr)
        sys.exit(1)

    dataset_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not dataset_dir.is_dir():
        print(f"ERROR: dataset_dir {dataset_dir} not found", file=sys.stderr)
        sys.exit(1)

    # Pick the richest case (most challenges) as the calibration source
    source_case = _pick_source_case(dataset_dir)
    print(f"Source case: {source_case.name}", file=sys.stderr)

    # ── Generate self-eval case ─────────────────────────────────────────
    self_eval_dir = output_dir / f"{source_case.name}-self-eval"
    _create_self_eval(source_case, self_eval_dir)
    print(f"Self-eval case: {self_eval_dir}", file=sys.stderr)

    # ── Generate degradation case ───────────────────────────────────────
    degraded_dir = output_dir / f"{source_case.name}-degraded"
    _create_degraded(source_case, degraded_dir)
    print(f"Degraded case: {degraded_dir}", file=sys.stderr)

    print(f"\nCalibration dataset ready at: {output_dir}", file=sys.stderr)
    print(f"Cases: {list(p.name for p in output_dir.iterdir() if p.is_dir())}",
          file=sys.stderr)


def _pick_source_case(dataset_dir: Path) -> Path:
    """Pick the case with the most adversarial challenges."""
    best_case = None
    best_challenges = -1
    for case_dir in sorted(dataset_dir.iterdir()):
        if not case_dir.is_dir():
            continue
        ann_path = case_dir / "annotations.yaml"
        if not ann_path.exists():
            continue
        ann = yaml.safe_load(ann_path.read_text())
        challenges = int(ann.get("gold_challenges_raised", 0))
        if challenges > best_challenges:
            best_challenges = challenges
            best_case = case_dir
    if best_case is None:
        print("ERROR: No valid cases found in dataset", file=sys.stderr)
        sys.exit(1)
    return best_case


def _create_self_eval(source_case: Path, dest: Path) -> None:
    """Create a self-eval case: gold standard is both reference and candidate.

    The model's "output" is an exact copy of the gold-standard analysis.md.
    Judges compare it against itself. Expected score: 4-5 on all dimensions.
    """
    dest.mkdir(parents=True, exist_ok=True)

    # Copy gold-standard directory
    gs_src = source_case / "gold-standard"
    gs_dst = dest / "gold-standard"
    if gs_dst.exists():
        shutil.rmtree(gs_dst)
    shutil.copytree(gs_src, gs_dst)

    # Copy and modify input.yaml
    input_data = yaml.safe_load(
        (source_case / "input.yaml").read_text()
    )
    input_data["calibration_type"] = "self-eval"
    input_data["expected_scores"] = "4-5 on all dimensions"
    # The prompt field will be populated by build_context.py, but for
    # self-eval we bypass the runner entirely -- the "candidate output"
    # is the gold-standard analysis.md itself.
    (dest / "input.yaml").write_text(
        yaml.dump(input_data, default_flow_style=False, allow_unicode=True)
    )

    # Copy and modify annotations.yaml
    ann = yaml.safe_load(
        (source_case / "annotations.yaml").read_text()
    )
    ann["calibration_type"] = "self-eval"
    (dest / "annotations.yaml").write_text(
        yaml.dump(ann, default_flow_style=False, allow_unicode=True)
    )

    # Create the "candidate output" -- exact copy of gold standard
    output_dir = dest / "output"
    output_dir.mkdir(exist_ok=True)
    shutil.copy2(gs_src / "analysis.md", output_dir / "analysis.md")

    # Create a valid gates.json (all gates pass for self-eval)
    import json
    gates = [
        {"number": i, "description": f"QC-{i}", "passed": True, "details": "self-eval"}
        for i in range(1, 7)
    ]
    (output_dir / "gates.json").write_text(json.dumps(gates, indent=2))

    # Create a valid critique-results.json (no defects for self-eval)
    critique = {
        "challenges_raised": 0,
        "challenges_resolved": 0,
        "disposition": "PASS",
        "new_defects": 0,
        "mode": "calibration",
    }
    (output_dir / "critique-results.json").write_text(
        json.dumps(critique, indent=2)
    )


def _create_degraded(source_case: Path, dest: Path) -> None:
    """Create a degraded case: weakened version of the gold standard.

    Degradations applied:
    - Remove all citations (bare JIRA keys, no URLs)
    - Make recommendations generic (remove owners and timelines)
    - Weaken rating rationale (replace specific evidence with generic language)
    - Remove data gaps

    Expected score: 2-3 on degraded dimensions (D2, D5, D7, D8).
    D1 and D4 should still pass (structure and exec summary preserved).
    """
    dest.mkdir(parents=True, exist_ok=True)

    # Copy gold-standard directory (reference stays intact)
    gs_src = source_case / "gold-standard"
    gs_dst = dest / "gold-standard"
    if gs_dst.exists():
        shutil.rmtree(gs_dst)
    shutil.copytree(gs_src, gs_dst)

    # Copy and modify input.yaml
    input_data = yaml.safe_load(
        (source_case / "input.yaml").read_text()
    )
    input_data["calibration_type"] = "degraded"
    input_data["expected_scores"] = "2-3 on D2, D5, D7, D8; 4-5 on D1, D4"
    (dest / "input.yaml").write_text(
        yaml.dump(input_data, default_flow_style=False, allow_unicode=True)
    )

    # Copy and modify annotations.yaml
    ann = yaml.safe_load(
        (source_case / "annotations.yaml").read_text()
    )
    ann["calibration_type"] = "degraded"
    (dest / "annotations.yaml").write_text(
        yaml.dump(ann, default_flow_style=False, allow_unicode=True)
    )

    # Read gold-standard analysis and degrade it
    analysis = (gs_src / "analysis.md").read_text()
    degraded = _degrade_analysis(analysis)

    # Write the degraded "candidate output"
    output_dir = dest / "output"
    output_dir.mkdir(exist_ok=True)
    (output_dir / "analysis.md").write_text(degraded)

    # Create valid gates.json (structure still passes, QC-6 may fail)
    import json
    gates = [
        {"number": 1, "description": "QC-1", "passed": True, "details": "structure ok"},
        {"number": 2, "description": "QC-2", "passed": True, "details": "sections present"},
        {"number": 3, "description": "QC-3", "passed": True, "details": "ratings valid"},
        {"number": 4, "description": "QC-4", "passed": True, "details": "regulatory ok"},
        {"number": 5, "description": "QC-5", "passed": False, "details": "sources incomplete"},
        {"number": 6, "description": "QC-6", "passed": True, "details": "consequences present"},
    ]
    (output_dir / "gates.json").write_text(json.dumps(gates, indent=2))

    # Critique: some defects found
    critique = {
        "challenges_raised": 5,
        "challenges_resolved": 2,
        "disposition": "MAX ROUNDS",
        "new_defects": 3,
        "mode": "calibration",
    }
    (output_dir / "critique-results.json").write_text(
        json.dumps(critique, indent=2)
    )


def _degrade_analysis(text: str) -> str:
    """Apply systematic degradations to a gold-standard analysis."""
    # 1. Strip all URLs (make citations unverifiable)
    text = re.sub(
        r'https?://\S+', '[link removed]', text
    )

    # 2. Replace specific JIRA browse URLs with bare keys
    text = re.sub(
        r'\[([A-Z]+-\d+)\]\(https?://[^)]+\)', r'\1', text
    )

    # 3. Weaken rating rationale -- replace evidence-specific language
    #    with generic risk language
    text = re.sub(
        r'(\*\*Severity justification:\*\*)[^*]+',
        r'\1 The severity is assessed based on the general risk profile and potential impact on the organization. ',
        text
    )
    text = re.sub(
        r'(\*\*Likelihood justification:\*\*)[^*]+',
        r'\1 The likelihood is assessed based on general industry trends and the current threat landscape. ',
        text
    )
    text = re.sub(
        r'(\*\*Impact justification:\*\*)[^*]+',
        r'\1 The impact is assessed based on the potential consequences to the business. ',
        text
    )

    # 4. Make recommendations generic -- strip owners and timelines
    text = re.sub(
        r'--\s*\*\*Owner:\*\*\s*[^-\n]+', '-- **Owner:** The team', text
    )
    text = re.sub(
        r'--\s*\*\*Definition of done:\*\*\s*[^\n]+',
        '-- **Definition of done:** Complete the task', text
    )

    # 5. Remove data gaps table
    text = re.sub(
        r'### Data Gaps.*?(?=##|\Z)',
        '### Data Gaps\n\nNo significant data gaps identified.\n\n',
        text,
        flags=re.DOTALL,
    )

    # 6. Add a marker so we can verify the degradation was applied
    text = text.replace(
        "[AI-GENERATED]",
        "[AI-GENERATED] [CALIBRATION-DEGRADED]",
        1,  # Only first occurrence
    )

    return text


if __name__ == "__main__":
    main()
