from parser import Pair, Parser
from lexer import Lexer
from dbQuery import Query
from queryRunner import QueryRunner
from query import Query as Q

#TODO Move this to dbquery making this into a single function. And make it able to return playlists, as well as return the return type string eg "playlists", "songs", "all"

class Compile:
    def __init__(self) -> None:
        pass

    def compile(self, ast: Pair):
        return self._compile(ast)

    def _compile(self, ast: Pair, op = None):
        if ast.data_type != "scope":
            return [{"func": ast.data_type, "key": ast.key, "value": ast.data, "op": op}]
        op = op
        results = []
        for pair in reversed(ast.data):
            if pair.data_type == "operator":
                op = pair.data
            else:
                results += self._compile(pair, op)
        print(ast.key)
        return results


if __name__ == "__main__":
    lex = Lexer()
    par = Parser()
    comp = Compile()
    q = Q("data/db.json")
    qr = QueryRunner(q)
    que = Query("data/db.json")
    string = 'playlists: artist: ironmouse and (title: "king*" or title: "*right")'
    tokens = lex.lex(string)
    ast = par.parse(tokens)

    asm = comp.compile(ast)
    # print(asm[0])
    results = que.query_db(asm)
    print(string)
    print(ast)
    print(asm)
    for i in results:
        print(i.get("title"))



