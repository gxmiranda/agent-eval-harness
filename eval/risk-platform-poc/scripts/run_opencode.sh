#!/usr/bin/env bash
# Run OpenCode with the plan agent on a risk assessment prompt.
#
# The CLI runner cannot pass large prompts via {args} (shlex.split mangles
# newlines and special characters in multi-KB text). This wrapper reads the
# prompt from input.yaml (populated by build_context.py) and passes it to
# opencode run as a properly quoted single argument.
#
# Uses the built-in "plan" agent which has edit and bash set to "ask".
# With --auto, non-denied permissions are auto-approved, but plan mode
# only suggests changes without executing them -- producing pure text
# output. Custom agents trigger an "assistant message prefill" error on
# the Vertex AI provider, so we use the built-in plan agent instead.
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

# Run OpenCode with the plan agent (text output only, no file modifications)
opencode run \
    --agent plan \
    --model "$model" \
    --auto \
    --format default \
    --dir "$workspace" \
    "$prompt"
