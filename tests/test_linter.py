"""
tests/test_linter.py

10 test cases covering different story lengths, complexities, and rule categories.
Run with: pytest tests/test_linter.py -v

Each test validates:
  - Correct rules are triggered
  - Short/garbage input is rejected before LLM call
  - Severity levels are appropriate
  - Findings structure is valid
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from core.linter import PRDLinter, MIN_WORDS

# ── Mock backend (no real LLM needed for structural tests) ────────────────
class MockBackend:
    """Returns configurable JSON responses for deterministic testing."""
    def __init__(self, response_json: str = '{"findings": []}'):
        self.response_json = response_json
        self.calls = []

    def complete(self, system: str, user: str) -> str:
        self.calls.append({"system": system, "user": user})
        return self.response_json

    def set_response(self, json_str: str):
        self.response_json = json_str

# ── Fixtures ──────────────────────────────────────────────────────────────
@pytest.fixture
def clean_backend():
    return MockBackend('{"findings": []}')

@pytest.fixture
def linter(clean_backend):
    return PRDLinter(clean_backend)


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 1 — Garbage input (single word)
# Expectation: rejected before LLM, returns ERROR, LLM never called
# ══════════════════════════════════════════════════════════════════════════
def test_01_single_word_rejected_before_llm(clean_backend):
    linter = PRDLinter(clean_backend)
    result = linter.lint("test", enabled_rules=["COMPLETENESS"])
    assert result["summary"]["ERROR"] == 1
    assert len(clean_backend.calls) == 0, "LLM should NOT be called for trivially short input"
    assert "too short" in result["findings"][0]["issue"].lower()


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 2 — Empty string input
# Expectation: rejected before LLM, returns ERROR
# ══════════════════════════════════════════════════════════════════════════
def test_02_empty_string_rejected(clean_backend):
    linter = PRDLinter(clean_backend)
    result = linter.lint("", enabled_rules=["AMBIGUITY", "MISSING_AC"])
    assert result["summary"]["ERROR"] == 1
    assert len(clean_backend.calls) == 0


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 3 — Exactly at word limit boundary (14 words → reject, 15 → allow)
# ══════════════════════════════════════════════════════════════════════════
def test_03_word_count_boundary(clean_backend):
    linter = PRDLinter(clean_backend)

    fourteen_words = "As a user I want to log in so that I can see my"
    assert len(fourteen_words.split()) == 14
    result_14 = linter.lint(fourteen_words, enabled_rules=["AMBIGUITY"])
    assert result_14["summary"]["ERROR"] == 1
    assert len(clean_backend.calls) == 0

    fifteen_words = "As a user I want to log in so that I can see my dashboard"
    assert len(fifteen_words.split()) == 15
    result_15 = linter.lint(fifteen_words, enabled_rules=["AMBIGUITY"])
    assert len(clean_backend.calls) == 1, "LLM should be called for 15+ word input"


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 4 — Valid minimal story, clean spec (no issues)
# Expectation: LLM called, zero findings returned, summary all zeros
# ══════════════════════════════════════════════════════════════════════════
MINIMAL_CLEAN_STORY = """
As a registered user, I want to reset my password via email
so that I can regain access to my account if I forget it.

Acceptance Criteria:
  Given I am on the login page
  When I click "Forgot Password" and enter my registered email address
  Then I receive a password reset link within 60 seconds
  And the link expires after 24 hours
  And if the email is not registered, I see: "If this email exists, a link has been sent"
