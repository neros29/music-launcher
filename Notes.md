
### MpvCommand
    mpv --input-ipc-server=/tmp/mpv --idle=yes --player-operation-mode=pseudo-gui
### Mpv client ipc
    get verstion of running server: '/tmp/mpv' '{"command":["get_version"]}'
    add song to playlist: '{"command":["loadfile", "/home/neros/Music/Soren/Pop/Album - Mouse Birthday Concert/A special thanks from mousey.mp3", "append"]}'
    replace playlist: '{"command":["loadfile", "/home/neros/Music/Soren/Pop/Album - Mouse Birthday Concert/A special thanks from mousey.mp3", "replace"]}'

### Brainstorm
I need three diffrent descripter keyword things. One to say what you want to recive menaing do you want a single, an album, a playlist, the secound thing is what you are searching for meaning are you searching by artist are you searching by album, are you seraching by song. Then the third is the value the value is what you are acutle searching. a tree would look kind of like this
type [key: value, key:value] as a key value pair are alwasy 1:1 while there can be as many key: value pairs to search for a type.

### TODO
make Playlist sort corectly based on query.
make parser autmaticly add a key if none exists
figure out why artist: nihm isent working.
get m3u files loading correctly.


### TODAY
refactor parser to be better for input.

### Lexer Rules:
type: a word in the type_keywords dict with any ammount of white spaces and a : following it eg, <type_keyword><ws*><":">
op: a word in the op_keywords dict with any ammont of white spaces and a type eg, <op_keyword><ws*><type_keyword><ws*><":">
value: everything that dose not match an op or type

### Parseing Rules:
A scope is any code that must be evaluated to return the value. A scope can be defined using a scopein and scopeout operater. Scope operaters are treated identicly to regular operaters in the lexing faze.
An implicit scope is created, when, A key is defined with anouther key word as it's value. The scope includes the secound defined key, and goes until you reach eather the end file or end of parent scope.
an implicit scope looks like this <op_keyword><ws*><":"><ws*><op_keyword><ws*><":">
an implicit scope is also created with the SOF as the scopein operater and EOF as teh scope out operater however this scope has no return type.
scopes created with the defualt ( and ) operater do not need a return type and the return type will be implictly evaluated to the defualt type.

### Genral Laungege
the laungege has 4 parts. 
1. return type: a key or return type is used to define what a value is searched in or what type a scope returns.
2. operater: an operater is used inside a scope to define how to seprate return values are concatinated.
3. value: A value is eather a scope that will be executed, or the value to be searched for.
4. scope: A list of key value pairs seprated by operaters that will be executed to find the value of the return type.
example syntax: playlists: artist: ironmouse and (title: "left right*" or title: king)
in this example we start with playlists: this is a return type and defines what the syntax as a whole will return.
The artist that follows also being evaluated as a key will be put inside an implicit scope with the return value of that implicit scope being playlist and the end of that scope being directly ebfore the EOF
the 3rd word in this is a value, a value is defined as anything after a key and before an operater or key, this means that ironmouse is the value and artist is the key. So the first value of this scope would be every song that has the artist name ironmouse.
the next word is and which is evaluated as an operater it is defined as the concatiantion methoud between teh currently genrated all songs with the artis as ironmouse and the results of the scope to it's right.
the next block is a scope this scope includes two key value pairs seprated by an or operater. This scope will be executed on it's own and the and concated with the artist: ironmouse key value pair.

# Definitions
everythhing in quotes is what the the value of the identifier.
If two things conflict the own defined last overwrites the first.

### identifiers
SOF = 1 before the begining of the file
EOF = 1 after the file.
EOS = the end of the scope
SEP = key value seprator
STR = a value surounded by quotes
WORDS = any sequence of any printable character
WS = one or more white space characters
WS* = zero or more white spaces characters

TYPE = WS + (<type_keyword> + WS* + SEP)
S_OP = WS + (<s_op>) + WS + [TYPE | EOF]
OP = WS + (<op_keyword>) + WS + [TYPE | S_OP]

T_VALUE = [TYPE | SOF] + WS + (STR) + [TYPE | OP | S_OP | EOF]
VALUE = [TYPE | SOF] + WS + (WORDS) + WS +[TYPE | OP | S_OP | EOF]

