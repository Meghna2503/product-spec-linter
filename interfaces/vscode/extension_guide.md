# VS Code Extension — Setup Guide

The VS Code extension is a thin wrapper that calls the Product Spec Linter CLI
and displays results in the VS Code Problems panel and as inline diagnostics.

## Scaffold (run once)

```bash
npm install -g @vscode/generator-code yo
yo code
# Choose: New Extension (TypeScript)
# Name: product-spec-linter
# Identifier: product-spec-linter
```

## Key extension.ts Logic

```typescript
import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
  const diagnosticCollection = vscode.languages.createDiagnosticCollection('prd-linter');

  const lintCommand = vscode.commands.registerCommand('productSpecLinter.lint', () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const filePath = editor.document.uri.fsPath;
    const backend = vscode.workspace.getConfiguration('productSpecLinter').get('backend', 'ollama');

    vscode.window.withProgress({
      location: vscode.ProgressLocation.Notification,
      title: "Product Spec Linter running...",
      cancellable: false
    }, () => new Promise<void>((resolve) => {
      exec(
        `python -m interfaces.cli "${filePath}" --output json --backend ${backend}`,
        { cwd: context.extensionPath },
        (error, stdout) => {
          try {
            const report = JSON.parse(stdout);
            const diagnostics = report.findings.map((f: any) => {
              const severity = f.severity === 'ERROR'
                ? vscode.DiagnosticSeverity.Error
                : f.severity === 'WARNING'
                ? vscode.DiagnosticSeverity.Warning
                : vscode.DiagnosticSeverity.Information;

              // Find line number by searching for the hint text
              const lines = editor.document.getText().split('\n');
              const lineIndex = lines.findIndex(l =>
                l.toLowerCase().includes(f.line_hint?.toLowerCase()?.substring(0, 20) || '')
              );
              const range = new vscode.Range(
                Math.max(0, lineIndex), 0,
                Math.max(0, lineIndex), 200
              );
              const diag = new vscode.Diagnostic(range, `[${f.rule}] ${f.issue}`, severity);
              diag.source = 'Product Spec Linter';
              diag.code = f.rule;
              return diag;
            });

            diagnosticCollection.set(editor.document.uri, diagnostics);
            vscode.window.showInformationMessage(
              `Lint complete: ${report.summary.ERROR} errors, ${report.summary.WARNING} warnings`
            );
          } catch {
            vscode.window.showErrorMessage('Linter failed. Is Ollama running?');
          }
          resolve();
        }
      );
    }));
  });

  context.subscriptions.push(lintCommand, diagnosticCollection);
}
```

## package.json additions

```json
{
  "contributes": {
    "commands": [{
      "command": "productSpecLinter.lint",
      "title": "Product Spec Linter: Lint this PRD"
    }],
    "configuration": {
      "title": "Product Spec Linter",
      "properties": {
        "productSpecLinter.backend": {
          "type": "string",
          "default": "ollama",
          "enum": ["ollama", "openai", "anthropic"],
          "description": "LLM backend. Use 'ollama' for maximum privacy (local, no data sent externally)."
        }
      }
    },
    "keybindings": [{
      "command": "productSpecLinter.lint",
      "key": "ctrl+shift+l",
      "mac": "cmd+shift+l",
      "when": "editorTextFocus"
    }]
  }
}
```

## Usage

1. Open any `.md` spec file in VS Code
2. Press `Cmd+Shift+L` (Mac) or `Ctrl+Shift+L` (Windows/Linux)
3. Issues appear as red/yellow squiggles + in the Problems panel
