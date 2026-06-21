from enum import Enum, auto

class basic_types(Enum):
    SEP = auto()
    L_OP = auto()
    R_OP = auto()
    WS = auto()
    S_QUOTES = auto()
    D_QUOTES = auto()
    ESC = auto()
    WORD = auto()
    EOF = auto()
    SOF = auto()

class token_types(Enum):
    EOF = auto()
    SOF = auto()
    OP = auto()
    L_OP = auto()
    R_OP = auto()
    TYPE = auto()
    VALUE = auto()
    S_VALUE = auto()

type_keywords = {
        "artist": "artist",
        "title": "title",
        "date": "date",
        "genre": "genre",
        "duration": "duration",

        "playlists": "playlists",
        "playlist": "playlists",
        "album": "playlists",
        "albums": "playlists",
        "shuffle": "shuffled-playlists",

        "songs": "songs",
        "song": "songs",

        "add": "append",
        "add-playlist":  "append-playlist",
        "add-list":  "append-playlist",
        "next": "insert-next",
        "all": "all-matches",
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

defulats = {
        token_types.TYPE: " artist:",
        token_types.L_OP: "(",
        token_types.R_OP: ")",
        token_types.OP: " and ",
        }

valid_syntax_paths = {
        token_types.SOF     : [token_types.TYPE, token_types.L_OP,  token_types.S_VALUE, token_types.EOF, token_types.VALUE], 
        token_types.TYPE    : [token_types.TYPE, token_types.L_OP, token_types.S_VALUE, token_types.VALUE],
        token_types.VALUE   : [token_types.OP, token_types.TYPE, token_types.L_OP, token_types.R_OP, token_types.EOF, token_types.VALUE],
        token_types.S_VALUE : [token_types.OP, token_types.TYPE, token_types.L_OP, token_types.R_OP, token_types.EOF],
        token_types.OP      : [token_types.TYPE, token_types.L_OP],
        token_types.L_OP    : [token_types.TYPE],
        token_types.R_OP    : [token_types.TYPE, token_types.R_OP, token_types.OP, token_types.EOF],
        }

valid_output_paths = {
        token_types.SOF     : [token_types.TYPE, token_types.EOF],
        token_types.TYPE    : [token_types.L_OP, token_types.VALUE, token_types.S_VALUE],
        token_types.VALUE   : [token_types.OP, token_types.R_OP, token_types.EOF],
        token_types.S_VALUE : [token_types.OP, token_types.R_OP,  token_types.EOF],
        token_types.OP      : [token_types.TYPE],
        token_types.L_OP    : [token_types.TYPE, token_types.S_VALUE, token_types.VALUE],
        token_types.R_OP    : [token_types.TYPE, token_types.R_OP, token_types.OP, token_types.EOF],
        }
