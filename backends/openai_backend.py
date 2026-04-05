import os


CLOUD_WARNING = """
╔══════════════════════════════════════════════════════╗
║  ⚠️  PRIVACY WARNING                                  ║
║  You are using the OpenAI cloud backend.             ║
║  Your PRD content will be sent to OpenAI's servers.  ║
║  For sensitive product requirements, use Ollama.     ║
║  See SECURITY.md for details.                        ║
╚══════════════════════════════════════════════════════╝
"""


class OpenAIBackend:
    def __init__(self, model: str = "gpt-4o", api_key: str = None):
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Run: pip install openai")

        print(CLOUD_WARNING)
        self.client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self.model = model

    def complete(self, system: str, user: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            temperature=0.1
        )
        return resp.choices[0].message.content