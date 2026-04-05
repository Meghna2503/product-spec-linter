import urllib.request
import urllib.error
import json


class OllamaBackend:
    """100% local. Zero data leaves your machine."""

    def __init__(self, model: str = "mistral", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def complete(self, system: str, user: str) -> str:
        payload = json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user",   "content": user}
            ],
            "stream": False,
            "options": {
                "temperature": 0.1
            }
        }).encode()

        req = urllib.request.Request(
            f"{self.host}/api/chat",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=600) as resp:
                return json.loads(resp.read())["message"]["content"]
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"Cannot reach Ollama at {self.host}. "
                f"Is it running? Try: ollama serve\nDetail: {e}"
            ) from e
        except KeyError as e:
            raise ValueError(
                f"Unexpected response format from Ollama. "
                f"Check model '{self.model}' is pulled: ollama pull {self.model}"
            ) from e