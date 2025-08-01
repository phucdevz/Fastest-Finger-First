"""
Cấu hình client cho Fastest Finger First
"""

# Cấu hình kết nối
SERVER_HOST = 'localhost'
SERVER_PORT = 5555
BUFFER_SIZE = 4096
RECONNECT_ATTEMPTS = 3
RECONNECT_DELAY = 2

# Cấu hình giao diện
UI_TYPE = 'console'  # 'console' hoặc 'gui'
REFRESH_RATE = 0.1  # Tần suất cập nhật UI (giây)

# Cấu hình game
DEFAULT_USERNAME = 'Player'
AUTO_JOIN_ROOM = True

# Giao thức truyền tin
ENCODING = 'utf-8'
DELIMITER = '\n'

# Loại message
class MessageType:
    CONNECT = 'connect'
    DISCONNECT = 'disconnect'
    JOIN_ROOM = 'join_room'
    LEAVE_ROOM = 'leave_room'
    QUESTION = 'question'
    ANSWER = 'answer'
    SCORE_UPDATE = 'score_update'
    LEADERBOARD = 'leaderboard'
    GAME_START = 'game_start'
    GAME_END = 'game_end'
    ERROR = 'error'
    INFO = 'info'

# Trạng thái client
class ClientState:
    DISCONNECTED = 'disconnected'
    CONNECTING = 'connecting'
    CONNECTED = 'connected'
    IN_ROOM = 'in_room'
    PLAYING = 'playing'
    GAME_ENDED = 'game_ended' 