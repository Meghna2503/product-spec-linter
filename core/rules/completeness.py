class CompletenessRule:
    id = "COMPLETENESS"
    severity = "SUGGESTION"
    description = "Checks for missing standard PRD sections"

    REQUIRED_SECTIONS = [
        ("non-functional requirements", "performance, security, accessibility targets"),
        ("out of scope", "explicit list of what is NOT included in this release"),
        ("rollback plan", "what happens if the feature is reverted"),
        ("error states", "how the system behaves when things go wrong"),
        ("mobile / responsive behaviour", "behaviour on mobile devices"),
    ]

    def prompt(self, text: str) -> str:
        sections = "\n".join([f"- {s[0]}: {s[1]}" for s in self.REQUIRED_SECTIONS])
        return f"""You are a strict Product Owner reviewing a PRD for completeness.

Check whether the following standard sections are present and adequately addressed:
{sections}

For each section that is missing or only superficially mentioned, return a JSON array:
[
  {{
    "rule": "COMPLETENESS",
    "severity": "SUGGESTION",
    "line_hint": "name of missing section",
    "issue": "what is missing or insufficient",
    "suggestion": "what should be added"
  }}
]

If all sections are present, return empty array [].
Only return valid JSON, no other text.

PRD TEXT:
{text}"""
