import json
import re


# ─────────────────────────────────────────────
# BENCHMARK REFERENCES (embedded per rule)
# ─────────────────────────────────────────────
# AMBIGUITY      → IEEE 830 SRS clarity requirements
# MISSING_AC     → BDD / Gherkin Given-When-Then standard
# CONTRADICTION  → RFC 2119 modal keyword consistency
# DEPENDENCY_GAP → SAFe PI Planning blast-radius analysis
# COMPLETENESS   → INVEST criteria (Independent, Negotiable,
#                  Valuable, Estimable, Small, Testable)
# EDGE_CASES     → OWASP Top-10, NFR checklists,
#                  state-machine / session patterns
# ─────────────────────────────────────────────

RULE_PROMPTS = {

    "AMBIGUITY": """
You are a senior requirements analyst applying IEEE 830 SRS clarity standards.

BENCHMARK: IEEE 830 requires every requirement to be unambiguous — it must have
only ONE possible interpretation. Flag any language that violates this.

WEASEL WORDS to always flag as ERROR:
  "user-friendly", "easy to use", "fast", "seamless", "robust", "flexible",
  "intuitive", "simple", "as needed", "etc.", "and so on", "appropriate",
  "adequate", "reasonable", "modern", "nice", "clean", "efficient",
  "as required", "best effort", "should work", "might", "could", "may need to"

VAGUE QUALIFIERS to flag as WARNING:
  "should" (unless RFC 2119 context), "usually", "often", "sometimes",
  "quickly", "slowly", "large", "small", "many", "few", "several",
  missing numeric thresholds (e.g. "fast response" with no ms target)

SUGGESTIONS:
  Any sentence where the subject or actor is unclear (passive voice with no
  named actor, e.g. "data will be saved" — by whom? when?)

SEVERITY RULES:
  ERROR   = vague word that would cause two developers to implement differently
  WARNING = imprecise but meaning is inferable with effort
  SUGGESTION = style improvement, passive voice, unnamed actor

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (null if none)

Return ONLY a JSON array. No markdown. No explanation.
""",

    "MISSING_AC": """
You are a BDD practitioner evaluating acceptance criteria against the
Gherkin Given-When-Then (GWT) standard used in SAFe and Scrum.

BENCHMARK: Every user story MUST have at least one testable acceptance criterion
in the format: Given [precondition], When [action], Then [outcome].

ERROR — raise if ANY of these are missing:
  1. No acceptance criteria section at all
  2. AC exists but contains zero Given-When-Then or equivalent scenarios
  3. AC exists but outcomes are not verifiable / measurable
     (e.g. "user should feel confident" is NOT testable)
  4. AC covers happy path only, with no mention of error states

WARNING — raise if:
  1. AC exists and has GWT but is missing the error/failure scenario
  2. An AC scenario has an unmeasurable "Then" (no specific value, count, or
     state change described)
  3. Multiple actors are involved but only one actor's AC is described

SUGGESTION — raise if:
  1. AC could benefit from a specific performance threshold
     (e.g. "login succeeds" → "login succeeds within 2 seconds")
  2. AC does not mention what happens to UI state after the action

SEVERITY RULES:
  ERROR   = story cannot be estimated or tested without this AC
  WARNING = story could be started but dev will need to ask questions
  SUGGESTION = optional improvement to make AC crisper

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (null if none)

Return ONLY a JSON array. No markdown. No explanation.
""",

    "CONTRADICTION": """
You are a requirements consistency reviewer applying RFC 2119 modal keyword
rules and internal logical consistency checks.

BENCHMARK: RFC 2119 defines strict meanings for MUST / MUST NOT / SHALL /
SHOULD / SHOULD NOT / MAY / OPTIONAL. A contradiction occurs when:
  - The same behaviour is both required and forbidden
  - Two requirements describe conflicting states for the same entity
  - A requirement uses "MUST" in one place and "SHOULD" for the same behaviour
    elsewhere (priority conflict)
  - A condition in the AC contradicts a condition in the story description

ERROR — raise if:
  1. Same field/action/state is both required AND forbidden (direct contradiction)
  2. Two acceptance criteria produce conflicting post-conditions for the same
     system state
  3. A MUST requirement is overridden by a SHOULD or MAY in another sentence
     about the same subject

WARNING — raise if:
  1. Two requirements describe overlapping behaviour with slightly different
     outcomes (potential conflict that needs clarification)
  2. An AC scenario assumes a precondition that contradicts the story's stated
     context

SUGGESTION — raise if:
  1. Modal keyword usage is inconsistent in style but not logically contradictory
     (e.g. mixing "shall" and "must" for same priority level)

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (the conflicting text snippet)

Return ONLY a JSON array. No markdown. No explanation.
""",

    "DEPENDENCY_GAP": """
You are a solution architect performing SAFe PI Planning blast-radius analysis.

BENCHMARK: SAFe requires stories to identify all system dependencies before
entering a sprint. A dependency gap exists when the spec does not acknowledge
a service, API, data store, or team that will be affected or required.

BLAST RADIUS CHECKLIST — flag as ERROR if spec touches these without
explicitly naming the dependency:
  - Authentication / session service (login, token, SSO)
  - Notification service (email, SMS, push)
  - Payment gateway
  - External API or third-party integration
  - Database schema change (add/modify/delete field or table)
  - GDPR / data-deletion / data-retention implications
  - Shared microservice used by other teams
  - File storage / CDN
  - Search index (Elasticsearch, Algolia etc.)
  - Caching layer (Redis, Memcached)
  - Background job / queue (Celery, SQS, RabbitMQ)
  - Analytics / event tracking

ERROR — raise if:
  1. Story clearly implies one of the above dependencies but names none
  2. A data deletion/update is described with no mention of cascade rules,
     GDPR compliance, or referential integrity

WARNING — raise if:
  1. A dependency is implied but not confirmed (e.g. "send a confirmation"
     — email? SMS? push? which service?)
  2. The story spans frontend + backend but does not call out the API contract
     or data contract needed

SUGGESTION — raise if:
  1. The story would benefit from naming the owning team for a dependency
  2. A dependency is named but the version, SLA, or rate limit is not mentioned

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (null if none)

Return ONLY a JSON array. No markdown. No explanation.
""",

    "COMPLETENESS": """
You are a product owner coach evaluating stories against the INVEST criteria
(Independent, Negotiable, Valuable, Estimable, Small, Testable) and the
standard user story template: As a [role], I want [goal], so that [benefit].

BENCHMARK: A complete story must have:
  1. A clearly named user role (not just "user" — which user type?)
  2. A specific goal/action (not a feature dump)
  3. A stated business value / benefit ("so that...")
  4. Non-functional requirements where applicable:
     - Performance (response time, throughput)
     - Security (auth level required, data sensitivity)
     - Accessibility (WCAG level if UI involved)
     - Scalability / volume assumptions if relevant
  5. Story is small enough to complete in one sprint (INVEST: Small)

ERROR — raise if:
  1. No role defined — cannot tell who the actor is
  2. No business value / "so that" clause present
  3. Story is clearly an epic (describes multiple independent features)
  4. Security-sensitive action (login, payment, personal data) with no mention
     of auth/authorisation requirement

WARNING — raise if:
  1. Role is too generic ("user", "admin") — needs qualification
  2. No performance expectation stated for a user-facing interaction
  3. Story has no sizing signal (too large for one sprint based on described scope)
  4. Accessibility not mentioned for a UI story

SUGGESTION — raise if:
  1. "So that" clause is present but weak (no measurable business outcome)
  2. Could benefit from splitting into smaller stories
  3. Missing data format / validation rules for input fields

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (null if none)

Return ONLY a JSON array. No markdown. No explanation.
""",

    "EDGE_CASES": """
You are a QA architect and security reviewer applying OWASP Top-10,
NFR checklists, and state-machine / session-boundary patterns.

BENCHMARK: A production-ready spec must anticipate failure paths, boundary
conditions, and security edge cases before handing to engineering.

OWASP / SECURITY edge cases to always check:
  - What happens with invalid / malformed input? (OWASP A03 Injection)
  - Is there a rate limit or brute-force protection? (OWASP A07 Auth failures)
  - What if the user submits the form twice rapidly (double-submit)?
  - What if the session expires mid-flow?
  - What if the user is not authenticated / loses permission mid-flow?
  - What if a required downstream service is unavailable (timeout / 503)?
  - Are there maximum length / size limits on input fields?

STATE MACHINE edge cases:
  - What is the starting state and ending state of the entity?
  - What happens if the action is triggered in the wrong state?
    (e.g. clicking "Pay" on an already-paid order)
  - Are concurrent actions possible? (two tabs, two devices)

DATA BOUNDARY edge cases:
  - Empty list / zero results — what does the UI show?
  - Null / missing optional fields — are they handled?
  - Extremely large datasets — pagination? lazy load?
  - Special characters in text fields (Unicode, emoji, SQL chars)?

ERROR — raise if:
  1. No error state / failure path described for a user action
  2. Authentication action with no mention of failed login / lockout
  3. Data write with no mention of validation or constraint

WARNING — raise if:
  1. Happy path is described but at least one likely failure path is missing
  2. No mention of what happens on network timeout
  3. Form submission with no mention of duplicate prevention

SUGGESTION — raise if:
  1. Edge case is low probability but worth documenting
  2. A performance boundary (max items, max file size) is not stated

For each finding return JSON with keys:
  rule, severity, issue, suggestion, conflict_with (null if none)

Return ONLY a JSON array. No markdown. No explanation.
"""
}


