class AmbiguityRule:
    id = "AMBIGUITY"
    severity = "WARNING"
    description = "Flags vague, unmeasurable language in requirements"

    VAGUE_TERMS = [
        "fast", "quickly", "easily", "simple", "intuitive", "user-friendly",
        "seamless", "robust", "scalable", "efficient", "modern", "clean",
        "better", "improved", "nice", "good", "smooth", "soon", "later",
        "major browsers", "popular payment methods", "all devices",
        "large number", "many users", "high performance"
    ]

    def prompt(self, text: str) -> str:
        return f"""You are a strict Product Owner reviewing a PRD for ambiguous requirements.

Scan the following PRD text for vague, unmeasurable, or undefined terms.
Focus on terms like: {', '.join(self.VAGUE_TERMS)} — or similar language without metrics.

For each ambiguous statement found, return a JSON array:
[
  {{
    "rule": "AMBIGUITY",
    "severity": "WARNING",
    "line_hint": "quote the ambiguous phrase (max 15 words)",
    "issue": "brief explanation of why it's ambiguous",
    "suggestion": "concrete rewrite with a measurable criterion"
  }}
]

If no ambiguity found, return empty array [].
Only return valid JSON, no other text.

PRD TEXT:
{text}"""
