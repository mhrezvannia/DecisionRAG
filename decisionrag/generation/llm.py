from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import httpx

from core.config import LLMConfig


try:  # pragma: no cover - import guard
    from openai import OpenAI
except ImportError:  # pragma: no cover - import guard
    OpenAI = None


@dataclass
class LLMResponse:
    text: str
    mode: str


ProviderName = Literal["openai", "gemini", "llama"]


@dataclass(frozen=True)
class LLMRuntimeConfig:
    provider: ProviderName
    api_key: str | None
    base_url: str | None
    model_name: str


@dataclass(frozen=True)
class ConnectionTestResult:
    success: bool
    message: str


class MultiProviderLLM:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self._clients: dict[tuple[str, str | None, str | None], OpenAI] = {}

    def resolve_runtime(
        self,
        *,
        provider_name: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> LLMRuntimeConfig:
        provider = (provider_name or self.config.default_provider or "openai").lower()
        if provider not in {"openai", "gemini", "llama"}:
            provider = "openai"
        defaults = getattr(self.config, provider)
        resolved_key = api_key if api_key is not None else defaults.api_key
        resolved_base_url = base_url if base_url is not None else defaults.base_url
        resolved_model = model_name or defaults.model_name
        if provider == "llama" and not resolved_key:
            resolved_key = "ollama"
        return LLMRuntimeConfig(
            provider=provider,  # type: ignore[arg-type]
            api_key=resolved_key,
            base_url=resolved_base_url,
            model_name=resolved_model,
        )

    def is_available(self, runtime: LLMRuntimeConfig) -> bool:
        if OpenAI is None or not runtime.model_name:
            return False
        if runtime.provider in {"openai", "gemini"}:
            return bool(runtime.api_key)
        return bool(runtime.base_url)

    @staticmethod
    def infer_provider_from_key(api_key: str) -> ProviderName | None:
        normalized = api_key.strip()
        if not normalized:
            return None
        if normalized.startswith("sk-"):
            return "openai"
        if normalized.startswith("AIza") or normalized.startswith("AQ"):
            return "gemini"
        return None

    @staticmethod
    def validate_api_key_format(
        provider_name: str,
        api_key: str,
    ) -> tuple[bool, str]:
        normalized = api_key.strip()
        if provider_name == "llama":
            return True, "Llama-compatible mode can work without an API key if the endpoint allows it."
        if not normalized:
            return False, "Enter an API key or leave the provider in fallback mode."
        if len(normalized) < 12:
            return False, "The entered key looks too short. Please check the copied value and try again."
        return True, "Key captured. Use the connection test to confirm whether the provider accepts it."

    def _client_for(self, runtime: LLMRuntimeConfig):
        if not self.is_available(runtime):
            return None
        cache_key = (runtime.provider, runtime.base_url, runtime.api_key)
        if cache_key not in self._clients:
            self._clients[cache_key] = OpenAI(
                api_key=runtime.api_key,
                base_url=runtime.base_url or None,
            )
        return self._clients[cache_key]

    @staticmethod
    def _normalize_base_url(base_url: str | None) -> str:
        return (base_url or "").rstrip("/")

    def _gemini_chat_completion(
        self,
        *,
        runtime: LLMRuntimeConfig,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        base_url = self._normalize_base_url(runtime.base_url)
        if not base_url:
            raise ValueError("Gemini base URL is missing.")
        response = httpx.post(
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {runtime.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": runtime.model_name,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                **({"max_tokens": max_tokens} if max_tokens is not None else {}),
            },
            timeout=30.0,
        )
        if response.is_success:
            payload = response.json()
            text = payload["choices"][0]["message"]["content"]
            return LLMResponse(text=text.strip(), mode=runtime.provider)

        error_text = self._extract_error_message(response)
        raise RuntimeError(error_text)

    @staticmethod
    def _extract_error_message(response: httpx.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    return str(error.get("message") or response.text).strip()
                if "message" in payload:
                    return str(payload["message"]).strip()
            if isinstance(payload, list) and payload and isinstance(payload[0], dict):
                error = payload[0].get("error")
                if isinstance(error, dict):
                    return str(error.get("message") or response.text).strip()
        except Exception:
            pass
        return response.text.strip() or f"HTTP {response.status_code}"

    def test_connection(self, runtime: LLMRuntimeConfig) -> ConnectionTestResult:
        if not self.is_available(runtime):
            if runtime.provider in {"openai", "gemini"} and not runtime.api_key:
                return ConnectionTestResult(
                    success=False,
                    message="Missing API key for the selected provider.",
                )
            return ConnectionTestResult(
                success=False,
                    message="Missing model or base URL for the selected provider.",
                )

        if runtime.provider == "gemini":
            try:
                self._gemini_chat_completion(
                    runtime=runtime,
                    system_prompt="Reply with OK.",
                    user_prompt="Ping",
                    max_tokens=1,
                )
                return ConnectionTestResult(
                    success=True,
                    message="Gemini connection successful.",
                )
            except Exception as exc:
                error_text = str(exc).strip().splitlines()[0]
                lowered = error_text.lower()
                if any(token in lowered for token in ("401", "403", "unauthorized", "invalid api key", "permission denied", "api key not valid")):
                    error_text = "Invalid API key. Please check and try again."
                return ConnectionTestResult(
                    success=False,
                    message=error_text or "Connection test failed.",
                )

        client = self._client_for(runtime)
        if client is None:
            return ConnectionTestResult(
                success=False,
                message="Could not initialize the selected provider client.",
            )

        try:
            client.models.list()
            return ConnectionTestResult(
                success=True,
                message=f"{runtime.provider.title()} connection successful.",
            )
        except Exception as first_exc:
            try:
                client.chat.completions.create(
                    model=runtime.model_name,
                    temperature=0.0,
                    max_tokens=1,
                    messages=[
                        {"role": "system", "content": "Reply with the word OK."},
                        {"role": "user", "content": "Ping"},
                    ],
                )
                return ConnectionTestResult(
                    success=True,
                    message=f"{runtime.provider.title()} connection successful.",
                )
            except Exception as second_exc:
                error_text = str(second_exc or first_exc).strip().splitlines()[0]
                lowered = error_text.lower()
                if any(token in lowered for token in ("401", "403", "unauthorized", "invalid api key", "permission denied", "api key not valid")):
                    error_text = "Invalid API key. Please check and try again."
                return ConnectionTestResult(
                    success=False,
                    message=error_text or "Connection test failed.",
                )

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        provider_name: str | None = None,
        model_name: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> LLMResponse | None:
        runtime = self.resolve_runtime(
            provider_name=provider_name,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url,
        )
        if runtime.provider == "gemini":
            try:
                return self._gemini_chat_completion(
                    runtime=runtime,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                )
            except Exception:
                return None
        client = self._client_for(runtime)
        if client is None:
            return None
        try:
            response = client.chat.completions.create(
                model=runtime.model_name,
                temperature=self.config.temperature,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            text = response.choices[0].message.content or ""
            return LLMResponse(text=text.strip(), mode=runtime.provider)
        except Exception:
            return None
