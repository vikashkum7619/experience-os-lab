from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from experience_os.llm_adapter import (
    LLMMessage,
    LLMResponse,
)
from experience_os.ollama_adapter import OllamaAdapter


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------


@pytest.fixture
def mock_response() -> dict:
    return {
        "message": {
            "content": "Hello from Qwen3",
        },
        "prompt_eval_count": 15,
        "eval_count": 7,
    }


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------


def test_default_model_name() -> None:
    adapter = OllamaAdapter()

    assert adapter.model_name == "qwen3:8b"


def test_custom_model_name() -> None:
    adapter = OllamaAdapter(
        model="mistral:latest",
    )

    assert adapter.model_name == "mistral:latest"


# ---------------------------------------------------------
# generate()
# ---------------------------------------------------------


@patch("experience_os.ollama_adapter.Client")
def test_generate_returns_llm_response(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    response = adapter.generate("Hello")

    assert isinstance(response, LLMResponse)
    assert response.text == "Hello from Qwen3"
    assert response.model == "qwen3:8b"
    assert response.prompt_tokens == 15
    assert response.completion_tokens == 7
    assert response.total_tokens == 22


@patch("experience_os.ollama_adapter.Client")
def test_generate_calls_client_chat(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    adapter.generate("Explain AI")

    mock_client.chat.assert_called_once()

    kwargs = mock_client.chat.call_args.kwargs

    assert kwargs["model"] == "qwen3:8b"
    assert kwargs["messages"][0]["role"] == "user"
    assert kwargs["messages"][0]["content"] == "Explain AI"


@patch("experience_os.ollama_adapter.Client")
def test_generate_uses_system_prompt(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter(
        system_prompt="You are helpful.",
    )

    adapter.generate("Hello")

    kwargs = mock_client.chat.call_args.kwargs

    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == "You are helpful"

    assert kwargs["messages"][1]["role"] == "user"


@patch("experience_os.ollama_adapter.Client")
def test_generate_wraps_exception(
    mock_client_class,
) -> None:

    mock_client = Mock()
    mock_client.chat.side_effect = Exception("Boom")

    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    with pytest.raises(RuntimeError):
        adapter.generate("Hello")


# ---------------------------------------------------------
# chat()
# ---------------------------------------------------------


@patch("experience_os.ollama_adapter.Client")
def test_chat_returns_response(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    response = adapter.chat(
        [
            LLMMessage(
                role="user",
                content="Hi",
            )
        ]
    )

    assert isinstance(response, LLMResponse)
    assert response.text == "Hello from Qwen3"


@patch("experience_os.ollama_adapter.Client")
def test_chat_passes_messages(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    adapter.chat(
        [
            LLMMessage(
                role="system",
                content="A",
            ),
            LLMMessage(
                role="user",
                content="B",
            ),
        ]
    )

    kwargs = mock_client.chat.call_args.kwargs

    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == "A"

    assert kwargs["messages"][1]["role"] == "user"
    assert kwargs["messages"][1]["content"] == "B"


@patch("experience_os.ollama_adapter.Client")
def test_chat_appends_system_prompt(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter(
        system_prompt="Global prompt",
    )

    adapter.chat(
        [
            LLMMessage(
                role="user",
                content="Hello",
            )
        ]
    )

    kwargs = mock_client.chat.call_args.kwargs

    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == "Global prompt"

    assert kwargs["messages"][1]["role"] == "user"


@patch("experience_os.ollama_adapter.Client")
def test_chat_wraps_exception(
    mock_client_class,
) -> None:

    mock_client = Mock()
    mock_client.chat.side_effect = Exception("Boom")

    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    with pytest.raises(RuntimeError):
        adapter.chat(
            [
                LLMMessage(
                    role="user",
                    content="Hello",
                )
            ]
        )


# ---------------------------------------------------------
# Token counting
# ---------------------------------------------------------


@patch("experience_os.ollama_adapter.Client")
def test_total_tokens(
    mock_client_class,
    mock_response,
) -> None:

    mock_client = Mock()
    mock_client.chat.return_value = mock_response
    mock_client_class.return_value = mock_client

    adapter = OllamaAdapter()

    response = adapter.generate("Prompt")

    assert response.total_tokens == (
        response.prompt_tokens
        + response.completion_tokens
    )