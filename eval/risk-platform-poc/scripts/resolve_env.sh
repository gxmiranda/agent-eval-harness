#!/usr/bin/env bash
# Resolve RP_PATH and write .hook-outputs.yaml for hook propagation.
#
# Called by the before_all hook in eval.yaml and its overlays.
# Accepts optional --critique-model and --triage-model flags to inject
# AI_MODEL_CRITIQUE and AI_MODEL_TRIAGE env var overrides for the
# Risk Platform's per-role model routing (used by the after_each hook's
# Garth critique via AIService).
#
# Usage:
#   resolve_env.sh                                          # Anthropic defaults
#   resolve_env.sh --critique-model openai/gpt-6-sol \
#                  --triage-model openai/gpt-6-luna         # OpenAI overrides
set -euo pipefail

# ── Parse optional task model overrides ─────────────────────────────────
critique_model="${AI_MODEL_CRITIQUE:-}"
triage_model="${AI_MODEL_TRIAGE:-}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --critique-model) critique_model="$2"; shift 2;;
    --triage-model)   triage_model="$2";   shift 2;;
    *)                shift;;
  esac
done

# ── Resolve RP_PATH: explicit env > sibling checkouts > error ───────────
rp="${RP_PATH:-}"
if [ -z "$rp" ] || [ ! -d "$rp/src/risk_platform" ]; then
  for candidate in \
    "../risk/risk-platform" \
    "../risk-platform" \
    "../../risk/risk-platform" \
    "$HOME/repos/risk/risk-platform"; do
    if [ -d "$candidate/src/risk_platform" ]; then
      rp="$(cd "$candidate" && pwd)"
      break
    fi
  done
fi

if [ -z "$rp" ] || [ ! -d "$rp/src/risk_platform" ]; then
  echo "ERROR: Cannot find risk-platform repo." >&2
  echo "Set RP_PATH to the risk-platform checkout, e.g.:" >&2
  echo "  export RP_PATH=/path/to/risk-platform" >&2
  exit 1
fi

echo "RP_PATH resolved: $rp" >&2

# ── Write hook outputs for forward propagation ──────────────────────────
# The harness reads .hook-outputs.yaml after before_all and merges the
# env block into all subsequent hook subprocesses (before_each, after_each).
cat > .hook-outputs.yaml <<EOF
env:
  RP_PATH: "$rp"
  RISK_PLATFORM_PATH: "$rp"
  PYTHONPATH: "$rp/src"
  GOOGLE_CLOUD_PROJECT: "${GOOGLE_CLOUD_PROJECT:-}"
  ANTHROPIC_VERTEX_PROJECT_ID: "${ANTHROPIC_VERTEX_PROJECT_ID:-}"
  CLOUD_ML_REGION: "${CLOUD_ML_REGION:-us-east5}"
  OPENAI_API_KEY: "${OPENAI_API_KEY:-}"
  AI_MODEL_CRITIQUE: "$critique_model"
  AI_MODEL_TRIAGE: "$triage_model"
EOF
