from typing import List
import pytest
from sys import path

path.append("src/")
from lexer import Tokens, Lexer
from langdef import token_types
from parser import Parser, Pair

@pytest.fixture
def parser():
    return Parser()

def gen_tokens(string: str) -> Tokens:
    lexer = Lexer()
    return lexer.lex(string)

def get_results(pairs: List[Pair]):
    results = []
    for i in pairs:
        if i.data_type == "scope":
            results.append((i.key, i.data_type, get_results(i.data)))
        else:
            results.append((i.key, i.data_type, i.data))
    return results
    
@pytest.mark.parametrize("tokens, expected", [
    (gen_tokens("playlists: artist: ironmouse"), [("", token_types.SOF), ("playlists:", token_types.TYPE), ("(", token_types.L_OP), (" artist:", token_types.TYPE), (' ironmouse', token_types.VALUE), (")", token_types.R_OP), ("", token_types.EOF)]),
    (gen_tokens("playlists: (ironmouse)"), [("", token_types.SOF), ("playlists:", token_types.TYPE), (" (", token_types.L_OP), (" artist:", token_types.TYPE), ('ironmouse', token_types.VALUE), (")", token_types.R_OP), ("", token_types.EOF)]),
    (gen_tokens("(ironmouse title: left right)"), [("", token_types.SOF), (" artist:", token_types.TYPE), ("(", token_types.L_OP), (" artist:", token_types.TYPE), ('ironmouse', token_types.VALUE), (" and ", token_types.OP), (" title:", token_types.TYPE), (" left right", token_types.VALUE), (")", token_types.R_OP), ("", token_types.EOF)])
    ])

def test_fix_tokens(parser, tokens, expected):
    parser.tokens = tokens
    parser._fix_tokens()
    results = [(i.value, i.token_type) for i in parser.tokens]
    assert results == expected

@pytest.mark.parametrize("tokens, expected", [
    (gen_tokens("playlists: (artist: ironmouse)"), [("playlists", "scope", [("artist", "fuzz", "ironmouse")])]),
    (gen_tokens("playlists: (artist: ironmouse and songs: (title: 'king*' or title: 'left*'))"), [("playlists", "scope", [("artist", "fuzz", "ironmouse"), (None, "operator", "and"), ("songs", "scope", [("title", "re", "king*"), (None, "operator", "or"), ("title", "re", "left*")])])]),
    (gen_tokens("album: (artist: ironmouse)"), [("playlists", "scope", [("artist", "fuzz", "ironmouse")])])
    ])
def test_get_pair(parser, tokens, expected):
    parser.tokens = tokens
    
    results = get_results(parser._get_pair())
    assert results == expected

@pytest.mark.parametrize("tokens, expected", [
    (gen_tokens("playlists: artist: ironmouse"), [("playlists", "scope", [("artist", "fuzz", "ironmouse")])]),
    (gen_tokens("playlists: (artist: ironmouse and songs: (title: 'king*' or title: 'left*') and artist: shiro beats)"), [("playlists", "scope", [("artist", "fuzz", "ironmouse"), (None, "operator", "and"), ("songs", "scope", [("title", "re", "king*"), (None, "operator", "or"), ("title", "re", "left*")]), (None, "operator", "and"), ("artist", "fuzz", "shiro beats")])]),
    (gen_tokens("()"), [("artist", "scope", [("artist", "fuzz", ")")])]),
    (gen_tokens("ironmouse"), [("artist", "fuzz", "ironmouse")])
    ])
def test_parser(parser, tokens, expected):
    results = get_results([parser.parse(tokens)])
    assert results == expected



