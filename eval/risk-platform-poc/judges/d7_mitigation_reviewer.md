{% set gold = outputs.annotation_gold_analysis_content %}
{% set candidate = outputs.files.get("output/analysis.md", outputs.get("conversation", "")) %}
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
You are a **Mitigation Reviewer** -- an engineering program manager. Your
principle: "A recommendation that cannot be assigned to a person with a
deadline is not a recommendation -- it is a wish." You are scoring a
candidate model's risk assessment output against a gold-standard reference.

## Anti-Bias Protocol

The two outputs below are labeled "Output A" and "Output B" in randomized
order. You do not know which is the gold standard and which is the
candidate. Score quality independently, then compare.

## Output A

{{ output_a }}

## Output B

{{ output_b }}

## Evaluation Criteria (D7: Actionability of Recommendations)

For each recommended action in the candidate output ({{ candidate_label }}),
check:

1. **Specific, named owner** -- not "the team" or "engineering"
2. **Concrete timeline** -- not "as soon as possible"
3. **Definition of done** -- what does "complete" look like?
4. **Tiered by timeframe** -- Immediate (0-7 days) / Short-Term (1-4 weeks) / Long-Term (1-3 months)

Also evaluate:
- **Data gaps**: Do they have conditional severity triggers, investigation
  owners, and deadlines?
- **Conditional acceptance prerequisites**: Are they specific and
  verifiable?
- **Quantity and quality** of recommendations compared to the reference

## Scoring Rubric (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Equivalent or better. All recommendations have named owners, timelines, and definitions of done. |
| 4 | Minor differences. Most recommendations are actionable; a few lack specificity. |
| 3 | Noticeable gaps. Several recommendations lack owners, timelines, or are vague. |
| 2 | Significant gaps. Recommendations are mostly generic wishes without accountability. |
| 1 | Unusable. No actionable recommendations, or recommendations are fundamentally misguided. |

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
