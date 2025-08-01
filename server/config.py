"""
Cấu hình server cho Fastest Finger First
"""

# Cấu hình mạng
HOST = 'localhost'
PORT = 5555
MAX_CLIENTS = 10
BUFFER_SIZE = 4096

# Cấu hình game
QUESTION_TIME_LIMIT = 30  # Thời gian trả lời mỗi câu hỏi (giây)
MIN_PLAYERS_TO_START = 2  # Số người chơi tối thiểu để bắt đầu
MAX_QUESTIONS_PER_GAME = 10  # Số câu hỏi tối đa mỗi trận
WAIT_TIME_BETWEEN_QUESTIONS = 3  # Thời gian chờ giữa các câu hỏi

# Cấu hình điểm số
POINTS_FOR_CORRECT_ANSWER = 10
BONUS_POINTS_FOR_SPEED = 5  # Điểm thưởng cho người trả lời nhanh nhất
POINTS_DEDUCTION_FOR_WRONG = 0  # Không trừ điểm cho câu trả lời sai

# Cấu hình database
DATABASE_FILE = 'game_data.db'
LOG_FILE = 'server.log'

# Cấu hình logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Giao thức truyền tin
ENCODING = 'utf-8'
DELIMITER = '\n'

# Trạng thái game
class GameState:
    WAITING = 'waiting'
    PLAYING = 'playing'
    FINISHED = 'finished'

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