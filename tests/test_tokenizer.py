from ai_engineer_60.tokenizer import Tokenizer


def test_round_trip():
    text = "Hello, byte pair encoding!"

    tokenizer = Tokenizer()
    tokenizer.train(text, 270)

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text


def test_toy_example():
    text = "aaabdaaabac"

    tokenizer = Tokenizer()
    tokenizer.train(text, 270)

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text
    assert len(encoded) < len(text.encode("utf-8"))


def test_short_text():
    text = "ab"

    tokenizer = Tokenizer()
    tokenizer.train(text, 300)

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text
    assert len(tokenizer.merges) == 1
    assert encoded == [256]


def test_single_character():
    text = "a"

    tokenizer = Tokenizer()
    tokenizer.train(text, 300)

    encoded = tokenizer.encode(text)
    decoded = tokenizer.decode(encoded)

    assert decoded == text
    assert len(tokenizer.merges) == 0
    assert encoded == [97]
