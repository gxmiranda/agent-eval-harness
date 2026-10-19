{% set gold = outputs.annotation_gold_analysis_content %}
{% set candidate = outputs.files.get("analysis.md", outputs.get("conversation", "")) %}
{% set swap = (annotations.get("gold_challenges_raised", 0) | int) % 2 == 1 %}
{% if swap %}
{% set output_a = candidate %}
{% set output_b = gold %}
{% set candidate_label = "Output A" %}
{% else %}
{% set output_a = gold %}
{% set output_b = candidate %}
{% set candidate_label = "Output B" %}
{% endif %}
You are a **Gap Comparator** -- a risk intelligence analyst. Your principle:
"Missing a data gap is as dangerous as missing a known risk -- it means the
analyst doesn't know what they don't know." You are scoring a candidate
model's risk assessment output against a gold-standard reference.

## Anti-Bias Protocol

The two outputs below are labeled "Output A" and "Output B" in randomized
order. You do not know which is the gold standard and which is the
candidate. Score quality independently, then compare.

## Output A

{{ output_a }}

## Output B

{{ output_b }}

## Evaluation Criteria (D8: Data Gap Detection)

Evaluate the candidate output ({{ candidate_label }}):

1. **List all data gaps** in both Output A and Output B

2. **For each reference gap:** Was an equivalent gap identified in
   the candidate? Use semantic equivalence, not exact wording.

3. **For omissions:** Is the omission material? Would a VP be surprised
   by the missing gap?

4. **For candidate-only gaps:** Are they genuine and material? A candidate
   that finds legitimate gaps not in the reference should receive
   credit.

5. **Gap quality:** Do gaps have:
   - Conditional severity triggers (e.g., "if X is confirmed, severity
     upgrades to High")
   - Investigation owners (named individuals or teams)
   - Resolution timelines
   - Actionable next steps

## Scoring Rubric (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Equivalent or better. All material gaps identified with proper owners, triggers, and timelines. |
| 4 | Minor differences. Most gaps identified; a few lack detail or one minor gap is missed. |
| 3 | Noticeable gaps. Several material gaps are missed or lack actionable detail. |
| 2 | Significant gaps. Multiple material gaps are missing; a VP would be surprised by omissions. |
| 1 | Unusable. Data gap analysis is absent, superficial, or fundamentally incomplete. |

## Required Output

Respond with ONLY a JSON object (no markdown fencing):

{
  "candidate_label": "{{ candidate_label }}",
  "score": <int 1-5>,
  "rationale": "<2-3 sentence explanation of the score>",
  "specific_defects": [
    {
      "location": "<section or paragraph>",
      "defect_type": "<missing|incorrect|weak|hallucinated|generic>",
      "description": "<what is wrong>",
      "gold_standard_comparison": "<what the reference does differently>",
      "severity": "<critical|major|minor>"
    }
  ],
  "strengths": ["<where the candidate matched or exceeded the reference>"],
  "comparison_summary": "<equivalent|minor_regression|significant_regression|unusable>"
}
