import socket
import threading
import json
import time
from datetime import datetime
from typing import Callable, List, Dict, Any

class GameViewModel:
    def __init__(self, config):
        self.config = config
        self.socket = None
        self.connected = False
        self.player_name = ""
        self.room_id = "default"
        self.current_question = None
        self.score = 0
        self.players = []
        self.leaderboard = []
        self.game_status = "disconnected"  # disconnected, connecting, waiting, playing, finished
        
        # Callbacks for UI updates
        self.on_connection_changed: Callable[[bool], None] = None
        self.on_question_received: Callable[[Dict], None] = None
        self.on_score_updated: Callable[[int], None] = None
        self.on_players_updated: Callable[[List], None] = None
        self.on_leaderboard_updated: Callable[[List], None] = None
        self.on_game_status_changed: Callable[[str], None] = None
        self.on_message_received: Callable[[str], None] = None
        
        # Thread for receiving messages
        self.receive_thread = None
        
    def connect_to_server(self, player_name: str, room_id: str = "default") -> bool:
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.config['client']['host'], self.config['client']['port']))
            
            self.player_name = player_name
            self.room_id = room_id
            self.connected = True
            self.game_status = "connecting"
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()
            
            # Send join room message
            self._send_message({
                'type': 'JOIN_ROOM',
                'player_name': player_name,
                'room_id': room_id
            })
            
            self._update_connection_status()
            return True
            
        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.connected = False
            self._update_connection_status()
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        try:
            if self.socket:
                self._send_message({
                    'type': 'DISCONNECT',
                    'player_name': self.player_name,
                    'room_id': self.room_id
                })
                self.socket.close()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        finally:
            self.connected = False
            self.game_status = "disconnected"
            self._update_connection_status()
    
    def send_answer(self, answer: int):
        """Gửi câu trả lời"""
        if not self.connected or not self.current_question:
            return
            
        try:
            self._send_message({
                'type': 'ANSWER',
                'room_id': self.room_id,
                'answer': answer,
                'answer_time': time.time()
            })
        except Exception as e:
            print(f"Error sending answer: {e}")
    
    def send_ready(self):
        """Gửi tín hiệu sẵn sàng"""
        if not self.connected:
            return
            
        try:
            self._send_message({
                'type': 'READY',
                'room_id': self.room_id
            })
        except Exception as e:
            print(f"Error sending ready: {e}")
    
    def _receive_messages(self):
        """Nhận messages từ server"""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                message = json.loads(data.decode('utf-8'))
                self._process_message(message)
                
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        # Connection lost
        self.connected = False
        self.game_status = "disconnected"
        self._update_connection_status()
    
    def _process_message(self, message: Dict[str, Any]):
        """Xử lý message từ server"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'JOIN_SUCCESS':
                self._handle_join_success(message)
            elif msg_type == 'JOIN_FAILED':
                self._handle_join_failed(message)
            elif msg_type == 'PLAYER_JOINED':
                self._handle_player_joined(message)
            elif msg_type == 'GAME_START':
                self._handle_game_start(message)
            elif msg_type == 'QUESTION':
                self._handle_question(message)
            elif msg_type == 'QUESTION_RESULT':
                self._handle_question_result(message)
            elif msg_type == 'SCORE_UPDATE':
                self._handle_score_update(message)
            elif msg_type == 'GAME_END':
                self._handle_game_end(message)
            elif msg_type == 'QUESTION_TIMEOUT':
                self._handle_question_timeout(message)
            else:
                print(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            print(f"Error processing message: {e}")
    
    def _handle_join_success(self, message):
        """Xử lý tham gia phòng thành công"""
        self.game_status = "waiting"
        self.players = message.get('players', [])
        self._update_game_status()
        self._update_players()
        
        if self.on_message_received:
            self.on_message_received("Tham gia phòng thành công!")
    
    def _handle_join_failed(self, message):
        """Xử lý tham gia phòng thất bại"""
        self.game_status = "disconnected"
        self._update_game_status()
        
        if self.on_message_received:
            self.on_message_received(f"Tham gia phòng thất bại: {message.get('message', '')}")
    
    def _handle_player_joined(self, message):
        """Xử lý player mới tham gia"""
        self.players = message.get('players', [])
        self._update_players()
        
        player_name = message.get('player_name', '')
        if self.on_message_received:
            self.on_message_received(f"{player_name} đã tham gia phòng!")
    
    def _handle_game_start(self, message):
        """Xử lý bắt đầu game"""
        self.game_status = "playing"
        self.score = 0
        self._update_game_status()
        self._update_score()
        
        if self.on_message_received:
            self.on_message_received("Game bắt đầu!")
    
    def _handle_question(self, message):
        """Xử lý nhận câu hỏi"""
        self.current_question = {
            'id': message.get('question_id'),
            'question': message.get('question'),
            'options': message.get('options'),
            'time_limit': message.get('time_limit'),
            'question_number': message.get('question_number'),
            'total_questions': message.get('total_questions')
        }
        
        if self.on_question_received:
            self.on_question_received(self.current_question)
    
    def _handle_question_result(self, message):
        """Xử lý kết quả câu hỏi"""
        self.current_question = None
        self.leaderboard = message.get('leaderboard', [])
        self._update_leaderboard()
        
        correct_answer = message.get('correct_answer')
        if self.on_message_received:
            self.on_message_received(f"Đáp án đúng: {correct_answer + 1}")
    
    def _handle_score_update(self, message):
        """Xử lý cập nhật điểm"""
        player_name = message.get('player_name')
        points_earned = message.get('points_earned', 0)
        is_correct = message.get('is_correct', False)
        
        if player_name == self.player_name:
            self.score += points_earned
            self._update_score()
        
        if self.on_message_received:
            status = "đúng" if is_correct else "sai"
            self.on_message_received(f"{player_name}: {status} (+{points_earned} điểm)")
    
    def _handle_game_end(self, message):
        """Xử lý kết thúc game"""
        self.game_status = "finished"
        self.current_question = None
        self.leaderboard = message.get('leaderboard', [])
        self._update_game_status()
        self._update_leaderboard()
        
        if self.on_message_received:
            self.on_message_received("Game kết thúc!")
    
    def _handle_question_timeout(self, message):
        """Xử lý timeout câu hỏi"""
        self.current_question = None
        if self.on_message_received:
            self.on_message_received("Hết thời gian!")
    
    def _send_message(self, message: Dict[str, Any]):
        """Gửi message đến server"""
        if self.socket and self.connected:
            try:
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
            except Exception as e:
                print(f"Error sending message: {e}")
    
    def _update_connection_status(self):
        """Cập nhật trạng thái kết nối"""
        if self.on_connection_changed:
            self.on_connection_changed(self.connected)
    
    def _update_game_status(self):
        """Cập nhật trạng thái game"""
        if self.on_game_status_changed:
            self.on_game_status_changed(self.game_status)
    
    def _update_score(self):
        """Cập nhật điểm số"""
        if self.on_score_updated:
            self.on_score_updated(self.score)
    
    def _update_players(self):
        """Cập nhật danh sách player"""
        if self.on_players_updated:
            self.on_players_updated(self.players)
    
    def _update_leaderboard(self):
        """Cập nhật bảng xếp hạng"""
        if self.on_leaderboard_updated:
            self.on_leaderboard_updated(self.leaderboard)
    
    # Getters for UI
    def get_player_name(self) -> str:
        return self.player_name
    
    def get_room_id(self) -> str:
        return self.room_id
    
    def get_score(self) -> int:
        return self.score
    
    def get_players(self) -> List[Dict]:
        return self.players
    
    def get_leaderboard(self) -> List[Dict]:
        return self.leaderboard
    
    def get_game_status(self) -> str:
        return self.game_status
    
    def is_connected(self) -> bool:
        return self.connected
    
    def get_current_question(self) -> Dict:
        return self.current_question 