FILE = (SOF + [TYPE + [SCOPE | VALUE | T_VALUE]]* | VALUE | T_VALUE] + EOF)
### virtual
PAIR = TYPE + WS* + VALUE
SCOPE = [TYPE | NONE] + S_OP + ([PAIR + OP]*) + S_OP
GLOBAL_SCOPE = SOF + WORDS + EOF

### Syntax
SOF     -> [TYPE | S_OP | T_VALUE | VALUE  | EOF]
TYPE    -> [TYPE | s_OP | T_VALUE | VALUE ]
VALUE   -> [OP | TYPE | S_OP | EOF]
T_VALUE -> [OP | TYPE | s_OP | EOF]
OP      -> [TYPE | s_OP]
S_OP    -> [TYPE | VALUE | T_VALUE]

### AST GENERATOR
[OP, TYPE, s_OP, T_VALUE, VALUE, EOF]
SOF -> [TYPE | EOF] 
TYPE -> [s_OP | VALUE | T_VALUE]
VALUE -> [OP | S_OP | EOF]
T_VALUE -> [OP | S_OP | EOF]
OP -> [TYPE]
S_OP -> [TYPE]

### TOKEN
start_index = tuple
virtual = bool
token_value = str
token_type = [OP | L_OP | R_OP | TYPE | VALUE | S_VALUE]
basic_type = [WORD | WS | SYMBOL]
__add__
__eq__

start_index says the string index of the start of the value it is a tuple were the first value is the index and the secound is the token at that index. This means if there are virtual tokens then they are just counted up in the secound index of the tuple.
virtual is a boolen value telling weather the token is virtual or real.

### TOKENS
data = []
append(token)
insert(token)
next()
prev()
__getitem__
__setitem__
__iter__

split_pass adds basic_type, lex_pass addes token_type, valididate_pass adds virtual functions, pars_pass creates ast.

# TODAY
valididate_pass adds virtual functions,
pares_pass creates ast.

playlists: artist: title (title: left right or title: king)

"" = SOF, "playlists" = WORD, ":" = SEP, " " = WS, "artist" = WORD, ":" = SEP, " " = WS, "title" = WORD, " " = WS, "(" = L_OP, "title" = WORD, ":" = SEP, " " = WS, "left" = WORD, " " = WS, "right" = WORD, " " = WS, "or" = WORD, " " = WS, "title" = WORD, ":" = SEP, " " = WS, "king" = WORD, ")" = R_OP, "" = EOF

ITER = 0
results.append(BUFF) results = [SOF]
CHECK = ITER
GUESS = TYPE
ITER ++
BUFF = "playlists"
ITER ++
BUFF += ":"
results.append(BUFF) results = [SOF, ("playlists:", TYPE)]
CHECK = ITER
GUESS = TYPE
ITER ++
BUFF = " "
ITER ++
BUFF += "artist"
ITER ++
BUFF += ":"
results.append(BUFF) results = [SOF, ("playlists:", TYPE), (" artist:", TYPE)]
CHECK = ITER
GUESS = TYPE
ITER ++
BUFF = " "
ITER ++
BUFF += "title"
ITER ++
BUFF += " "
ITER ++
GUESS = L_OP
ITER = CHECK
ITER ++
BUFF = " "
ITER ++
GUESS = T_VALUE
ITER = CHECK
ITER ++
BUFF = " "
ITER ++
GUESS = VALUE
ITER = CHECK
ITER ++
BUFF = " "
ITER ++
results.append(BUFF) results = [SOF, ("playlists:", TYPE), (" artist:", TYPE), (" (", L_OP)]
CHECK = ITER
GUESS = TYPE
ITER ++
BUFF = "title"
ITER ++
BUFF += ":"
results.append(BUFF) results = [SOF, ("playlists:", TYPE), (" artist:", TYPE), (" (", L_OP), ("title:", TYPE)]
CHECK = ITER
GUESS = TYPE
ITER ++
BUFF = " "
ITER ++
ITER = CHECK
GUESS = L_OP
ITER ++
BUFF = " "
ITER ++
ITER = CHECK
GUESS = S_VALUE
ITER ++
buff = " "
ITER ++
ITER = CHECK
GUESS = VALUE
ITER ++
BUFF = " "
ITER ++
BUFF += "left"







