import os


CLOUD_WARNING = """
╔══════════════════════════════════════════════════════════╗
║  ⚠️  PRIVACY WARNING                                      ║
║  You are using the Anthropic cloud backend.              ║
║  Your PRD content will be sent to Anthropic's servers.   ║
║  Enterprise users: verify your DPA covers this use case. ║
║  For maximum privacy, use Ollama instead.                ║
╚══════════════════════════════════════════════════════════╝
"""


class AnthropicBackend:
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str = None):
        try:
            import anthropic
        except ImportError:
            raise ImportError("Run: pip install anthropic")

        print(CLOUD_WARNING)
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.model = model

    def complete(self, system: str, user: str) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}]
        )
        return msg.content[0].text