"""

def test_04_clean_minimal_story_no_findings(clean_backend):
    linter = PRDLinter(clean_backend)
    result = linter.lint(MINIMAL_CLEAN_STORY, enabled_rules=["AMBIGUITY"])
    assert result["summary"] == {"ERROR": 0, "WARNING": 0, "SUGGESTION": 0}
    assert result["findings"] == []
    assert len(clean_backend.calls) == 1


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 5 — Ambiguous language detection
# Expectation: mock returns an AMBIGUITY finding, correctly parsed
# ══════════════════════════════════════════════════════════════════════════
AMBIGUOUS_STORY = """
As a user I want the app to load fast so that I have a good experience.
The system should be robust and handle errors gracefully.
The dashboard should be intuitive and easy to use for all users.
"""

AMBIGUITY_MOCK_RESPONSE = '''{
  "findings": [
    {
      "severity": "ERROR",
      "rule": "AMBIGUITY",
      "line_hint": "load fast",
      "issue": "'Fast' is unmeasurable. No SLA defined.",
      "suggestion": "The dashboard must load within 2 seconds for 95th percentile users under normal load (< 500 concurrent users).",
      "conflict_with": null
    },
    {
      "severity": "WARNING",
      "rule": "AMBIGUITY",
      "line_hint": "intuitive and easy to use",
      "issue": "'Intuitive' and 'easy to use' are subjective and untestable.",
      "suggestion": "Define measurable usability criteria: e.g. a first-time user can complete the core task within 3 minutes without help.",
      "conflict_with": null
    }
  ]
}'''

def test_05_ambiguity_findings_parsed_correctly():
    backend = MockBackend(AMBIGUITY_MOCK_RESPONSE)
    linter = PRDLinter(backend)
    result = linter.lint(AMBIGUOUS_STORY, enabled_rules=["AMBIGUITY"])
    assert result["summary"]["ERROR"] == 1
    assert result["summary"]["WARNING"] == 1
    assert len(result["findings"]) == 2
    assert result["findings"][0]["rule"] == "AMBIGUITY"
    assert result["findings"][0]["line_hint"] == "load fast"


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 6 — Missing acceptance criteria
# Expectation: MISSING_AC finding with ERROR severity
# ══════════════════════════════════════════════════════════════════════════
NO_AC_STORY = """
As an admin, I want to be able to delete user accounts from the admin panel
so that I can remove inactive or abusive users from the platform.
The admin should also be able to bulk delete multiple users at once.
There should be a confirmation step before deletion.
"""

MISSING_AC_MOCK = '''{
  "findings": [
    {
      "severity": "ERROR",
      "rule": "MISSING_AC",
      "line_hint": "delete user accounts",
      "issue": "No acceptance criteria defined. Missing: success state, failure state, auth check, data cascade, audit log.",
      "suggestion": "Given I am logged in as an admin\\nWhen I click Delete on user ID 123 and confirm\\nThen the user account is soft-deleted\\nAnd I see a success toast: 'User John Doe deleted'\\nAnd an audit log entry is created: { admin_id, user_id, timestamp, action: 'DELETE' }\\nAnd the user cannot log in\\nAnd the user receives a deletion confirmation email",
      "conflict_with": null
    }
  ]
}'''

def test_06_missing_ac_detected():
    backend = MockBackend(MISSING_AC_MOCK)
    linter = PRDLinter(backend)
    result = linter.lint(NO_AC_STORY, enabled_rules=["MISSING_AC"])
    assert result["summary"]["ERROR"] == 1
    assert result["findings"][0]["rule"] == "MISSING_AC"
    assert "Given" in result["findings"][0]["suggestion"]


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 7 — Contradiction detection
# Expectation: CONTRADICTION finding with conflict_with populated
# ══════════════════════════════════════════════════════════════════════════
CONTRADICTORY_STORY = """
As an admin, I want to manage user accounts so I can keep the platform clean.

Business Rules:
- Admins can permanently delete any user account.
- All user data must be retained for 7 years for compliance purposes.
- Deleted users cannot be restored.
- The system must maintain a complete audit trail of all user activity.
"""

CONTRADICTION_MOCK = '''{
  "findings": [
    {
      "severity": "ERROR",
      "rule": "CONTRADICTION",
      "line_hint": "Admins can permanently delete any user account",
      "issue": "Permanent deletion contradicts the 7-year data retention requirement. These two rules cannot coexist without a defined reconciliation strategy.",
      "suggestion": "Resolve by implementing soft delete: mark account as deleted and restrict login, but retain data in cold storage for 7 years to satisfy compliance. Hard delete should only occur after the retention period via an automated purge job.",
      "conflict_with": "All user data must be retained for 7 years for compliance purposes"
    }
  ]
}'''

def test_07_contradiction_conflict_with_populated():
    backend = MockBackend(CONTRADICTION_MOCK)
    linter = PRDLinter(backend)
    result = linter.lint(CONTRADICTORY_STORY, enabled_rules=["CONTRADICTION"])
    assert result["summary"]["ERROR"] == 1
    finding = result["findings"][0]
    assert finding["conflict_with"] is not None
    assert "7 years" in finding["conflict_with"]


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 8 — Dependency gap / blast radius
# Expectation: DEPENDENCY_GAP findings for schema change blast radius
# ══════════════════════════════════════════════════════════════════════════
SCHEMA_CHANGE_STORY = """
As a product manager, I want to add a "preferred_language" field to the user profile
so that we can personalise the UI and email communications based on user preference.

