#!/usr/bin/env python3
"""Parse OpenCode --format json output into text + metrics.

Reads OpenCode JSON events from stdin, extracts:
- Text content from "text" events -> printed to stdout
- Token/cost telemetry from "step_finish" events -> written to metrics.json

Usage:
    opencode run --format json "prompt" | python3 parse_opencode_json.py <output_dir>

The CLI runner captures stdout as stdout.log (the analysis text).
The metrics.json file is read by the CLI runner for cost reporting.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: parse_opencode_json.py <output_dir>", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(sys.argv[1])
    output_dir.mkdir(parents=True, exist_ok=True)

    text_parts: list[str] = []
    total_input_tokens = 0
    total_output_tokens = 0
    total_cache_read = 0
    total_cache_write = 0
    total_cost = 0.0
    model = ""
    num_steps = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue

        event_type = event.get("type", "")
        part = event.get("part", {})

        if event_type == "text":
            text = part.get("text", "")
            if text:
                text_parts.append(text)

        elif event_type == "step_finish":
            num_steps += 1
            tokens = part.get("tokens", {})
            total_input_tokens += tokens.get("input", 0)
            total_output_tokens += tokens.get("output", 0)
            cache = tokens.get("cache", {})
            total_cache_read += cache.get("read", 0)
            total_cache_write += cache.get("write", 0)
            cost = part.get("cost")
            if isinstance(cost, (int, float)):
                total_cost += cost

        elif event_type == "session_start":
            # Some events may carry model info
            pass

    # Write the text content to stdout (captured as stdout.log by CLI runner)
    full_text = "".join(text_parts)
    if full_text:
        print(full_text)
    else:
        print("ERROR: No text content found in OpenCode JSON output",
              file=sys.stderr)

    # Write metrics.json for the CLI runner's cost reporting
    metrics = {
        "token_usage": {
            "input": total_input_tokens + total_cache_write,
            "output": total_output_tokens,
            "cache_read": total_cache_read,
            "cache_write": total_cache_write,
        },
        "cost_usd": total_cost if total_cost > 0 else None,
        "num_turns": num_steps,
    }

    metrics_path = output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))
    print(f"Metrics written: tokens_in={total_input_tokens + total_cache_write} "
          f"tokens_out={total_output_tokens} cost=${total_cost:.4f} "
          f"steps={num_steps}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
