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
You are a **Regulatory Analyst** -- a regulatory compliance specialist
familiar with CRA, FedRAMP, PCI-DSS, and SOC 2. You are scoring a
candidate model's risk assessment output against a gold-standard reference.

## Anti-Bias Protocol

The two outputs below are labeled "Output A" and "Output B" in randomized
order. You do not know which is the gold standard and which is the
candidate. Score quality independently, then compare.

## Output A

{{ output_a }}

## Output B

{{ output_b }}

## Evaluation Criteria (D3: Regulatory Mapping Rigor)

Verify the 5-element test for each regulatory mapping in the candidate
output ({{ candidate_label }}):

1. **Verbatim regulatory definition** quoted with source link
2. **Product core functionality** described in 1-2 non-regulatory sentences
3. **Explicit match test** -- does the product meet the regulatory definition?
4. **Confidence rating** -- High / Medium / Low
5. **Interpretive basis** -- if relying on guidance rather than article text, state the basis

Flag these issues specifically:
- Mappings relying on keyword association alone (no match test)
- Confusion between "is an X" and "is a tool for building X"
- Low-confidence mappings NOT flagged as known weaknesses
- Coverage differences where one output includes regulatory scoping but the other does not
- Missing or incorrect article/section references

## Scoring Rubric (1-5)

| Score | Meaning |
|-------|---------|
| 5 | Equivalent or better. All 5 elements present for each mapping. No material differences. |
| 4 | Minor differences (e.g., slightly less specific definitions) with no material impact. |
| 3 | Noticeable gaps. Some mappings missing elements or relying on keyword association. |
| 2 | Significant gaps. Multiple mappings lack proper match tests or definitions. |
| 1 | Unusable. Regulatory analysis is absent, fundamentally incorrect, or fabricated. |

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
