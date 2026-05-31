from unittest.mock import MagicMock, call
import pytest

from sys import path
path.append("src/")
from queryRunner import QueryRunner
from parser import Pair


@pytest.fixture
def mock_root():
    return MagicMock()

@pytest.fixture
def parser(mock_root):
    return QueryRunner(mock_root)

def test_fuzz(parser, mock_root):
    ast = Pair("playlists", "scope", [Pair("title", "fuzz", "left right")])
    parser.run(ast)
    mock_root.fuzz.assert_called_once_with("title", "left right") 

@pytest.mark.parametrize("glob, regex", [
    (r"*iron*", r"^.*iron.*$"),
    (r"*iron?ouse.*", r"^.*iron.ouse\..*$")
    ])
def test_glob_to_regex(parser, glob, regex):
    assert parser._glob_to_regex(glob) == regex

def test_regex(parser, mock_root):
    ast = Pair("playlists", "scope", [Pair("title", "re", "left right")])
    parser.run(ast)
    mock_root.regex.assert_called_once_with("title", parser._glob_to_regex("left right"))

# def test_and(parser, mock_root):
#     song1 = MagicMock()
#     song2 = MagicMock()
#     mock_root.get_songs_batch.side_effect = [song1, song2]
#     ast = Pair("playlists", "scope", [Pair("title", "fuzz", "left right"), Pair(None,"operator","and"), Pair("title", "fuzz", "right left")])
#     parser.run(ast)
#     song1.concat_and.assert_called_once_with(song2) 

def test_or(parser, mock_root):
    song1 = MagicMock()
    song2 = MagicMock()
    mock_root.get_songs_batch.side_effect = [song1, song2]
    ast = Pair("playlists", "scope", [Pair("title", "fuzz", "left right"), Pair(None,"operator","or"), Pair("title", "fuzz", "right left")])
    parser.run(ast)
    song1.concat_or.assert_called_once_with(song2) 

def test_get_playlists(parser, mock_root):
    song1 = MagicMock()
    song2 = MagicMock()
    mock_root.get_songs_batch.side_effect = [song1, song2]
    song1.concat_or.return_value = "correct"
    ast = Pair("playlists", "scope", [Pair("title", "fuzz", "left right"), Pair(None,"operator","or"), Pair("title", "fuzz", "right left")])
    parser.run(ast)
    mock_root.get_playlists.assert_called_once_with("correct")

