from typing import Dict, Any

ICONS = {
    "ERROR":      "🔴",
    "WARNING":    "🟡",
    "SUGGESTION": "⚪",
    "META":       "⚙️",
}

RULE_LABELS = {
    "AMBIGUITY":      "Ambiguous Language",
    "MISSING_AC":     "Missing Acceptance Criteria",
    "CONTRADICTION":  "Contradiction",
    "DEPENDENCY_GAP": "Dependency Gap",
    "COMPLETENESS":   "Completeness",
    "META":           "Tool Warning",
}


def render_report(report: Dict[str, Any], prd_name: str = "PRD") -> str:
    lines = []
    s = report["summary"]

    lines.append(f"\n{'━'*55}")
    lines.append(f"  PRD Lint Report — {prd_name}")
    lines.append(f"{'━'*55}")
    lines.append(f"  🔴 ERRORS      {s['ERROR']}")
    lines.append(f"  🟡 WARNINGS    {s['WARNING']}")
    lines.append(f"  ⚪ SUGGESTIONS {s['SUGGESTION']}")
    lines.append(f"{'━'*55}\n")

    if report["total"] == 0:
        lines.append("  ✅ No issues found. Clean spec!")
        return "\n".join(lines)

    current_sev = None
    for f in report["findings"]:
        sev = f.get("severity", "META")
        if sev != current_sev:
            current_sev = sev
            lines.append(f"\n{'─'*55}")
            lines.append(f"  {ICONS.get(sev, '?')} {sev}S")
            lines.append(f"{'─'*55}")

        rule_label = RULE_LABELS.get(f.get("rule", ""), f.get("rule", ""))
        lines.append(f"\n  [{rule_label}]")
        lines.append(f"  ❝ {f.get('line_hint', '')}")

        if f.get("conflict_with"):
            lines.append(f"  ↔ conflicts with: {f['conflict_with']}")

        lines.append(f"  Issue: {f.get('issue', '')}")
        lines.append(f"  Fix:   {f.get('suggestion', '')}")

    lines.append(f"\n{'━'*55}\n")
    return "\n".join(lines)


def render_json(report: Dict[str, Any]) -> str:
    import json
    return json.dumps(report, indent=2)
