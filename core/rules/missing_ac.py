class MissingACRule:
    id = "MISSING_AC"
    severity = "ERROR"
    description = "Flags user stories without testable acceptance criteria"

    def prompt(self, text: str) -> str:
        return f"""You are a strict Product Owner reviewing a PRD for missing acceptance criteria.

Scan the following PRD text for user stories or requirements that lack testable acceptance criteria.
A valid AC must be specific, measurable, and testable (Given/When/Then, or a clear pass/fail condition).

For each story or requirement missing ACs, return a JSON array:
[
  {{
    "rule": "MISSING_AC",
    "severity": "ERROR",
    "line_hint": "quote the story or requirement (max 20 words)",
    "issue": "explain what acceptance criteria are missing",
    "suggestion": "write one example AC for this requirement"
  }}
]

If all stories have adequate ACs, return empty array [].
Only return valid JSON, no other text.

PRD TEXT:
{text}"""
