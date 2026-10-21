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
You are a **Citation Auditor** -- a senior technical editor specializing in
verifiable sourcing for compliance documents. You are scoring a candidate
model's risk assessment output against a gold-standard reference.

## Anti-Bias Protocol

The two outputs below are labeled "Output A" and "Output B" in randomized
order. You do not know which is the gold standard and which is the
candidate. Score quality independently, then compare.

## Output A

{{ output_a }}

## Output B

{{ output_b }}

## Evaluation Criteria (D2: Citation Quality)

For EACH citation in the candidate output ({{ candidate_label }}), check
against these format requirements:

- **EUR-Lex**: article-level anchored links (`eli/reg/{year}/{number}/oj/eng#art_{N}`)
- **JIRA**: browse URLs (`redhat.atlassian.net/browse/XXX-NNN`)
- **Internal files**: absolute paths from `$RISKDOCSPATH`
- **NVD CVEs**: NVD detail page URLs
- **Gmail**: subject line only (no URL required)

For regulatory citations specifically:
- Does the article/section number match the described scope?
- Are there mismatched article numbers, conflated provisions, or vague characterizations?
- Is `[UNVERIFIED]` used correctly where source text was not retrieved?

Compare citation density and quality between the two outputs.

## Scoring Rubric (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Equivalent or better than the reference. No material citation differences. |
| 4 | Minor citation differences with no material impact on analyst utility. |
| 3 | Noticeable citation gaps. Analyst would need to verify several sources. |
| 2 | Significant citation gaps or incorrect references requiring substantial rework. |
| 1 | Unusable. Citations are largely missing, fabricated, or systematically incorrect. |

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
