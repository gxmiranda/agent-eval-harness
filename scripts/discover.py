#!/usr/bin/env python3
"""Discover eval configs and print results as JSON.

Shared helper used by all eval skill SKILL.md files for config
discovery and verification.

Usage:
    # Auto-discover all configs in the project
    python3 scripts/discover.py [--project-root <path>]

    # Verify an explicit --config path exists (resolves relative to project root)
    python3 scripts/discover.py --verify <config-path> [--project-root <path>]

Discovery output (JSON):
    {
        "configs": [{"path": "...", "eval_name": "...", "is_root": true}],
        "layout": "root|nested|flat|mixed|none",
        "count": 1
    }

Verify output (JSON):
    {
        "exists": true,
        "resolved_path": "/absolute/path/to/eval.yaml",
        "eval_name": "risk-platform-benchmark"
    }
    Exit code 0 if found, 1 if not found.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import agent_eval._bootstrap  # noqa: F401 — auto-activate venv
from agent_eval.config import discover_configs, infer_layout


def main():
    parser = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project-root", default=".",
                        help="Project root directory (default: cwd)")
    parser.add_argument("--verify", metavar="CONFIG_PATH", default=None,
                        help="Verify that a specific config file exists. "
                             "Path is resolved relative to --project-root. "
                             "Exits 0 if found, 1 if not.")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()

    if args.verify is not None:
        _verify_config(args.verify, project_root)
    else:
        _discover_configs(project_root)


def _verify_config(config_path: str, project_root: Path) -> None:
    """Verify an explicit config path exists and print its metadata."""
    import yaml as _yaml

    candidate = Path(config_path)

    # Resolve relative paths against the project root
    if not candidate.is_absolute():
        candidate = project_root / candidate

    resolved = candidate.resolve()

    if not resolved.is_file():
        result = {
            "exists": False,
            "requested_path": config_path,
            "resolved_path": str(resolved),
            "error": f"Config file not found at {resolved}",
        }
        print(json.dumps(result, indent=2))
        sys.exit(1)

    # Extract eval_name from the config
    eval_name = None
    try:
        with resolved.open() as f:
            head = _yaml.safe_load(f) or {}
        if isinstance(head, dict):
            # Same priority chain as discover_configs
            skill_ref = (head.get("execution") or {}).get("skill") or head.get("skill")
            if skill_ref:
                eval_name = skill_ref
            elif head.get("name"):
                sanitized = head["name"].lower().replace(" ", "-")
                sanitized = "".join(
                    c for c in sanitized if c.isalnum() or c in "._-"
                )
                eval_name = sanitized or None
    except Exception:
        pass

    if not eval_name:
        if resolved.name == "eval.yaml":
            eval_name = resolved.parent.name
        else:
            eval_name = resolved.stem

    result = {
        "exists": True,
        "resolved_path": str(resolved),
        "eval_name": eval_name,
    }
    print(json.dumps(result, indent=2))


def _discover_configs(project_root: Path) -> None:
    """Auto-discover all eval configs in the project."""
    configs = discover_configs(project_root)
    layout = infer_layout(configs)

    result = {
        "configs": [
            {
                "path": str(c.path),
                "eval_name": c.eval_name,
                "is_root": c.is_root,
            }
            for c in configs
        ],
        "layout": layout,
        "count": len(configs),
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
