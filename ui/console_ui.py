"""
Console UI cho Fastest Finger First
Giao diện console đẹp và dễ sử dụng
"""

import os
import sys
import time
import threading
from typing import Optional
from ui.ui_base import UIBase
from client.config import ClientState

class ConsoleInterface(UIBase):
    """Giao diện console cho game"""
    
    def __init__(self, view_model):
        super().__init__(view_model)
        self.input_thread = None
        self.user_input = ""
        self.input_ready = threading.Event()
        self.current_question = None
        self.leaderboard = []
        self.game_status = {}
        self.messages = []
        
        # Colors for console (ANSI escape codes)
        self.colors = {
            'reset': '\033[0m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'underline': '\033[4m'
        }
    
    def start(self):
        """Khởi động console UI"""
        self.running = True
        
        # Hiển thị welcome screen
        self.show_welcome_screen()
        
        # Khởi động input thread
        self.input_thread = threading.Thread(target=self._input_loop, daemon=True)
        self.input_thread.start()
        
        print(f"{self.colors['green']}Console UI started{self.colors['reset']}")
        print(f"{self.colors['yellow']}Type 'connect' to connect to server{self.colors['reset']}")
        print()
    
    def stop(self):
        """Dừng console UI"""
        self.running = False
        if self.input_thread:
            self.input_thread.join(timeout=1)
        print(f"\n{self.colors['yellow']}Console UI stopped{self.colors['reset']}")
    
    def update(self):
        """Cập nhật console UI"""
        if not self.running:
            return
        
        # Chỉ cập nhật khi có thay đổi thực sự
        # Không clear screen liên tục để tránh gián đoạn input
        pass
    
    def clear_screen(self):
        """Xóa màn hình"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_welcome_screen(self):
        """Hiển thị màn hình chào mừng"""
        self.clear_screen()
        print(f"{self.colors['cyan']}{'='*60}")
        print(f"{self.colors['bold']}    FASTEST FINGER FIRST - CONSOLE CLIENT")
        print(f"{self.colors['reset']}{'='*60}")
        print(f"{self.colors['yellow']}Welcome to the fastest finger first game!")
        print(f"Connect to server and start playing...{self.colors['reset']}")
        print()
    
    def draw_interface(self):
        """Vẽ giao diện chính"""
        # Header
        self.draw_header()
        
        # Main content area
        self.draw_main_content()
        
        # Footer
        self.draw_footer()
        
        # Input area
        self.draw_input_area()
    
    def draw_header(self):
        """Vẽ header"""
        state = self.view_model.get_state()
        username = self.view_model.get_username()
        
        print(f"{self.colors['cyan']}{'='*60}")
        print(f"Player: {self.colors['bold']}{username}{self.colors['reset']} | "
              f"State: {self.get_state_color(state)}{state}{self.colors['reset']}")
        print(f"{'='*60}{self.colors['reset']}")
    
    def draw_main_content(self):
        """Vẽ nội dung chính"""
        state = self.view_model.get_state()
        
        if state == ClientState.DISCONNECTED:
            self.draw_disconnected_screen()
        elif state == ClientState.CONNECTING:
            self.draw_connecting_screen()
        elif state == ClientState.CONNECTED:
            self.draw_connected_screen()
        elif state == ClientState.IN_ROOM:
            self.draw_room_screen()
        elif state == ClientState.PLAYING:
            self.draw_game_screen()
        elif state == ClientState.GAME_ENDED:
            self.draw_game_end_screen()
    
    def draw_disconnected_screen(self):
        """Vẽ màn hình ngắt kết nối"""
        print(f"{self.colors['red']}❌ Disconnected from server{self.colors['reset']}")
        print(f"{self.colors['yellow']}Type 'connect' to connect to server{self.colors['reset']}")
        print()
    
    def draw_connecting_screen(self):
        """Vẽ màn hình đang kết nối"""
        print(f"{self.colors['yellow']}🔄 Connecting to server...{self.colors['reset']}")
        print()
    
    def draw_connected_screen(self):
        """Vẽ màn hình đã kết nối"""
        print(f"{self.colors['green']}✅ Connected to server{self.colors['reset']}")
        print(f"{self.colors['yellow']}Type 'join' to join a room{self.colors['reset']}")
        print()
    
    def draw_room_screen(self):
        """Vẽ màn hình trong phòng"""
        print(f"{self.colors['green']}🏠 In game room{self.colors['reset']}")
        print(f"{self.colors['yellow']}Waiting for other players...{self.colors['reset']}")
        print()
        
        # Hiển thị bảng xếp hạng
        if self.leaderboard:
            self.display_leaderboard(self.leaderboard)
    
    def draw_game_screen(self):
        """Vẽ màn hình game"""
        if self.current_question:
            self.display_question(self.current_question)
        
        # Hiển thị bảng xếp hạng
        if self.leaderboard:
            self.display_leaderboard(self.leaderboard)
    
    def draw_game_end_screen(self):
        """Vẽ màn hình kết thúc game"""
        if self.view_model.get_final_results():
            self.display_final_results(self.view_model.get_final_results())
    
    def draw_footer(self):
        """Vẽ footer"""
        print(f"{self.colors['cyan']}{'='*60}")
        print(f"Commands: connect, join, leave, quit{self.colors['reset']}")
        print()
    
    def draw_input_area(self):
        """Vẽ vùng input"""
        # Không hiển thị prompt ở đây vì đã được xử lý trong _input_loop
        pass
    
    def get_state_color(self, state: str) -> str:
        """Lấy màu cho trạng thái"""
        colors = {
            ClientState.DISCONNECTED: self.colors['red'],
            ClientState.CONNECTING: self.colors['yellow'],
            ClientState.CONNECTED: self.colors['green'],
            ClientState.IN_ROOM: self.colors['blue'],
            ClientState.PLAYING: self.colors['magenta'],
            ClientState.GAME_ENDED: self.colors['cyan']
        }
        return colors.get(state, self.colors['white'])
    
    def display_question(self, question_data: dict):
        """Hiển thị câu hỏi"""
        print(f"{self.colors['bold']}{'='*50}")
        print(f"QUESTION {question_data.get('question_number', '?')}")
        print(f"{'='*50}{self.colors['reset']}")
        print(f"{self.colors['white']}{question_data.get('question_text', '')}{self.colors['reset']}")
        print()
        
        # Hiển thị các lựa chọn
        options = question_data.get('options', [])
        for i, option in enumerate(options, 1):
            print(f"{self.colors['yellow']}{i}. {option}{self.colors['reset']}")
        
        print()
        print(f"{self.colors['green']}Type your answer (A, B, C, D or 1, 2, 3, 4):{self.colors['reset']}")
        print()
    
    def display_leaderboard(self, leaderboard: list):
        """Hiển thị bảng xếp hạng"""
        if not leaderboard:
            return
        
        print(f"{self.colors['bold']}{'='*30}")
        print(f"LEADERBOARD")
        print(f"{'='*30}{self.colors['reset']}")
        
        for i, player in enumerate(leaderboard[:10], 1):
            rank_color = self.colors['yellow'] if i == 1 else self.colors['white']
            print(f"{rank_color}{i:2d}. {player['username']:<15} {player['score']:>5} pts{self.colors['reset']}")
        
        print()
    
    def display_final_results(self, results: dict):
        """Hiển thị kết quả cuối cùng"""
        print(f"{self.colors['bold']}{'='*50}")
        print(f"GAME ENDED")
        print(f"{'='*50}{self.colors['reset']}")
        
        winner = results.get('winner', 'Unknown')
        winner_score = results.get('winner_score', 0)
        
        print(f"{self.colors['yellow']}🏆 Winner: {winner} ({winner_score} points){self.colors['reset']}")
        print()
        
        # Hiển thị kết quả tất cả người chơi
        players = results.get('players', [])
        for player in players:
            color = self.colors['yellow'] if player['username'] == winner else self.colors['white']
            print(f"{color}{player['username']}: {player['score']} points "
                  f"({player['correct_answers']} correct, {player['wrong_answers']} wrong){self.colors['reset']}")
        
        print()
    
    def _input_loop(self):
        """Vòng lặp xử lý input"""
        while self.running:
            try:
                # Hiển thị prompt và đợi input
                print(f"{self.colors['green']}>>> {self.colors['reset']}", end='', flush=True)
                user_input = input().strip()
                if user_input:
                    self.process_command(user_input)
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                print(f"Input error: {e}")
    
    def process_command(self, command: str):
        """Xử lý lệnh từ người dùng"""
        command = command.lower()
        state = self.view_model.get_state()
        
        if command == 'quit' or command == 'exit':
            self.running = False
            return
        
        elif command == 'connect':
            if state == ClientState.DISCONNECTED:
                self.view_model.connect_to_server()
            else:
                self.show_message("Already connected or connecting", "warning")
        
        elif command == 'join':
            if state == ClientState.CONNECTED:
                self.view_model.join_room()
            else:
                self.show_message("Must be connected to join room", "warning")
        
        elif command == 'leave':
            if state in [ClientState.IN_ROOM, ClientState.PLAYING]:
                self.view_model.leave_room()
            else:
                self.show_message("Not in a room", "warning")
        
        elif state == ClientState.PLAYING and self.current_question:
            # Xử lý đáp án
            self.process_answer(command)
        
        else:
            self.show_message(f"Unknown command: {command}", "warning")
    
    def process_answer(self, answer: str):
        """Xử lý đáp án từ người dùng"""
        if not self.current_question:
            return
        
        # Chuyển đổi đáp án
        answer_map = {
            '1': 'A', '2': 'B', '3': 'C', '4': 'D',
            'a': 'A', 'b': 'B', 'c': 'C', 'd': 'D'
        }
        
        processed_answer = answer_map.get(answer, answer.upper())
        
        if processed_answer in ['A', 'B', 'C', 'D']:
            self.view_model.submit_answer(processed_answer)
            self.show_message(f"Submitted answer: {processed_answer}", "info")
        else:
            self.show_message("Invalid answer. Use A, B, C, D or 1, 2, 3, 4", "warning")
    
    def show_message(self, message: str, message_type: str = "info"):
        """Hiển thị thông báo"""
        colors = {
            'info': self.colors['blue'],
            'warning': self.colors['yellow'],
            'error': self.colors['red'],
            'success': self.colors['green']
        }
        
        color = colors.get(message_type, self.colors['white'])
        print(f"{color}[{message_type.upper()}] {message}{self.colors['reset']}")
    
    # UI Event Handlers
    def on_state_changed(self, new_state: str):
        """Xử lý thay đổi trạng thái"""
        # Chỉ hiển thị thông báo, không clear screen
        self.show_message(f"State changed to: {new_state}", "info")
    
    def on_question_received(self, question_data: dict):
        """Xử lý nhận câu hỏi"""
        self.current_question = question_data
        # Clear screen và hiển thị câu hỏi mới
        self.clear_screen()
        self.draw_interface()
    
    def on_score_updated(self, results: dict):
        """Xử lý cập nhật điểm"""
        # Chỉ hiển thị thông báo
        self.show_message("Score updated!", "success")
    
    def on_leaderboard_updated(self, leaderboard: list):
        """Xử lý cập nhật bảng xếp hạng"""
        self.leaderboard = leaderboard
        # Clear screen và vẽ lại để hiển thị leaderboard mới
        self.clear_screen()
        self.draw_interface()
    
    def on_game_started(self, data: dict):
        """Xử lý bắt đầu game"""
        self.show_message("Game started!", "success")
        self.clear_screen()
        self.draw_interface()
    
    def on_game_ended(self, final_results: dict):
        """Xử lý kết thúc game"""
        self.show_message("Game ended!", "info")
        self.clear_screen()
        self.draw_interface()
    
    def on_error_occurred(self, error_message: str):
        """Xử lý lỗi"""
        self.show_message(error_message, "error")
    
    def on_info_received(self, info_message: str):
        """Xử lý thông tin"""
        self.show_message(info_message, "info") 