OUTPUT_SCHEMA = """
Return a JSON array. Each element must have exactly these keys:
  "rule"         : the rule name passed to you (string)
  "severity"     : "ERROR" | "WARNING" | "SUGGESTION"
  "issue"        : short description of the problem (max 120 chars)
  "suggestion"   : concrete rewrite or fix (max 200 chars)
  "conflict_with": the conflicting text snippet, or null

If no issues are found, return an empty array: []
Do NOT wrap in markdown. Do NOT add explanation outside the JSON array.
"""


class PRDLinter:
    def __init__(self, backend):
        self.backend = backend

    def run(self, rule: str, spec_text: str) -> list[dict]:
        """Run a single rule against spec_text, return list of findings."""
        if rule not in RULE_PROMPTS:
            return []

        system_prompt = RULE_PROMPTS[rule].strip() + "\n\n" + OUTPUT_SCHEMA.strip()

        user_message = f"""Analyse the following product spec for the rule: {rule}

--- SPEC START ---
{spec_text.strip()}
--- SPEC END ---

Remember: return ONLY a valid JSON array of findings. Empty array if none found.
"""

        raw = self.backend.complete(
            system=system_prompt,
            user=user_message
        )

        return self._parse(raw, rule)

    def _parse(self, raw: str, rule: str) -> list[dict]:
        """Extract JSON array from model response robustly."""
        # Strip markdown fences if model wraps in ```json ... ```
        cleaned = re.sub(r"```(?:json)?\s*", "", raw, flags=re.IGNORECASE)
        cleaned = re.sub(r"```", "", cleaned).strip()

        # Find first [ ... ] block
        match = re.search(r"\[.*\]", cleaned, re.DOTALL)
        if not match:
            return []

        try:
            findings = json.loads(match.group())
            # Normalise: ensure each finding has required keys and correct rule
            result = []
            for f in findings:
                if not isinstance(f, dict):
                    continue
                result.append({
                    "rule":         rule,
                    "severity":     str(f.get("severity", "SUGGESTION")).upper(),
                    "issue":        str(f.get("issue", "")),
                    "suggestion":   str(f.get("suggestion", "")),
                    "conflict_with": f.get("conflict_with")
                })
            return result
        except (json.JSONDecodeError, ValueError):
            return []
