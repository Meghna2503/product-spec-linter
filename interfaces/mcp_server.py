#!/usr/bin/env python3
"""
PRD Linter — MCP Server
Exposes the linter as a Model Context Protocol tool for Claude Code Enterprise.

Setup:
  pip install mcp
  python interfaces/mcp_server.py

Claude Code config (~/.claude/config.json):
  {
    "mcpServers": {
      "prd-linter": {
        "command": "python",
        "args": ["/path/to/prd-linter/interfaces/mcp_server.py"],
        "env": { "PRD_LINTER_BACKEND": "ollama" }
      }
    }
  }

Usage in Claude Code:
  /prd-lint path/to/spec.md
  /prd-lint path/to/spec.md --rules CONTRADICTION MISSING_AC
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("Install MCP SDK: pip install mcp")
    sys.exit(1)

from backends import get_backend
from core.linter import PRDLinter
from core.report import render_report

app = Server("prd-linter")
BACKEND_TYPE = os.environ.get("PRD_LINTER_BACKEND", "ollama")


@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="prd_lint",
            description=(
                "Lint a Product Requirements Document (PRD) for ambiguity, "
                "missing acceptance criteria, contradictions, dependency gaps, "
                "and completeness issues. Runs locally via Ollama by default."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the PRD file (.md or .txt)"
                    },
                    "rules": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": ["AMBIGUITY", "MISSING_AC", "CONTRADICTION",
                                     "DEPENDENCY_GAP", "COMPLETENESS"]
                        },
                        "description": "Specific rules to run (default: all)"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "prd_lint":
        raise ValueError(f"Unknown tool: {name}")

    file_path = arguments["file_path"]
    rules = arguments.get("rules", None)

    if not os.path.exists(file_path):
        return [types.TextContent(type="text", text=f"❌ File not found: {file_path}")]

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    backend = get_backend(BACKEND_TYPE)
    linter = PRDLinter(backend)
    report = linter.lint(text, enabled_rules=rules)

    output = render_report(report, os.path.basename(file_path))
    return [types.TextContent(type="text", text=output)]


async def main():
    async with stdio_server() as streams:
        await app.run(streams[0], streams[1], app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
