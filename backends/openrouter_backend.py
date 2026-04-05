import os
import urllib.request
import urllib.error
import json


SUPPORTED_MODELS = """
Popular models on OpenRouter for PRD linting:
  moonshotai/kimi-k2.5              — Best reasoning, huge context (recommended for tuning)
  anthropic/claude-sonnet-4-5       — Strong instruction following
  openai/gpt-4o                     — Reliable, well-rounded
  meta-llama/llama-3.1-70b-instruct — Open source, strong quality
  mistralai/mistral-large            — Mistral at full scale
  google/gemini-2.0-flash            — Fast, good for large docs
"""


CLOUD_WARNING = """
╔══════════════════════════════════════════════════════════════╗
║  ⚠️  PRIVACY WARNING — OpenRouter Cloud Backend              ║
║  Your PRD content will be sent to OpenRouter's servers       ║
║  and routed to the selected model provider.                  ║
║  For sensitive product requirements, use: --backend ollama   ║
║  See SECURITY.md for details.                                ║
╚══════════════════════════════════════════════════════════════╝
"""


class OpenRouterBackend:
    """
    Access 100+ models (Kimi K2.5, Claude, GPT-4o, Llama, Gemini)
    through a single OpenRouter API key.

    Usage:
        python -m interfaces.cli spec.md --backend openrouter
        python -m interfaces.cli spec.md --backend openrouter --model moonshotai/kimi-k2.5
    """

    def __init__(
        self,
        model: str = "moonshotai/kimi-k2.5",
        api_key: str = None,
        site_url: str = "https://github.com/yourusername/product-spec-linter",
        site_name: str = "Product Spec Linter"
    ):
        print(CLOUD_WARNING)
        print(f"  Model: {model}")
        print(f"\n{SUPPORTED_MODELS}")

        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.site_url = site_url
        self.site_name = site_name

        if not self.api_key:
            raise ValueError(
                "OpenRouter API key required.\n"
                "Set it with: export OPENROUTER_API_KEY=your_key\n"
                "Get a key at: https://openrouter.ai/keys"
            )

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            "temperature": 0.1
        }).encode()

        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/chat/completions",
            data=payload,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": self.site_url,
                "X-Title": self.site_name
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read())
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            raise ConnectionError(
                f"OpenRouter API error {e.code}: {e.reason}. "
                f"Check your API key and model name '{self.model}'."
            ) from e
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Cannot reach OpenRouter. Check your internet connection.\nDetail: {e}"
            ) from e
        except KeyError as e:
            raise ValueError(
                f"Unexpected response format from OpenRouter. "
                f"Model '{self.model}' may not be available."
            ) from e