The field should be a dropdown with supported languages: EN, ES, FR, DE.
Default value: EN. The preference should apply immediately across the app.
It should also be used to send transactional emails in the user's language.
"""

DEP_GAP_MOCK = '''{
  "findings": [
    {
      "severity": "ERROR",
      "rule": "DEPENDENCY_GAP",
      "line_hint": "add a preferred_language field to the user profile",
      "issue": "Schema change to the users table. Blast radius unaddressed: Auth Service, Billing Service, and Email Service all read from the users table. No migration strategy defined.",
      "suggestion": "Before development: (1) Auth Service — confirm preferred_language field addition is backward-compatible with current JWT payload. (2) Billing Service — confirm no joins on users schema will break. (3) Email Service (SendGrid) — template variants needed for EN/ES/FR/DE; confirm template IDs and fallback to EN if translation missing. (4) DB migration: ADD COLUMN preferred_language VARCHAR(5) DEFAULT 'EN' NOT NULL — backward compatible, no downtime.",
      "conflict_with": null
    }
  ]
}'''

def test_08_dependency_blast_radius_detected():
    backend = MockBackend(DEP_GAP_MOCK)
    linter = PRDLinter(backend)
    result = linter.lint(SCHEMA_CHANGE_STORY, enabled_rules=["DEPENDENCY_GAP"])
    assert result["summary"]["ERROR"] == 1
    assert "blast radius" in result["findings"][0]["issue"].lower()


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 9 — Large complex story that should be split
# Expectation: COMPLETENESS returns a WARNING with split recommendation
# ══════════════════════════════════════════════════════════════════════════
LARGE_STORY = """
As a marketplace seller, I want to manage my product catalogue so that I can
list, edit, and remove products, upload images, set pricing and inventory,
apply discount codes, view sales analytics, and export reports to CSV.

