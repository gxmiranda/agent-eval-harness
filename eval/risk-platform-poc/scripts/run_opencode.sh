#!/usr/bin/env bash
# Run OpenCode with the plan agent on a risk assessment prompt.
#
# The CLI runner cannot pass large prompts via {args} (shlex.split mangles
# newlines and special characters in multi-KB text). This wrapper reads the
# prompt from input.yaml (populated by build_context.py) and passes it to
# opencode run as a properly quoted single argument.
#
# Uses the built-in "plan" agent with a workspace-local opencode.json that
# denies ALL permissions and disables MCP servers. This ensures a strictly
# frozen-input comparison: the model can only respond with text based on
# the prompt content, with no file reads, JIRA lookups, or other tool use.
#
# Output: Uses --format json and pipes through parse_opencode_json.py to:
#   - Extract text content -> stdout (captured as stdout.log by CLI runner)
#   - Extract token/cost telemetry -> output/metrics.json (read by CLI runner)
#
# Usage: run_opencode.sh <workspace> <output_dir> <model>
set -uo pipefail

workspace="$1"
output_dir="$2"
model="$3"

# Resolve the scripts directory (where parse_opencode_json.py lives)
script_dir="$(cd "$(dirname "$0")" && pwd)"

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

# Write a lockdown opencode.json into the workspace to deny ALL tools
# and disable MCP servers. OpenCode's project-level config overrides
# the global config, and "deny" is always enforced even with --auto.
# This prevents the model from reading files, querying JIRA, or using
# any tool -- ensuring a strictly frozen-input benchmark comparison.
cat > "${workspace}/opencode.json" <<'LOCKDOWN'
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "read": "deny",
    "edit": "deny",
    "bash": "deny",
    "glob": "deny",
    "grep": "deny",
    "list": "deny",
    "task": "deny",
    "webfetch": "deny",
    "websearch": "deny",
    "lsp": "deny",
    "skill": "deny",
    "external_directory": "deny",
    "question": "deny",
    "jira_*": "deny",
    "slack_*": "deny",
    "*": "deny"
  },
  "mcp": {}
}
LOCKDOWN

# Run OpenCode with --format json and pipe through the parser.
# The parser extracts text -> stdout and telemetry -> metrics.json.
opencode run \
    --agent plan \
    --model "$model" \
    --auto \
    --format json \
    --dir "$workspace" \
    "$prompt" \
  | python3 "$script_dir/parse_opencode_json.py" "$output_dir"
