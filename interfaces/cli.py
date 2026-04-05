#!/usr/bin/env python3
"""
prd-linter CLI
Usage: python -m interfaces.cli path/to/spec.md [options]
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backends import get_backend
from core.linter import PRDLinter
from core.report import render_report, render_json


def main():
    parser = argparse.ArgumentParser(
        description="PRD Linter — catch ambiguity, missing ACs, and contradictions before dev handoff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m interfaces.cli spec.md
  python -m interfaces.cli spec.md --backend ollama --model llama3
  python -m interfaces.cli spec.md --backend openai
  python -m interfaces.cli spec.md --rules AMBIGUITY CONTRADICTION
  python -m interfaces.cli spec.md --output json > report.json
        """
    )
    parser.add_argument("file", help="Path to PRD file (.md, .txt)")
    parser.add_argument("--backend", default="ollama",
                        choices=["ollama", "openrouter", "openai", "anthropic"],
                        help="LLM backend (default: ollama — fully local)")
    parser.add_argument("--model", default=None,
                        help="Model name (default: mistral for ollama, gpt-4o for openai)")
    parser.add_argument("--rules", nargs="+",
                        choices=["AMBIGUITY", "MISSING_AC", "CONTRADICTION",
                                 "DEPENDENCY_GAP", "COMPLETENESS"],
                        help="Run specific rules only")
    parser.add_argument("--output", default="text", choices=["text", "json"],
                        help="Output format (default: text)")
    parser.add_argument("--host", default="http://localhost:11434",
                        help="Ollama host (default: http://localhost:11434)")

    args = parser.parse_args()

    # Read PRD
    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    with open(args.file, "r", encoding="utf-8") as f:
        text = f.read()

    if len(text.strip()) < 50:
        print("❌ File appears empty or too short to lint.")
        sys.exit(1)

    # Build backend
    kwargs = {}
    if args.model:
        kwargs["model"] = args.model
    if args.backend == "ollama":
        kwargs["host"] = args.host

    print(f"\n⏳ Running PRD Linter ({args.backend})...")
    backend = get_backend(args.backend, **kwargs)
    linter = PRDLinter(backend)

    report = linter.lint(text, enabled_rules=args.rules)
    prd_name = os.path.basename(args.file)

    if args.output == "json":
        print(render_json(report))
    else:
        print(render_report(report, prd_name))

    # Exit code: 1 if errors found (useful for CI pipelines)
    sys.exit(1 if report["summary"]["ERROR"] > 0 else 0)


if __name__ == "__main__":
    main()
