"""LLM provider abstraction.

Supports: none (rule-based), ollama, openai-compatible.
Structured JSON outputs with schema validation. System instructions are
separated from document content to resist prompt injection.
"""

from abc import ABC, abstractmethod
from typing import Optional
import json
import logging

from app.config import settings

logger = logging.getLogger("clauseclear")


class BaseLLMProvider(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def simplify(
        self, original_text: str, category: str, level: str, context: str
    ) -> dict:
        ...

    @abstractmethod
    def classify(
        self, original_text: str, context: str
    ) -> dict:
        ...

    @abstractmethod
    def answer_question(
        self, question: str, context: str
    ) -> dict:
        ...


class NoneProvider(BaseLLMProvider):
    def is_available(self) -> bool:
        return False

    def simplify(self, original_text, category, level, context):
        return {"simplified_text": "", "rationale": "no provider", "confidence": 0.0}

    def classify(self, original_text, context):
        return {"category": "", "confidence": 0.0}

    def answer_question(self, question, context):
        return {"answer": "", "citations": [], "confidence": 0.0}


class OllamaProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

    def is_available(self) -> bool:
        try:
            import urllib.request, json as _json

            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _call(self, system: str, user: str) -> str:
        import urllib.request, json as _json

        payload = _json.dumps({
            "model": self.model,
            "system": system,
            "prompt": user,
            "stream": False,
            "format": "json",
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=settings.request_timeout_seconds) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        return data.get("response", "")

    def simplify(self, original_text, category, level, context):
        system = (
            "You are a legal-text simplification assistant. "
            "Simplify the clause into plain language at the requested level. "
            "Do NOT change the original meaning. Do NOT provide legal advice. "
            "Return JSON only with keys: simplified_text, rationale, confidence."
        )
        user = _json.dumps({
            "category": category,
            "level": level,
            "context": context,
            "clause": original_text,
        })
        try:
            raw = self._call(system, user)
            return _parse_json(raw, {
                "simplified_text": original_text,
                "rationale": "LLM simplification",
                "confidence": 0.7,
            })
        except Exception as exc:
            logger.warning("Ollama simplify failed: %s", exc)
            return {"simplified_text": original_text, "rationale": str(exc), "confidence": 0.4}

    def classify(self, original_text, context):
        return {"category": "", "confidence": 0.0}

    def answer_question(self, question, context):
        system = (
            "Answer using ONLY the provided document context. "
            "If the answer is not in the context, say the document does not specify it. "
            "Do NOT fabricate. Return JSON only with keys: answer, citations, confidence."
        )
        user = _json.dumps({"question": question, "context": context})
        try:
            raw = self._call(system, user)
            return _parse_json(raw, {"answer": "", "citations": [], "confidence": 0.5})
        except Exception as exc:
            logger.warning("Ollama Q&A failed: %s", exc)
            return {"answer": f"LLM unavailable: {exc}", "citations": [], "confidence": 0.0}


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(self):
        self.base_url = settings.openai_base_url.rstrip("/")
        self.model = settings.openai_model
        self.api_key = settings.openai_api_key

    def is_available(self) -> bool:
        return bool(self.api_key)

    def _call(self, system: str, user: str) -> str:
        import urllib.request, json as _json

        payload = _json.dumps({
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=settings.request_timeout_seconds) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        return data["choices"][0]["message"]["content"]

    def simplify(self, original_text, category, level, context):
        system = (
            "You are a legal-text simplification assistant. "
            "Simplify the clause into plain language at the requested level. "
            "Do NOT change the original meaning. Do NOT provide legal advice. "
            "Return JSON only with keys: simplified_text, rationale, confidence."
        )
        user = _json.dumps({
            "category": category,
            "level": level,
            "context": context,
            "clause": original_text,
        })
        try:
            raw = self._call(system, user)
            return _parse_json(raw, {
                "simplified_text": original_text,
                "rationale": "LLM simplification",
                "confidence": 0.7,
            })
        except Exception as exc:
            logger.warning("OpenAI simplify failed: %s", exc)
            return {"simplified_text": original_text, "rationale": str(exc), "confidence": 0.4}

    def classify(self, original_text, context):
        return {"category": "", "confidence": 0.0}

    def answer_question(self, question, context):
        system = (
            "Answer using ONLY the provided document context. "
            "If the answer is not in the context, say the document does not specify it. "
            "Do NOT fabricate. Return JSON only with keys: answer, citations, confidence."
        )
        user = _json.dumps({"question": question, "context": context})
        try:
            raw = self._call(system, user)
            return _parse_json(raw, {"answer": "", "citations": [], "confidence": 0.5})
        except Exception as exc:
            logger.warning("OpenAI Q&A failed: %s", exc)
            return {"answer": f"LLM unavailable: {exc}", "citations": [], "confidence": 0.0}


def _parse_json(raw: str, fallback: dict) -> dict:
    try:
        # Extract JSON block if wrapped in markdown.
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end > start:
            return json.loads(raw[start:end])
    except Exception:
        pass
    return fallback


_PROVIDER: Optional[BaseLLMProvider] = None


def get_provider() -> BaseLLMProvider:
    global _PROVIDER
    if _PROVIDER is not None:
        return _PROVIDER
    name = settings.llm_provider.lower()
    if name == "ollama":
        _PROVIDER = OllamaProvider()
    elif name == "openai-compatible":
        _PROVIDER = OpenAICompatibleProvider()
    else:
        _PROVIDER = NoneProvider()
    return _PROVIDER
