from lexer import basic_types
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
