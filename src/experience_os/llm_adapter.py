from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------


@dataclass(slots=True, frozen=True)
class LLMMessage:
    """
    Single message exchanged with an LLM.
    """

    role: str
    content: str


@dataclass(slots=True, frozen=True)
class LLMResponse:
    """
    Response returned by an LLM.
    """

    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return (
            self.prompt_tokens
            + self.completion_tokens
        )


# ---------------------------------------------------------
# Adapter Interface
# ---------------------------------------------------------


class LLMAdapter(ABC):
    """
    Base class for all language model adapters.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """
        Name of the underlying model.
        """
        raise NotImplementedError

    @abstractmethod
    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:
        """
        Generate a completion.
        """
        raise NotImplementedError

    def chat(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        """
        Default chat implementation.

        Concatenates messages into a prompt and
        delegates to generate().
        """

        prompt = "\n".join(
            f"{message.role}: {message.content}"
            for message in messages
        )

        return self.generate(prompt)


# ---------------------------------------------------------
# Dummy Adapter
# ---------------------------------------------------------


class DummyLLMAdapter(LLMAdapter):
    """
    Deterministic adapter used for testing.
    """

    def __init__(
        self,
        response: str = "dummy response",
    ) -> None:
        self._response = response

    @property
    def model_name(self) -> str:
        return "dummy"

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        return LLMResponse(
            text=self._response,
            model=self.model_name,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(
                self._response.split()
            ),
        )


# ---------------------------------------------------------
# Echo Adapter
# ---------------------------------------------------------


class EchoLLMAdapter(LLMAdapter):
    """
    Returns the prompt itself.

    Useful for debugging prompt builders.
    """

    @property
    def model_name(self) -> str:
        return "echo"

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        return LLMResponse(
            text=prompt,
            model=self.model_name,
            prompt_tokens=len(prompt.split()),
            completion_tokens=len(prompt.split()),
        )