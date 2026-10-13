#!/usr/bin/env bash
# Run OpenCode with the benchmark-eval agent on a risk assessment prompt.
#
# The CLI runner cannot pass large prompts via {args} (shlex.split mangles
# newlines and special characters in multi-KB text). This wrapper reads the
# prompt from input.yaml (populated by build_context.py) and passes it to
# opencode run as a properly quoted single argument.
#
# Usage: run_opencode.sh <workspace> <output_dir> <model>
set -uo pipefail

workspace="$1"
output_dir="$2"
model="$3"

# Read the assembled prompt from input.yaml
prompt=$(python3 -c "
import yaml, sys
data = yaml.safe_load(open('${workspace}/input.yaml'))
prompt = data.get('prompt', '')
if not prompt:
    print('ERROR: no prompt field in input.yaml', file=sys.stderr)
    sys.exit(1)
print(prompt)
")

if [ $? -ne 0 ] || [ -z "$prompt" ]; then
    echo "ERROR: Failed to read prompt from ${workspace}/input.yaml" >&2
    exit 1
fi

# Run OpenCode with the benchmark-eval agent (no tools, single step)
opencode run \
    --agent benchmark-eval \
    --model "$model" \
    --auto \
    --format default \
    --dir "$workspace" \
    "$prompt"
