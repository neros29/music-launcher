from unittest.mock import MagicMock, call
import pytest

from sys import path
path.append("src/")
from lexer import Lexer, Token, Tokens, basic_types, token_types


@pytest.fixture
def lexer():
    type_keywords = {
            "artist": "artist",
            "title": "title",
            "playlists": "playlists",
            "playlist": "playlists",
            "album": "playlists",
            "albums": "playlists",
            "date": "date",
            "genre": "genre",
            "duration": "duration",
            "songs": "songs",
            "song": "songs"
            }
    operator_keywords = {
            "and": "and",
            "or": "or",
            "|": "or",
            "&": "and"
            }

    seperators= {
            " ": basic_types.WS,
            "\n": basic_types.WS,
            "\t": basic_types.WS,
            "\\": basic_types.ESC,
            '"': basic_types.D_QUOTES,
            "'": basic_types.S_QUOTES,
            ":": basic_types.SEP,
            "(": basic_types.L_OP,
            ")": basic_types.R_OP
            }
    return Lexer(type_keywords, operator_keywords, seperators)

@pytest.mark.parametrize("string, expected", [
    ('artist: ironmouse', [("", token_types.SOF), ("artist:", token_types.TYPE), (" ironmouse", token_types.VALUE),("", token_types.EOF)]),
    ('artist: artist', [("", token_types.SOF), ("artist:", token_types.TYPE), (" artist", token_types.VALUE),("", token_types.EOF)]),
    ('artist: "artist"', [("", token_types.SOF), ("artist:", token_types.TYPE), (" \"artist\"", token_types.S_VALUE),("", token_types.EOF)]),
    ('artist: "artist" and title: and', [("", token_types.SOF), ("artist:", token_types.TYPE), (" \"artist\"", token_types.S_VALUE), (" and", token_types.OP), (" title:", token_types.TYPE), (" and", token_types.VALUE),("", token_types.EOF)]),
    ('artist: \'artist\'', [("", token_types.SOF), ("artist:", token_types.TYPE), (" 'artist'", token_types.S_VALUE),("", token_types.EOF)]),
    ('artist: unicode 🤖', [("", token_types.SOF), ("artist:", token_types.TYPE), (" unicode 🤖", token_types.VALUE),("", token_types.EOF)]),
    ("artist: 'ironmouse", [("", token_types.SOF), ("artist:", token_types.TYPE), (" 'ironmouse", token_types.VALUE),("", token_types.EOF)]),
    ("artist:ironmouse", [("", token_types.SOF), ("artist:", token_types.TYPE), ("ironmouse", token_types.VALUE),("", token_types.EOF)]),
    ("artist:\x00\n\tironmouse", [("", token_types.SOF), ("artist:", token_types.TYPE), ("\x00\n\tironmouse", token_types.VALUE),("", token_types.EOF)]),
    ('artist: "\\"artist\\""', [("", token_types.SOF), ("artist:", token_types.TYPE), (' "\\"artist\\""', token_types.S_VALUE),("", token_types.EOF)]),
    ('', [("", token_types.SOF),("", token_types.EOF)]),
    ('!@#$%^&*', [("", token_types.SOF), ("!@#$%^&*", token_types.VALUE),("", token_types.EOF)]),
    ('some random text', [("", token_types.SOF),("some random text", token_types.VALUE),("", token_types.EOF)]),
    ('playlists: (title: left right)', [("", token_types.SOF), ("playlists:", token_types.TYPE), (" (", token_types.L_OP), ("title:", token_types.TYPE), (' left right', token_types.VALUE), (")", token_types.R_OP), ("", token_types.EOF)]),
    ])

def test_lexing(lexer, string, expected):
    results = [(i.value, i.token_type) for i in lexer.lex(string)]
    assert results == expected


