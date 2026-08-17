from __future__ import annotations

from openai import OpenAI

from experience_os.llm_adapter import (
    LLMAdapter,
    LLMResponse,
)


class OpenAIAdapter(LLMAdapter):
    """
    OpenAI implementation of LLMAdapter.

    Example
    -------
    adapter = OpenAIAdapter(
        api_key="YOUR_API_KEY",
        model="gpt-5",
    )

    response = adapter.generate(
        "Explain Experience OS."
    )

    print(response.text)
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str = "gpt-5",
        temperature: float = 0.2,
        max_tokens: int = 1024,
        system_prompt: str | None = None,
    ) -> None:

        self._client = OpenAI(
            api_key=api_key,
        )

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._system_prompt = system_prompt

    @property
    def model_name(self) -> str:
        return self._model

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a completion using OpenAI Chat Completions.
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

        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=self._temperature,
            max_completion_tokens=self._max_tokens,
        )

        text = response.choices[0].message.content or ""

        usage = response.usage

        prompt_tokens = (
            usage.prompt_tokens
            if usage is not None
            else 0
        )

        completion_tokens = (
            usage.completion_tokens
            if usage is not None
            else 0
        )

        return LLMResponse(
            text=text,
            model=self._model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )