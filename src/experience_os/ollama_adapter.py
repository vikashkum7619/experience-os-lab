from __future__ import annotations

import os

from ollama import Client

from experience_os.llm_adapter import (
    LLMAdapter,
    LLMMessage,
    LLMResponse,
)


class OllamaAdapter(LLMAdapter):
    """
    Ollama implementation of LLMAdapter.

    Supports any locally installed Ollama model.

    Examples
    --------
    adapter = OllamaAdapter()

    response = adapter.generate(
        "Explain Experience OS."
    )

    print(response.text)
    """

    def __init__(
        self,
        *,
        model: str = "qwen3:8b",
        host: str = "http://localhost:11434",
        temperature: float = 0.2,
        num_ctx: int = 16384,
        timeout: float = 120.0,
        system_prompt: str | None = None,
    ) -> None:

        self._model = os.getenv(
            "OLLAMA_MODEL",
            model,
        )

        self._host = os.getenv(
            "OLLAMA_HOST",
            host,
        )

        self._temperature = temperature
        self._num_ctx = num_ctx
        self._system_prompt = system_prompt

        self._client = Client(
            host=self._host,
            timeout=timeout,
        )

    @property
    def model_name(self) -> str:
        return self._model

    # ---------------------------------------------------------
    # Generate
    # ---------------------------------------------------------

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a completion from Ollama.
        """

        messages: list[dict[str, str]] = []

        if self._system_prompt:
            messages.append(
                {
                    "role": "system",
                    "content": self._system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        try:

            response = self._client.chat(
                model=self._model,
                messages=messages,
                options={
                    "temperature": self._temperature,
                    "num_ctx": self._num_ctx,
                },
            )

        except Exception as exc:
            raise RuntimeError(
                f"Failed to generate response using "
                f"Ollama model '{self._model}'. "
                f"Is Ollama running? "
                f"Original error: {exc}"
            ) from exc

        text = response["message"]["content"]

        return LLMResponse(
            text=text,
            model=self._model,
            prompt_tokens=response.get(
                "prompt_eval_count",
                0,
            ),
            completion_tokens=response.get(
                "eval_count",
                0,
            ),
        )

    # ---------------------------------------------------------
    # Chat
    # ---------------------------------------------------------

    def chat(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        """
        Native chat implementation.
        """

        payload: list[dict[str, str]] = []

        if self._system_prompt:
            payload.append(
                {
                    "role": "system",
                    "content": self._system_prompt,
                }
            )

        payload.extend(
            {
                "role": message.role,
                "content": message.content,
            }
            for message in messages
        )

        try:

            response = self._client.chat(
                model=self._model,
                messages=payload,
                options={
                    "temperature": self._temperature,
                    "num_ctx": self._num_ctx,
                },
            )

        except Exception as exc:
            raise RuntimeError(
                f"Failed to chat using "
                f"Ollama model '{self._model}'. "
                f"Original error: {exc}"
            ) from exc

        text = response["message"]["content"]

        return LLMResponse(
            text=text,
            model=self._model,
            prompt_tokens=response.get(
                "prompt_eval_count",
                0,
            ),
            completion_tokens=response.get(
                "eval_count",
                0,
            ),
        )