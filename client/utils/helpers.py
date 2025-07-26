# Hàm tiện ích (validate input, format text, ...)
# Phụ trách: Nguyễn Đức Lượng

import time

def format_message(msg_type: str, data: dict, player_id: str = None):
    return {
        "type": msg_type,
        "data": data,
        "timestamp": time.time(),
        "player_id": player_id
    }
