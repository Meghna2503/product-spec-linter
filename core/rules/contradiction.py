class ContradictionRule:
    id = "CONTRADICTION"
    severity = "ERROR"
    description = "Detects conflicting requirements within the document"

    def prompt(self, text: str) -> str:
        return f"""You are a strict Product Owner reviewing a PRD for contradictions.

Read the ENTIRE PRD carefully and identify any statements that directly conflict with each other.
Look for: conflicting scope statements, mutually exclusive requirements, 
conflicting user permissions, contradictory technical constraints, 
or stories whose acceptance criteria contradict each other.

For each contradiction found, return a JSON array:
[
  {{
    "rule": "CONTRADICTION",
    "severity": "ERROR",
    "line_hint": "quote the FIRST conflicting statement (max 15 words)",
    "conflict_with": "quote the SECOND conflicting statement (max 15 words)",
    "issue": "explain why these two statements conflict",
    "suggestion": "how to resolve the contradiction"
  }}
]

If no contradictions found, return empty array [].
Only return valid JSON, no other text.

PRD TEXT:
{text}"""
