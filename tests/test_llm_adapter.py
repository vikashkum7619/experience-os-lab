from __future__ import annotations

import pytest

from experience_os.llm_adapter import (
    DummyLLMAdapter,
    EchoLLMAdapter,
    LLMAdapter,
    LLMMessage,
    LLMResponse,
)


# ---------------------------------------------------------
# Models
# ---------------------------------------------------------


def test_message_creation() -> None:
    message = LLMMessage(
        role="user",
        content="Hello",
    )

    assert message.role == "user"
    assert message.content == "Hello"


def test_response_creation() -> None:
    response = LLMResponse(
        text="Hi",
        model="dummy",
        prompt_tokens=5,
        completion_tokens=3,
    )

    assert response.text == "Hi"
    assert response.model == "dummy"


def test_total_tokens() -> None:
    response = LLMResponse(
        text="answer",
        model="dummy",
        prompt_tokens=12,
        completion_tokens=8,
    )

    assert response.total_tokens == 20


# ---------------------------------------------------------
# Dummy Adapter
# ---------------------------------------------------------


def test_dummy_model_name() -> None:
    adapter = DummyLLMAdapter()

    assert adapter.model_name == "dummy"


def test_dummy_generate_returns_response() -> None:
    adapter = DummyLLMAdapter()

    response = adapter.generate(
        "What is AI?"
    )

    assert isinstance(
        response,
        LLMResponse,
    )

    assert response.text == "dummy response"


def test_dummy_custom_response() -> None:
    adapter = DummyLLMAdapter(
        response="custom",
    )

    response = adapter.generate(
        "hello",
    )

    assert response.text == "custom"


def test_dummy_prompt_tokens() -> None:
    adapter = DummyLLMAdapter()

    response = adapter.generate(
        "one two three four",
    )

    assert response.prompt_tokens == 4


def test_dummy_completion_tokens() -> None:
    adapter = DummyLLMAdapter(
        response="one two",
    )

    response = adapter.generate(
        "hello",
    )

    assert response.completion_tokens == 2


# ---------------------------------------------------------
# Echo Adapter
# ---------------------------------------------------------


def test_echo_model_name() -> None:
    adapter = EchoLLMAdapter()

    assert adapter.model_name == "echo"


def test_echo_returns_prompt() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.generate(
        "experience os",
    )

    assert response.text == "experience os"


def test_echo_token_count() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.generate(
        "one two three",
    )

    assert response.prompt_tokens == 3
    assert response.completion_tokens == 3


# ---------------------------------------------------------
# Chat
# ---------------------------------------------------------


def test_chat_single_message() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.chat(
        [
            LLMMessage(
                role="user",
                content="Hello",
            )
        ]
    )

    assert "Hello" in response.text


def test_chat_multiple_messages() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.chat(
        [
            LLMMessage(
                role="system",
                content="You are helpful.",
            ),
            LLMMessage(
                role="user",
                content="Hi",
            ),
        ]
    )

    assert "system:" in response.text
    assert "user:" in response.text


def test_chat_uses_generate() -> None:
    adapter = DummyLLMAdapter()

    response = adapter.chat(
        [
            LLMMessage(
                role="user",
                content="Hello",
            )
        ]
    )

    assert response.text == "dummy response"


def test_chat_empty_messages() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.chat([])

    assert response.text == ""


# ---------------------------------------------------------
# Abstract Interface
# ---------------------------------------------------------


class FakeAdapter(LLMAdapter):

    @property
    def model_name(self) -> str:
        return "fake"

    def generate(
        self,
        prompt: str,
    ) -> LLMResponse:

        return LLMResponse(
            text="ok",
            model=self.model_name,
        )


def test_custom_adapter() -> None:
    adapter = FakeAdapter()

    response = adapter.generate(
        "hello",
    )

    assert response.text == "ok"
    assert response.model == "fake"


def test_custom_adapter_chat() -> None:
    adapter = FakeAdapter()

    response = adapter.chat(
        [
            LLMMessage(
                role="user",
                content="Hello",
            )
        ]
    )

    assert response.text == "ok"


# ---------------------------------------------------------
# Misc
# ---------------------------------------------------------


def test_dummy_is_llm_adapter() -> None:
    adapter = DummyLLMAdapter()

    assert isinstance(
        adapter,
        LLMAdapter,
    )


def test_echo_is_llm_adapter() -> None:
    adapter = EchoLLMAdapter()

    assert isinstance(
        adapter,
        LLMAdapter,
    )


def test_response_total_tokens_zero() -> None:
    response = LLMResponse(
        text="",
        model="dummy",
    )

    assert response.total_tokens == 0


def test_dummy_response_model_name() -> None:
    adapter = DummyLLMAdapter()

    response = adapter.generate(
        "hello",
    )

    assert response.model == "dummy"


def test_echo_response_model_name() -> None:
    adapter = EchoLLMAdapter()

    response = adapter.generate(
        "hello",
    )

    assert response.model == "echo"