class DependencyGapRule:
    id = "DEPENDENCY_GAP"
    severity = "WARNING"
    description = "Flags references to undefined features, systems, or data sources"

    def prompt(self, text: str) -> str:
        return f"""You are a strict Product Owner reviewing a PRD for undefined dependencies.

Scan the PRD for references to:
- Features or systems mentioned but never defined in the document
- Third-party integrations referenced without a spec or link
- Data sources assumed to exist without specification
- APIs or services mentioned without contract details
- Other teams or components assumed to deliver something without a formal dependency

For each dependency gap found, return a JSON array:
[
  {{
    "rule": "DEPENDENCY_GAP",
    "severity": "WARNING",
    "line_hint": "quote the reference (max 15 words)",
    "issue": "what is undefined or assumed",
    "suggestion": "what needs to be defined or linked"
  }}
]

If no gaps found, return empty array [].
Only return valid JSON, no other text.

PRD TEXT:
{text}"""
