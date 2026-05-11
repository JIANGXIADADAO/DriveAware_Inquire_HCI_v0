import os
from src.interaction.nlp_parser import NLPParser


def test_yes_variants_to_dynamic():
    parser = NLPParser()
    for text in ["yes", "yeah", "yep", "y", "ok", "okay", "sure",
                 "yes please", "of course", "absolutely", "definitely"]:
        result = parser._keyword_parse(text)
        assert result == "dynamic", f"'{text}' should be dynamic, got '{result}'"


def test_whisper_mishearings_of_yes():
    parser = NLPParser()
    for text in ["yinz", "yis", "yass", "yesss", "yees", "yas", "yus", "yiss"]:
        result = parser._keyword_parse(text)
        assert result == "dynamic", f"'{text}' should be dynamic (Whisper mishearing), got '{result}'"


def test_no_variants_to_rest():
    parser = NLPParser()
    for text in ["no", "nope", "nah", "n", "no thanks"]:
        result = parser._keyword_parse(text)
        assert result == "rest", f"'{text}' should be rest, got '{result}'"


def test_whisper_truncations_of_rest():
    parser = NLPParser()
    for text in ["res", "ress", "switch to res mode", "go to res"]:
        result = parser._keyword_parse(text)
        assert result == "rest", f"'{text}' should be rest (Whisper truncation), got '{result}'"


def test_embedded_dynamic_keyword():
    parser = NLPParser()
    result = parser._keyword_parse("I want dynamic mode please")
    assert result == "dynamic"


def test_embedded_rest_keyword():
    parser = NLPParser()
    result = parser._keyword_parse("please stay in rest mode")
    assert result == "rest"


def test_embedded_calm_keyword():
    parser = NLPParser()
    result = parser._keyword_parse("I feel calm today")
    assert result == "rest"


def test_embedded_relax_keyword():
    parser = NLPParser()
    result = parser._keyword_parse("let's relax")
    assert result == "rest"


def test_unknown_transcript():
    parser = NLPParser()
    result = parser._keyword_parse("hello world")
    assert result == "unknown"


def test_empty_transcript():
    parser = NLPParser()
    result = parser._keyword_parse("")
    assert result == "unknown"


def test_single_word_dynamic():
    parser = NLPParser()
    assert parser._keyword_parse("dynamic") == "dynamic"


def test_single_word_rest():
    parser = NLPParser()
    assert parser._keyword_parse("rest") == "rest"
