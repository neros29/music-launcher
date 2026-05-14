
### MpvCommand
    mpv --input-ipc-server=/tmp/mpv --idle=yes --player-operation-mode=pseudo-gui
### Mpv client ipc
    get verstion of running server: '/tmp/mpv' '{"command":["get_version"]}'
    add song to playlist: '{"command":["loadfile", "/home/neros/Music/Soren/Pop/Album - Mouse Birthday Concert/A special thanks from mousey.mp3", "append"]}'
    replace playlist: '{"command":["loadfile", "/home/neros/Music/Soren/Pop/Album - Mouse Birthday Concert/A special thanks from mousey.mp3", "replace"]}'
