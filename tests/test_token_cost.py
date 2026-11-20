from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from ai_engineer_60.token_cost import (
    Usage,
    call_usage,
    cost_usd,
    count_input_tokens,
)

# --------------------------------------------------
# Usage dataclass tests
# --------------------------------------------------


def test_usage_default_output_tokens():
    usage = Usage(input_tokens=100)

    assert usage.input_tokens == 100
    assert usage.output_tokens == 0


def test_usage_with_input_and_output_tokens():
    usage = Usage(input_tokens=100, output_tokens=50)

    assert usage.input_tokens == 100
    assert usage.output_tokens == 50


def test_usage_is_immutable():
    usage = Usage(input_tokens=100, output_tokens=50)

    with pytest.raises(AttributeError):
        usage.input_tokens = 200


# --------------------------------------------------
# cost_usd() tests
# --------------------------------------------------


def test_cost_usd_input_tokens_only():
    usage = Usage(input_tokens=1_000_000)

    cost = cost_usd("claude-haiku-5-5", usage)

    assert cost == Decimal("0.10")


def test_cost_usd_output_tokens_only():
    usage = Usage(input_tokens=0, output_tokens=1_000_000)

    cost = cost_usd("claude-haiku-5-5", usage)

    assert cost == Decimal("0.50")


def test_cost_usd_with_input_and_output_tokens():
    usage = Usage(input_tokens=1000, output_tokens=500)

    cost = cost_usd("claude-haiku-5-5", usage)

    assert cost == Decimal("0.00035")


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("claude-haiku-5-5", Decimal("0.10")),
        ("claude-sonnet-5-5", Decimal("2")),
        ("claude-opus-5-5", Decimal("4")),
    ],
)
def test_cost_usd_different_models(model, expected):
    usage = Usage(input_tokens=1_000_000)

    assert cost_usd(model, usage) == expected


def test_cost_usd_invalid_model():
    usage = Usage(input_tokens=100)

    with pytest.raises(KeyError, match="No price for"):
        cost_usd("unknown-model", usage)


def test_cost_usd_zero_tokens():
    usage = Usage(input_tokens=0, output_tokens=0)

    assert cost_usd("claude-haiku-5-5", usage) == Decimal("0")


# --------------------------------------------------
# count_input_tokens() tests
# --------------------------------------------------


def test_count_input_tokens():
    client = MagicMock()

    client.messages.count_tokens.return_value = SimpleNamespace(input_tokens=25)

    result = count_input_tokens(
        client,
        "claude-haiku-5-5",
        "What is tokenization?",
    )

    assert result == 25

    client.messages.count_tokens.assert_called_once_with(
        model="claude-haiku-5-5",
        messages=[{"role": "user", "content": "What is tokenization?"}],
    )


# --------------------------------------------------
# call_usage() tests
# --------------------------------------------------


def test_call_usage():
    client = MagicMock()

    client.messages.create.return_value = SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=30,
            output_tokens=100,
        )
    )

    result = call_usage(
        client,
        "claude-haiku-5-5",
        "Explain BPE",
    )

    assert result == Usage(
        input_tokens=30,
        output_tokens=100,
    )

    client.messages.create.assert_called_once_with(
        model="claude-haiku-5-5",
        max_tokens=200,
        messages=[{"role": "user", "content": "Explain BPE"}],
    )


def test_call_usage_custom_max_tokens():
    client = MagicMock()

    client.messages.create.return_value = SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=10,
            output_tokens=50,
        )
    )

    result = call_usage(
        client,
        "claude-sonnet-5-5",
        "Explain embeddings",
        max_tokens=500,
    )

    assert result.input_tokens == 10
    assert result.output_tokens == 50

    client.messages.create.assert_called_once_with(
        model="claude-sonnet-5-5",
        max_tokens=500,
        messages=[{"role": "user", "content": "Explain embeddings"}],
    )
