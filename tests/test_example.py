import pytest
import sys
sys.path.append("src/")

from parser import Parser
from string import printable

@pytest.fixture
def parser():
    return Parser()


# ==============================================================================
# 1. THE "OOPS, I FORGOT SOMETHING" TESTS (MISSING SYNTAX)
# ==============================================================================

@pytest.mark.parametrize("missing_syntax_str", [
    "artist: ",                           # Missing value entirely
    ": \"*iron*\"",                       # Missing key entirely
    "title: a | : b",                     # Missing key after an operator
    "   ",                                # Pure whitespace
    "",                                   # Empty string
    "Just some random unkeyed text"       # No keywords or colons anywhere
])
def test_parse_handles_missing_syntax_gracefully(parser, missing_syntax_str):
    """
    Ensures the parser handles structurally incomplete strings safely.
    It should either fall back to default behavior or return None, 
    but it must NEVER raise an unhandled exception (e.g., IndexError).
    """
    try:
        result = parser.parse(missing_syntax_str)
        # If it returns a result, ensure it's either None or a structured dict
        assert result is None or isinstance(result, dict)
    except Exception as e:
        pytest.fail(f"Parser crashed with {type(e).__name__}: {e} on input: '{missing_syntax_str}'")


# ==============================================================================
# 2. THE OPERATOR ABUSE TESTS
# ==============================================================================

@pytest.mark.parametrize("operator_abuse_str", [
    "artist: \"iron\" & | title: \"left\"",  # Consecutive operators
    "artist: \"*iron*\" |",                  # Trailing operator
    "| artist: \"*iron*\"",                  # Leading operator
    "artist: \"iron\" && title: \"left\"",   # Doubled up operator symbols
])
def test_parse_handles_operator_abuse(parser, operator_abuse_str):
    """
    Tests how the state machine and the even/odd index logic in _final_pass
    handles operators that break standard grammar rules.
    """
    # This assertion checks that the parser handles the abuse safely without crashing.
    # Depending on your goals, you might want this to return None.
    result = parser.parse(operator_abuse_str)
    assert result is None or "query" in result


# ==============================================================================
# 3. QUOTE AND CHARACTER SHENANIGANS
# ==============================================================================

def test_parse_handles_mismatched_quotes(parser):
    """
    Checks if regex in _third_pass allows mismatched start/end quotes.
    Input starts with double quote but ends with single quote.
    """
    string = "artist: \"*iron*'"
    result = parser.parse(string)
    
    # If your parser requires matching quotes, this should be a 'fuzz' match, NOT an 're' match.
    if result and "query" in result:
        pair = result["query"][0]
        assert "fuzz" in pair, "Mismatched quotes were incorrectly parsed as a valid regex/exact match!"


def test_parse_handles_colons_inside_quotes(parser):
    """
    Verifies if a colon inside a quoted string breaks the first-pass tokenizer.
    """
    string = 'title: "Lord of the Rings: The Two Towers"'
    result = parser.parse(string)
    
    assert result is not None
    # The entire movie title should remain intact as the value
    assert result["query"][0]["re"] == "Lord of the Rings: The Two Towers"


@pytest.mark.parametrize("apostrophe_str", [
    "title: Don't stop me now",
    "title: 'Don't stop me now'"
])
def test_parse_handles_apostrophes_in_fuzz_matching(parser, apostrophe_str):
    """Tests whether single quotes used as apostrophes break the parser."""
    result = parser.parse(apostrophe_str)
    assert result is not None
    assert "query" in result


# ==============================================================================
# 4. CASE SENSITIVITY AND TYPOS
# ==============================================================================

def test_parse_is_case_insensitive_for_keywords(parser):
    """
    Checks if capitalized or uppercase keywords are recognized.
    Currently, 'ARTIST' is not in `self.song_key_words`.
    """
    string = 'ARTIST: "*iron*"'
    result = parser.parse(string)
    
    assert result is not None
    # If case-insensitivity isn't implemented, this key will likely default to 'title'
    assert result["query"][0]["key"] == "artist"


# ==============================================================================
# ORIGINAL FUNCTIONAL TESTS (PREVIOUS BEST PRACTICES)
# ==============================================================================

def test_first_pass_tokenizes_delimiters_correctly(parser):
    string = 'songs: artist: "*iron*"  title :Arent we all teh worst | title : \'Left*\'' 
    expected = [
        "songs", ":", " ", "artist", ":", " ", '"*iron*"', " ", " ", 
        "title", " ", ":", "Arent", " ", "we", " ", "all", " ", "teh", 
        " ", "worst", " ", "|", " ", "title", " ", ":", ' ', "'Left*'"
    ]
    assert parser._first_pass(string) == expected


def test_second_pass_groups_keys_and_values(parser):
    tokens = [
        "songs", ":", " ", "artist", ":", " ", '"*iron*"', " ", " ", 
        "title", " ", ":", "Arent", " ", "we", " ", "all", " ", "teh", 
        " ", "worst", " ", "|", " ", "title", " ", ":", ' ', "'Left*'"
    ]
    expected = [
        {"key": "songs"}, {"key": "artist"}, {"value": '"*iron*"'}, 
        {"key": "title"}, {"value": "Arent we all teh worst"}, 
        {"operator": "|"}, {"key": "title"}, {"value": "'Left*'"}
    ]
    assert parser._secound_pass(tokens) == expected


def test_third_pass_identifies_regex_vs_fuzz_matching(parser):
    tokens = [
        {"key": "songs"}, {"key": "artist"}, {"value": '"*iron*"'}, 
        {"key": "title"}, {"value": "Arent we all teh worst"}, 
        {"operator": "|"}, {"key": "title"}, {"value": "'Left*'"}
    ]
    expected = [
        {"key": "songs"}, 
        {"pair": {"key": "artist", "re": "*iron*"}}, 
        {"pair": {"key": "title", "fuzz": "Arent we all teh worst"}}, 
        {"operator": "|"}, 
        {"pair": {"key": "title", "re": "Left*"}} 
    ]
    assert parser._third_pass(tokens) == expected


@pytest.mark.parametrize("query_string, expected_results_type", [
    ('songs : artist : "*iron*" title : Arent we all teh worst|title : \'Left*\'', "songs"),
    ('artist:"*iron*" title:Arent we all teh worst|title:\'Left*\'', "playlists"),
    ('artist        :        "*iron*"       title     :     Arent we all teh worst    |      title:     \'Left*\'', "playlists")
])
def test_parse_handles_varying_spacing_and_defaults(parser, query_string, expected_results_type):
    expected_ast = {
        "results": expected_results_type, 
        "query": [
            {"key": "artist", "re": "*iron*"}, "and", 
            {"key": "title", "fuzz": "Arent we all teh worst"}, "or", 
            {"key": "title", "re": "Left*"}
        ]
    }
    assert parser.parse(query_string) == expected_ast


