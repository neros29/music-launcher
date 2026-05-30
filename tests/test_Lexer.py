import pytest
from sys import path

path.append("src/")
from langdef import token_types
from lexer import Lexer


@pytest.fixture
def lexer():
    return Lexer()

@pytest.mark.parametrize("string, expected", [
    ('artist: ironmouse', [("", token_types.SOF), ("artist:", token_types.TYPE), (" ironmouse", token_types.VALUE),("", token_types.EOF)]),
    ('artist:', [("", token_types.SOF), ("artist:", token_types.VALUE), ("", token_types.EOF)]),
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

def test_multiple_querys(lexer):
    string1 = "artist: ironmouse title: king"
    string2 = "playlists:"
    r1 = lexer.lex(string1)
    r2 = lexer.lex(string2)
    assert len(r1.data) == 6
    assert len(r2.data) == 3

