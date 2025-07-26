# Quản lý logic xử lý, nhận câu hỏi, gửi đáp án, update điểm
# Phụ trách: Nguyễn Đức Lượng

import json
import time

from model.player import Player
from model.question import Question
from utils.helpers import format_message


class GameViewModel:
    def __init__(self, socket, player_name, ui):
        self.socket = socket
        self.player_name = player_name
        self.player = Player(name=player_name)
        self.ui = ui
        self.current_question = None
        self.start_time = None

    def send_connect(self):
        msg = format_message("connect", {"player_name": self.player_name})
        self.send(msg)

    def send(self, message: dict):
        try:
            self.socket.sendall((json.dumps(message) + "\n").encode("utf-8"))
        except Exception as e:
            print(f"Lỗi khi gửi dữ liệu: {e}")

    def handle_user_input(self, command: str):
        if command == "join":
            self.send(format_message("join_game", {}))
        elif command == "ready":
            self.send(format_message("ready", {}))
        elif command == "answer":
            if not self.current_question:
                print("⚠️  Không có câu hỏi hiện tại.")
                return
            answer = self.ui.get_answer_input(self.current_question.options)
            answer_time = round(time.time() - self.start_time, 2)
            self.send(format_message("answer", {
                "answer": answer,
                "answer_time": answer_time
            }))
        elif command == "status":
            self.send(format_message("get_status", {}))
        else:
            print("⚠️  Lệnh không hợp lệ.")

    def handle_message(self, message: dict):
        msg_type = message.get("type")

        if msg_type == "connected":
            player_id = message["data"].get("player_id")
            self.player.id = player_id
            print(f"✅ Đã kết nối thành công với ID: {player_id}")

        elif msg_type == "joined_game":
            print("🎮 Đã tham gia phòng chơi.")

        elif msg_type == "ready_status":
            print("✅ Bạn đã sẵn sàng.")

        elif msg_type == "question":
            self.current_question = Question.from_message(message)
            self.start_time = time.time()
            self.ui.display_question(self.current_question)

        elif msg_type == "answer_review":
            self.ui.display_answer_review(message)

        elif msg_type == "game_end":
            self.ui.display_game_end(message)
            self.current_question = None

        elif msg_type == "status":
            self.ui.display_status(message["data"])

        elif msg_type == "error":
            print(f"❌ Lỗi: {message['data'].get('message')}")

        else:
            print(f"(i) Nhận message không xác định: {msg_type}")
