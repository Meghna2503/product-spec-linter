def get_backend(backend_type: str, **kwargs):
    if backend_type == "ollama":
        from .ollama import OllamaBackend
        return OllamaBackend(**kwargs)
    elif backend_type == "openai":
        from .openai_backend import OpenAIBackend
        return OpenAIBackend(**kwargs)
    elif backend_type == "anthropic":
        from .anthropic_backend import AnthropicBackend
        return AnthropicBackend(**kwargs)
    elif backend_type == "openrouter":
        from .openrouter_backend import OpenRouterBackend
        return OpenRouterBackend(**kwargs)
    else:
        raise ValueError(
            f"Unknown backend: '{backend_type}'.\n"
            f"Choose from: ollama, openrouter, openai, anthropic\n\n"
            f"  ollama      — 100% local, zero data leaves machine (default)\n"
            f"  openrouter  — 100+ models via one API key (Kimi K2.5, Claude, GPT-4o...)\n"
            f"  openai      — OpenAI API directly\n"
            f"  anthropic   — Anthropic API directly"
        )
