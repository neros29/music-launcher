
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

