from sys import path
path.append("src/")

from parser import Parser
from string import printable

def test_Parser():
    parser = Parser()
    string = 'songs: artist: "*iron*"  title :Arent we all teh worst | title : \'Left*\'' 

    first = parser._first_pass(string) 
    expected = ["songs", ":", " ", "artist", ":", " ", '"*iron*"', " ", " ", "title", " ", ":", "Arent", " ", "we", " ", "all", " ", "teh", " ", "worst", " ", "|", " ","title", " ", ":", ' ', "'Left*'"]
    assert first == expected

    secound = parser._secound_pass(first) 
    expected = [{"key": "songs"}, {"key": "artist"}, {"value": '"*iron*"'}, {"key": "title"}, {"value": "Arent we all teh worst"}, {"operator": "|"}, {"key": "title"}, {"value": "'Left*'"}]
    assert secound == expected

    third = parser._third_pass(secound)
    expected = [{"key": "songs"}, {"pair": {"key":"artist", "re": "*iron*"}}, {"pair": {"key": "title", "fuzz": "Arent we all teh worst"}}, {"operator": "|"}, {"pair": {"key": "title", "re": "Left*"}} ]
    assert third == expected

    result = parser._final_pass(third)
    expected = {r"results": r"songs", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}, r"or", {r"key": r"title", r"re": "Left*"}]}
    assert result == expected

    string = 'songs : artist : "*iron*" title : Arent we all teh worst|title : \'Left*\'' 
    result = parser.parse(string)
    expected = {r"results": r"songs", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}, r"or", {r"key": r"title", r"re": "Left*"}]}
    assert result == expected

    string = 'artist:"*iron*" title:Arent we all teh worst|title:\'Left*\'' 
    result = parser.parse(string)
    expected = {r"results": r"playlists", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}, r"or", {r"key": r"title", r"re": "Left*"}]}
    assert result == expected

    string = 'artist        :        "*iron*"       title     :     Arent we all teh worst    |      title:     \'Left*\'' 
    result = parser.parse(string)
    expected = {r"results": r"playlists", r"query": [{r"key": r"artist", r"re": "*iron*"}, r"and", {r"key": r"title", r"fuzz": r"Arent we all teh worst"}, r"or", {r"key": r"title", r"re": "Left*"}]}
    assert result == expected

