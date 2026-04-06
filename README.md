# Product Spec Linter

> Catch ambiguity, missing acceptance criteria, and contradictions in your PRDs — before they reach your dev team.

Built by a Product Owner who got tired of specs that made sense when written and caused confusion in sprint planning.
<img width="959" height="436" alt="image" src="https://github.com/user-attachments/assets/38b64759-79f4-45f1-a737-09840720f0bd" />

---

## The Problem

Bad specs are expensive. A vague acceptance criterion, a contradiction between two stories, an undefined integration — each one costs hours of dev rework, misaligned deliverables, or a sprint review conversation nobody wants to have.

Most teams catch these issues *after* handoff. This tool catches them *before*.

---

## What It Checks

| Rule | Severity | What It Catches |
|---|---|---|
| **Ambiguity** | ⚠️ Warning | Vague language: "fast", "seamless", "major browsers", "popular payment methods" |
| **Missing AC** | 🔴 Error | User stories with no testable acceptance criteria |
| **Contradiction** | 🔴 Error | Conflicting requirements anywhere in the document |
| **Dependency Gap** | ⚠️ Warning | Undefined integrations, unspecced APIs, assumed data sources |
| **Completeness** | ⚪ Suggestion | Missing NFRs, rollback plan, error states, out-of-scope definition |

<img width="707" height="439" alt="image" src="https://github.com/user-attachments/assets/0aa1a4dd-e9ce-4dbd-810f-0daaa55bb06f" />

---

## Privacy First

**Your specs contain your roadmap. They should never leave your machine.**

| Backend | Data goes to | Use when |
|---|---|---|
| **Ollama (default)** | Nowhere — 100% local | Always. Especially for sensitive specs. |
| **OpenRouter** | OpenRouter → model provider | Dev/tuning. Access Kimi K2.5, Claude, GPT-4o via one API key |
| **Anthropic Enterprise** | Anthropic (covered by your DPA) | Your team uses Claude Code Enterprise |
| **OpenAI / Anthropic cloud** | Provider servers | Personal projects only |

See [SECURITY.md](SECURITY.md) for full details and network verification instructions.

---

## Install

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) (for local mode)

```bash
# 1. Clone
git clone https://github.com/yourusername/product-spec-linter
cd product-spec-linter

# 2. Pull a model (one-time, ~4GB)
ollama pull mistral

# 3. Run
python -m interfaces.cli examples/sample_prd.md
```

---

## Usage

```bash
# Lint a spec (local Ollama — default)
python -m interfaces.cli path/to/spec.md

# Run specific rules only
python -m interfaces.cli spec.md --rules CONTRADICTION MISSING_AC

# JSON output (pipe to other tools)
python -m interfaces.cli spec.md --output json > report.json

# Use a stronger local model
python -m interfaces.cli spec.md --model llama3

# Cloud backend (prints privacy warning)
python -m interfaces.cli spec.md --backend openai
```

### CI/CD Integration

The CLI exits with code `1` if errors are found, `0` if clean.

```yaml
# .github/workflows/spec-lint.yml
- name: Lint PRD
  run: python -m interfaces.cli docs/spec.md --backend openai
```

---

## Claude Code Enterprise (MCP)

Add to `~/.claude/config.json`:

```json
{
  "mcpServers": {
    "product-spec-linter": {
      "command": "python",
      "args": ["/path/to/product-spec-linter/interfaces/mcp_server.py"],
      "env": { "PRD_LINTER_BACKEND": "ollama" }
    }
  }
}
```

Then inside Claude Code:
```
/prd-lint path/to/checkout-redesign.md
```

---

## Example Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PRD Lint Report — checkout-redesign-v2.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🔴 ERRORS       2
  🟡 WARNINGS     4
  ⚪ SUGGESTIONS  3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

── 🔴 ERRORS ──────────────────────────────────────────

  [Contradiction]
  ❝ "Guest checkout is available for all users"
  ↔ conflicts with: "Users must be logged in before placing an order"
  Issue: These two requirements are mutually exclusive
  Fix:   Define which takes precedence or clarify scope per user segment

  [Missing Acceptance Criteria]
  ❝ "The system should process payments quickly"
  Issue: No testable criterion for payment processing time
  Fix:   Add: "Payment confirmation returned within 3 seconds at P95"
```

---

## Project Structure

```
product-spec-linter/
├── core/
│   ├── linter.py          # Orchestrates rules, parses LLM output
│   ├── report.py          # Formats lint report (text + JSON)
│   └── rules/             # One file per rule — easy to extend
├── backends/
│   ├── ollama.py          # Local (default)
│   ├── openai_backend.py  # Cloud (with privacy warning)
│   └── anthropic_backend.py
├── interfaces/
│   ├── cli.py             # Terminal + CI/CD
│   └── mcp_server.py      # Claude Code Enterprise
├── examples/
│   └── sample_prd.md      # Demo spec with intentional issues
├── SECURITY.md
└── README.md
```

---

## Roadmap

- [ ] VS Code extension with inline highlights
- [ ] Ecommerce-specific rule set (checkout flows, PDP requirements)
- [ ] HTML report export
- [ ] Pre-commit hook
- [ ] Rule severity configuration per team

---

## Contributing

PRs welcome. If you're a PO who writes specs, your domain knowledge is more valuable here than raw coding skill — especially for improving the rule prompts.

---

## License

MIT — use it, modify it, ship it.

---

*Built by a PO. For POs.*
