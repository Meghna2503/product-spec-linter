# Contributing to Product Spec Linter

Thanks for your interest in contributing! This project was built by a Product Owner for Product Owners, and your domain knowledge is just as valuable as code contributions.

## Ways to Contribute

### 1. Improve Rule Prompts
The prompts in `core/linter.py` are the heart of this tool. If you find:
- False positives (flagging good specs)
- False negatives (missing bad specs)
- Unclear suggestions

Open an issue with:
- The spec text that triggered the issue
- What the tool reported
- What it should have reported

### 2. Add New Rules
New rules should:
- Address a real spec-writing problem you've encountered
- Include clear severity guidance (ERROR/WARNING/SUGGESTION)
- Have test cases in `tests/test_linter.py`

### 3. Bug Fixes & Features
Check the [GitHub Issues](../../issues) for tagged items:
- `good-first-issue` — easy starting points
- `help-wanted` — needs community input
- `bug` — confirmed issues

## Development Setup

```bash
# 1. Clone
git clone https://github.com/yourusername/product-spec-linter
cd product-spec-linter

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install in editable mode with dev dependencies
pip install -e ".[dev]"

# 4. Run tests
pytest tests/ -v
```

## Pull Request Process

1. Fork the repo and create a branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Add/update tests as needed
4. Ensure tests pass: `pytest tests/ -v`
5. Submit a PR with a clear description

## Code Style

- Follow PEP 8
- Use descriptive variable names
- Add docstrings for public functions
- Keep rule prompts clear and actionable

## Questions?

Open a [GitHub Discussion](../../discussions) or reach out in issues.

---

*Built by POs, for POs.*