The system should integrate with our inventory management system (IMS) for
real-time stock sync. When stock hits zero, the product should auto-deactivate.
Sellers should receive email and push notifications for low stock alerts.
The product listing page should load in under 1 second and support bulk operations.
Admins should be able to review and approve new product listings before they go live.
Discount codes should be validated against the promotions service in real time.
"""

SPLIT_MOCK = '''{
  "findings": [
    {
      "severity": "WARNING",
      "rule": "COMPLETENESS",
      "line_hint": "manage my product catalogue",
      "issue": "This story spans 5+ distinct technical layers (FE catalogue UI, BE CRUD, IMS integration, promotions service, notifications) and covers at least 8 independent user outcomes. Estimated at 20+ story points — significantly exceeds one sprint. Should be split using Workflow Steps + Technical Layer patterns.",
      "suggestion": "Recommended split (SAFe Vertical Slicing + SPIDR):\\n\\n📋 Story A — List and View Products [~3 pts]\\nAs a seller, I want to view my product catalogue so that I can see all my listings.\\nDependency: None — can start immediately.\\nTech: FE (catalogue page) + BE (GET /seller/{id}/products)\\nAC: Given I am logged in as a seller, When I navigate to My Products, Then I see a paginated list of my products with title, price, stock, and status.\\n\\n📋 Story B — Create and Edit Products [~5 pts]\\nAs a seller, I want to add and edit product listings so that I can manage my catalogue.\\nDependency: Story A.\\nTech: FE (product form) + BE (POST/PUT /products) + image upload (S3)\\n\\n📋 Story C — IMS Stock Sync [~5 pts]\\nAs a seller, I want my stock levels to sync with the IMS in real time so that overselling is prevented.\\nDependency: Story B (product IDs must exist).\\nTech: BE integration (IMS webhook) + auto-deactivation logic\\n\\n📋 Story D — Low Stock Notifications [~2 pts]\\nAs a seller, I want to receive alerts when stock is low so that I can reorder in time.\\nDependency: Story C (stock sync must be live).\\nTech: BE event trigger + Notification Service (email + push)\\n\\n📋 Story E — Discount Code Validation [~3 pts]\\nAs a seller, I want to apply discount codes to products so that I can run promotions.\\nDependency: None (parallel to B).\\nTech: FE (discount field) + BE (Promotions Service API integration)\\n\\n📋 Story F — Sales Analytics and CSV Export [~3 pts]\\nAs a seller, I want to view sales analytics and export to CSV so that I can track performance.\\nDependency: Story B (orders data must exist).\\nTech: FE (dashboard) + BE (analytics aggregation + CSV generation)",
      "conflict_with": null
    }
  ]
}'''

def test_09_large_story_split_recommended():
    backend = MockBackend(SPLIT_MOCK)
    linter = PRDLinter(backend)
    result = linter.lint(LARGE_STORY, enabled_rules=["COMPLETENESS"])
    assert result["summary"]["WARNING"] == 1
    suggestion = result["findings"][0]["suggestion"]
    assert "Story A" in suggestion
    assert "Story B" in suggestion
    assert "Dependency:" in suggestion


# ══════════════════════════════════════════════════════════════════════════
# TEST CASE 10 — Multi-rule run on a realistic but flawed story
# Expectation: multiple rules fire, summary counts are accurate
# ══════════════════════════════════════════════════════════════════════════
REALISTIC_FLAWED_STORY = """
As a customer, I want to checkout quickly so I can complete my purchase easily.
The checkout should support credit cards and PayPal.
After payment the order should be confirmed and the user notified.
Admins can refund orders from the admin panel.
"""

def test_10_multi_rule_summary_counts_accurate():
    # Each rule returns one finding of a different severity
    call_count = [0]
    responses = [
        '{"findings": [{"severity": "ERROR", "rule": "AMBIGUITY", "line_hint": "checkout quickly", "issue": "Vague.", "suggestion": "Checkout must complete within 3s.", "conflict_with": null}]}',
        '{"findings": [{"severity": "WARNING", "rule": "MISSING_AC", "line_hint": "order confirmed", "issue": "No AC for payment failure.", "suggestion": "Given payment fails, When user submits, Then error shown inline.", "conflict_with": null}]}',
        '{"findings": []}',
        '{"findings": [{"severity": "ERROR", "rule": "DEPENDENCY_GAP", "line_hint": "PayPal", "issue": "PayPal integration contract undefined.", "suggestion": "Specify PayPal SDK version, sandbox credentials, and IPN webhook URL.", "conflict_with": null}]}',
        '{"findings": [{"severity": "SUGGESTION", "rule": "COMPLETENESS", "line_hint": "refund orders", "issue": "No refund SLA or partial refund flow defined.", "suggestion": "Define: full vs partial refund, processing time SLA (3-5 business days), notification to customer.", "conflict_with": null}]}',
    ]

    class SequentialMockBackend:
        def __init__(self):
            self.idx = 0
        def complete(self, system, user):
            r = responses[self.idx % len(responses)]
            self.idx += 1
            return r

    linter = PRDLinter(SequentialMockBackend())
    result = linter.lint(
        REALISTIC_FLAWED_STORY,
        enabled_rules=["AMBIGUITY", "MISSING_AC", "CONTRADICTION", "DEPENDENCY_GAP", "COMPLETENESS"]
    )

    assert result["summary"]["ERROR"] == 2
    assert result["summary"]["WARNING"] == 1
    assert result["summary"]["SUGGESTION"] == 1
    assert len(result["findings"]) == 4
    # Verify rule tags are correctly assigned
    rules_found = {f["rule"] for f in result["findings"]}
    assert "AMBIGUITY" in rules_found
    assert "MISSING_AC" in rules_found
    assert "DEPENDENCY_GAP" in rules_found
    assert "COMPLETENESS" in rules_found
