# Security Guarantees

Product Spec Linter is built privacy-first. Your product specs contain your company's
roadmap, unreleased features, and competitive strategy. They should never leave your machine.

## Default Mode (Ollama — Fully Local)

✅ 100% local inference via Ollama  
✅ No API keys required  
✅ No network calls during analysis  
✅ No telemetry or usage tracking  
✅ Spec content never written to disk beyond your own filesystem  
✅ Full source code auditable — no obfuscated dependencies  
✅ Works fully offline after one-time model download  

**Your product specs never leave your machine.**

## Cloud Backends (OpenAI / Anthropic)

⚠️ When using `--backend openai` or `--backend anthropic`:
- Your spec content is sent to the provider's servers
- Subject to the provider's data retention and privacy policies
- Suitable for personal projects or non-confidential specs only
- The tool prints an explicit warning before every run

## Claude Code Enterprise

When running via MCP against Claude Code Enterprise:
- Data handling is governed by your enterprise agreement with Anthropic
- Verify your Data Processing Agreement (DPA) covers this use case
- For maximum privacy, set `PRD_LINTER_BACKEND=ollama` in MCP config

## Verifying No Network Calls (Ollama Mode)

You can verify zero outbound traffic yourself:
```bash
# macOS
sudo lsof -i -n -P | grep python

# Linux
ss -tp | grep python
```
Run this while the linter is processing — you'll see only localhost:11434 (Ollama).

## OpenRouter Backend

⚠️ When using `--backend openrouter`:
- Your spec content is sent to OpenRouter's servers, then routed to the selected model provider
- OpenRouter's privacy policy applies: https://openrouter.ai/privacy
- Suitable for personal projects or when using non-confidential specs
- Recommended model for best linting quality: `moonshotai/kimi-k2.5`
- The tool prints an explicit warning before every run

**Use OpenRouter during development/prompt tuning. Switch to Ollama for production/sensitive specs.**
