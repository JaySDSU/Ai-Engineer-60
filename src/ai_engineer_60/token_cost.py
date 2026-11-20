"""Day 2: count tokens and estimate cost for 5 prompts across models.

Usage:
    uv run python token_cost.py            # count only (free endpoint)
    uv run python token_cost.py --call     # also make real calls, use response.usage

Learning:
You can count tokens before sending a request and estimate the input cost.
Different models can tokenize the same text differently.
Input and output tokens have different costs.
Token usage should be monitored in production.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal

import anthropic
from dotenv import find_dotenv, load_dotenv

# USD per 1M tokens, from https://platform.claude.com/docs/en/about-claude/pricing (checked 2026-11-18).
PRICES: dict[str, dict[str, Decimal]] = {
    "claude-haiku-5-5": {"input": Decimal("0.10"), "output": Decimal("0.50")},  # <=100K-token prompts
    "claude-sonnet-5-5": {"input": Decimal("2"), "output": Decimal("10")},
    "claude-opus-5-5": {"input": Decimal("4"), "output": Decimal("20")},
}
PER_MILLION = Decimal(1_000_000)

PROMPTS: dict[str, str] = {
    "short_en": "What is a token?",
    "long_en": "Explain byte-pair encoding, why LLMs use subword tokens instead of words, "
    "and how vocabulary size trades off sequence length against embedding-table size. " * 3,
    "code": "def two_sum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n            return [seen[target - n], i]\n        seen[n] = i\n",
    "numbers": "Revenue 2024: 1234567.89; 2025: 2345678.90; growth 90.04%; RevPAR $187.42",
    "non_english": "トークン化とは、テキストをモデルが処理できる単位に分割することです。",
}


@dataclass(frozen=True)
class Usage:
    input_tokens: int
    output_tokens: int = 0


def cost_usd(model: str, usage: Usage) -> Decimal:
    """Cost of one request. Decimal avoids float rounding on money."""
    if model not in PRICES:
        raise KeyError(f"No price for {model!r}; add it to PRICES")
    p = PRICES[model]
    return (usage.input_tokens * p["input"] + usage.output_tokens * p["output"]) / PER_MILLION


def count_input_tokens(client: anthropic.Anthropic, model: str, prompt: str) -> int:
    resp = client.messages.count_tokens(model=model, messages=[{"role": "user", "content": prompt}])
    return resp.input_tokens


def call_usage(client: anthropic.Anthropic, model: str, prompt: str, max_tokens: int = 200) -> Usage:
    resp = client.messages.create(model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])
    return Usage(resp.usage.input_tokens, resp.usage.output_tokens)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--call", action="store_true", help="make real calls to get output tokens")
    args = parser.parse_args()
    load_dotenv(find_dotenv(usecwd=True))
    client = anthropic.Anthropic()

    print(f"{'prompt':<12} {'chars':>6} {'model':<18} {'in_tok':>7} {'out_tok':>7} {'chars/tok':>9} {'cost $':>11}")
    for name, prompt in PROMPTS.items():
        for model in PRICES:
            if args.call:
                usage = call_usage(client, model, prompt)
            else:
                usage = Usage(count_input_tokens(client, model, prompt))
            ratio = len(prompt) / usage.input_tokens
            print(
                f"{name:<12} {len(prompt):>6} {model:<18} {usage.input_tokens:>7} "
                f"{usage.output_tokens:>7} {ratio:>9.2f} {cost_usd(model, usage):>11.6f}"
            )


if __name__ == "__main__":
    main()


"""
Output:
uv run python token_cost.py --call
prompt        chars model               in_tok out_tok chars/tok      cost $
short_en         16 claude-haiku-5-5        13     200      1.23    0.000101
short_en         16 claude-sonnet-5-5       13     200      1.23    0.002026
short_en         16 claude-opus-5-5         13     200      1.23    0.004052
long_en         465 claude-haiku-5-5       161     200      2.89    0.000116
long_en         465 claude-sonnet-5-5      161     200      2.89    0.002322
long_en         465 claude-opus-5-5        161     200      2.89    0.004644
code            166 claude-haiku-5-5        73     200      2.27    0.000107
code            166 claude-sonnet-5-5       73     200      2.27    0.002146
code            166 claude-opus-5-5         73     200      2.27    0.004292
numbers          73 claude-haiku-5-5        51     200      1.43    0.000105
numbers          73 claude-sonnet-5-5       51     200      1.43    0.002102
numbers          73 claude-opus-5-5         51     200      1.43    0.004204
non_english      34 claude-haiku-5-5        35     200      0.97    0.000104
non_english      34 claude-sonnet-5-5       35     200      0.97    0.002070
non_english      34 claude-opus-5-5         35     200      0.97    0.004140

uv run python token_cost.py
prompt        chars model               in_tok out_tok chars/tok      cost $
short_en         16 claude-haiku-5-5        13       0      1.23    0.000001
short_en         16 claude-sonnet-5-5       13       0      1.23    0.000026
short_en         16 claude-opus-5-5         13       0      1.23    0.000052
long_en         465 claude-haiku-5-5       161       0      2.89    0.000016
long_en         465 claude-sonnet-5-5      161       0      2.89    0.000322
long_en         465 claude-opus-5-5        161       0      2.89    0.000644
code            166 claude-haiku-5-5        73       0      2.27    0.000007
code            166 claude-sonnet-5-5       73       0      2.27    0.000146
code            166 claude-opus-5-5         73       0      2.27    0.000292
numbers          73 claude-haiku-5-5        51       0      1.43    0.000005
numbers          73 claude-sonnet-5-5       51       0      1.43    0.000102
numbers          73 claude-opus-5-5         51       0      1.43    0.000204
non_english      34 claude-haiku-5-5        35       0      0.97    0.000004
non_english      34 claude-sonnet-5-5       35       0      0.97    0.000070
non_english      34 claude-opus-5-5         35       0      0.97    0.000140
"""
