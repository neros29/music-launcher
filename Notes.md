
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

### QUERY 
One pass system. I compile the ast into one instruction i run on every single song. This includes fuzzing, and glob for specific proeprtys. Basicly for each instruction in the ast you creat that same instruction but made for a single songs, in a way were i only have to go through every song once to cheack each indivule song against the criteria. I also think instead of storing the song i will store the path to the song. I am basicly treating the path of the song as the hash of the song. This allows me to have a O(1) lookup while not storing multple vertsion of the song in memory or having to copy each song to a new data type. This means a song will become just a wrapper of that hash were when it has to check the main data structer for the song it's self. 

As for how i will acitly store the data i think it makes sense to store the data as a list with operters. This would be like [{"function_to_call": ["arg1", "arg2"]}, "and", {"function_to_call": ["arg1", "arg2"]}]
This would then in the query function look like going through each song and calling the function or just executing the code on the arguments provided. Basicly each function returns true or false, and then you use boolen operaters to find weather the song matches. This makes it realy easy to add a new thing as you just add a new function to the querying engine, and then add a new key word.

### TODO
I should make the parser return defualt for defualt inteasd of having it guess for defults as the querying engine will be much better at guessing. Also it should set scope keys to None if there is not key defined for the scope. Basicly serpate concerns the data base query worryas about defualt cases, and the parser just parsers. This will allow for much more intelgenct choices when it comes to defualts. 

[
    {'func': 'self', 'key': 'songs', 'value': 
    [
        {'func': 'self', 'key': 'songs', 'value': 
        [
            {'func': 'fuzz', 'key': 'artist', 'value': 'ironmouse', 'op': None}, 
            {'func': 'fuzz', 'key': 'artist', 'value': 'shirobeats', 'op': 'or'}
        ], 'op': None}, 
        {'func': 'self', 'key': 'artist', 'value': 
        [
            {'func': 're', 'key': 'title', 'value': 'king*', 'op': None}, 
            {'func': 're', 'key': 'title', 'value': 'show off*', 'op': 'or'}
        ],'op': 'and'}
    ]
    , 'op': None}
]

