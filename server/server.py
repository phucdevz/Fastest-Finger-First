"""
Server chính cho Fastest Finger First
Xử lý kết nối đa client, quản lý game và giao tiếp realtime
"""

import socket
import threading
import json
import logging
import time
import select
from typing import Dict, List, Optional
from .config import (
    HOST, PORT, BUFFER_SIZE, ENCODING, DELIMITER,
    QUESTION_TIME_LIMIT, WAIT_TIME_BETWEEN_QUESTIONS,
    MessageType, GameState, LOG_LEVEL, LOG_FORMAT, LOG_FILE
)
from .database import GameDatabase
from .game_manager import GameManager, Question

class ClientHandler:
    """Xử lý kết nối từ một client"""
    
    def __init__(self, client_socket: socket.socket, address: tuple, server):
        self.client_socket = client_socket
        self.address = address
        self.server = server
        self.username = None
        self.is_connected = True
        self.logger = logging.getLogger(f"ClientHandler-{address}")
    
    def send_message(self, message_type: str, data: dict = None):
        """Gửi message đến client"""
        try:
            message = {
                'type': message_type,
                'data': data or {},
                'timestamp': time.time()
            }
            message_str = json.dumps(message, ensure_ascii=False) + DELIMITER
            self.client_socket.send(message_str.encode(ENCODING))
        except Exception as e:
            self.logger.error(f"Error sending message to {self.username}: {e}")
            self.disconnect()
    
    def receive_message(self) -> Optional[dict]:
        """Nhận message từ client"""
        try:
            data = self.client_socket.recv(BUFFER_SIZE)
            if not data:
                return None
            
            message_str = data.decode(ENCODING)
            messages = message_str.split(DELIMITER)
            
            for msg in messages:
                if msg.strip():
                    return json.loads(msg)
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message from {self.username}: {e}")
            return None
    
    def handle_message(self, message: dict):
        """Xử lý message từ client"""
        try:
            message_type = message.get('type')
            data = message.get('data', {})
            
            if message_type == MessageType.CONNECT:
                self.handle_connect(data)
            elif message_type == MessageType.JOIN_ROOM:
                self.handle_join_room(data)
            elif message_type == MessageType.ANSWER:
                self.handle_answer(data)
            elif message_type == MessageType.LEAVE_ROOM:
                self.handle_leave_room(data)
            else:
                self.logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            self.logger.error(f"Error handling message: {e}")
            self.send_message(MessageType.ERROR, {'message': 'Internal server error'})
    
    def handle_connect(self, data: dict):
        """Xử lý kết nối client"""
        username = data.get('username')
        if not username:
            self.send_message(MessageType.ERROR, {'message': 'Username is required'})
            return
        
        if self.server.add_client(username, self):
            self.username = username
            self.send_message(MessageType.CONNECT, {
                'success': True,
                'message': f'Welcome {username}!'
            })
            self.logger.info(f"Client {username} connected from {self.address}")
        else:
            self.send_message(MessageType.ERROR, {
                'message': 'Username already exists'
            })
    
    def handle_join_room(self, data: dict):
        """Xử lý tham gia phòng"""
        if not self.username:
            self.send_message(MessageType.ERROR, {'message': 'Not connected'})
            return
        
        if self.server.game_manager.add_player(self.username, self.client_socket):
            self.send_message(MessageType.JOIN_ROOM, {
                'success': True,
                'message': f'Joined room successfully'
            })
            
            # Gửi thông tin phòng hiện tại
            self.send_game_status()
            
            # Thông báo cho các client khác
            self.server.broadcast_to_others(self, MessageType.INFO, {
                'message': f'{self.username} joined the room'
            })
        else:
            self.send_message(MessageType.ERROR, {
                'message': 'Failed to join room'
            })
    
    def handle_answer(self, data: dict):
        """Xử lý đáp án từ client"""
        if not self.username:
            self.send_message(MessageType.ERROR, {'message': 'Not connected'})
            return
        
        answer = data.get('answer')
        if not answer:
            self.send_message(MessageType.ERROR, {'message': 'Answer is required'})
            return
        
        result = self.server.game_manager.submit_answer(self.username, answer)
        if result['valid']:
            self.send_message(MessageType.ANSWER, {
                'success': True,
                'response_time': result['response_time'],
                'is_fastest': result['is_fastest']
            })
            
            # Thông báo cho tất cả client về đáp án
            self.server.broadcast_to_all(MessageType.INFO, {
                'message': f'{self.username} answered in {result["response_time"]:.2f}s'
            })
        else:
            self.send_message(MessageType.ERROR, {
                'message': result['message']
            })
    
    def handle_leave_room(self, data: dict):
        """Xử lý rời phòng"""
        if self.username:
            self.server.game_manager.remove_player(self.username)
            self.server.broadcast_to_others(self, MessageType.INFO, {
                'message': f'{self.username} left the room'
            })
    
    def send_game_status(self):
        """Gửi trạng thái game hiện tại"""
        status = self.server.game_manager.get_game_status()
        self.send_message(MessageType.INFO, {
            'game_status': status,
            'leaderboard': self.server.game_manager.get_leaderboard()
        })
    
    def disconnect(self):
        """Ngắt kết nối client"""
        if self.username:
            self.server.remove_client(self.username)
            self.server.game_manager.remove_player(self.username)
        
        self.is_connected = False
        try:
            self.client_socket.close()
        except:
            pass
        
        self.logger.info(f"Client {self.username} disconnected")

class GameServer:
    """Server chính quản lý game"""
    
    def __init__(self, host: str = HOST, port: int = PORT):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients: Dict[str, ClientHandler] = {}
        self.client_threads: List[threading.Thread] = []
        
        # Khởi tạo database và game manager
        self.database = GameDatabase()
        self.game_manager = GameManager(self.database)
        
        # Thread quản lý game
        self.game_thread = None
        self.running = False
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """Thiết lập logging"""
        logging.basicConfig(
            level=getattr(logging, LOG_LEVEL),
            format=LOG_FORMAT,
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    def start(self):
        """Khởi động server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.logger.info(f"Server started on {self.host}:{self.port}")
            
            # Khởi động thread quản lý game
            self.game_thread = threading.Thread(target=self.game_loop, daemon=True)
            self.game_thread.start()
            
            # Vòng lặp chính nhận kết nối
            self.accept_connections()
            
        except Exception as e:
            self.logger.error(f"Error starting server: {e}")
            self.stop()
    
    def accept_connections(self):
        """Chấp nhận kết nối từ client"""
        while self.running:
            try:
                client_socket, address = self.server_socket.accept()
                self.logger.info(f"New connection from {address}")
                
                # Tạo handler cho client mới
                client_handler = ClientHandler(client_socket, address, self)
                
                # Tạo thread xử lý client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_handler,),
                    daemon=True
                )
                client_thread.start()
                self.client_threads.append(client_thread)
                
            except Exception as e:
                if self.running:
                    self.logger.error(f"Error accepting connection: {e}")
    
    def handle_client(self, client_handler: ClientHandler):
        """Xử lý client trong thread riêng"""
        while client_handler.is_connected and self.running:
            try:
                message = client_handler.receive_message()
                if message:
                    client_handler.handle_message(message)
                else:
                    break
            except Exception as e:
                self.logger.error(f"Error handling client {client_handler.username}: {e}")
                break
        
        client_handler.disconnect()
    
    def add_client(self, username: str, client_handler: ClientHandler) -> bool:
        """Thêm client mới"""
        if username in self.clients:
            return False
        
        self.clients[username] = client_handler
        return True
    
    def remove_client(self, username: str):
        """Xóa client"""
        if username in self.clients:
            del self.clients[username]
    
    def broadcast_to_all(self, message_type: str, data: dict):
        """Gửi message đến tất cả client"""
        for client in self.clients.values():
            if client.is_connected:
                client.send_message(message_type, data)
    
    def broadcast_to_others(self, sender: ClientHandler, message_type: str, data: dict):
        """Gửi message đến tất cả client trừ sender"""
        for client in self.clients.values():
            if client.is_connected and client != sender:
                client.send_message(message_type, data)
    
    def game_loop(self):
        """Vòng lặp quản lý game"""
        while self.running:
            try:
                # Kiểm tra có thể bắt đầu game không
                if (self.game_manager.game_state == GameState.WAITING and 
                    self.game_manager.can_start_game()):
                    self.start_game()
                
                # Xử lý game đang chạy
                elif self.game_manager.game_state == GameState.PLAYING:
                    self.run_game_round()
                
                # Kiểm tra kết thúc game
                elif (self.game_manager.game_state == GameState.PLAYING and 
                      self.game_manager.is_game_finished()):
                    self.end_game()
                
                time.sleep(1)  # Sleep 1 giây
                
            except Exception as e:
                self.logger.error(f"Error in game loop: {e}")
                time.sleep(1)
    
    def start_game(self):
        """Bắt đầu game"""
        if self.game_manager.start_game():
            self.logger.info("Game started")
            self.broadcast_to_all(MessageType.GAME_START, {
                'message': 'Game started!',
                'total_players': len(self.game_manager.players)
            })
    
    def run_game_round(self):
        """Chạy một vòng game"""
        # Lấy câu hỏi tiếp theo
        if not self.game_manager.current_question:
            question = self.game_manager.get_next_question()
            if question:
                self.send_question(question)
            else:
                return
        
        # Kiểm tra thời gian câu hỏi
        if (time.time() - self.game_manager.question_start_time >= 
            QUESTION_TIME_LIMIT):
            self.end_question()
    
    def send_question(self, question: Question):
        """Gửi câu hỏi đến tất cả client"""
        question_data = question.to_dict()
        question_data['question_number'] = self.game_manager.question_index + 1
        question_data['time_limit'] = QUESTION_TIME_LIMIT
        
        self.broadcast_to_all(MessageType.QUESTION, question_data)
        self.logger.info(f"Sent question {self.game_manager.question_index + 1}")
    
    def end_question(self):
        """Kết thúc câu hỏi"""
        results = self.game_manager.end_question()
        
        # Gửi kết quả đến tất cả client
        self.broadcast_to_all(MessageType.SCORE_UPDATE, {
            'results': results,
            'leaderboard': self.game_manager.get_leaderboard()
        })
        
        # Chờ một chút trước câu hỏi tiếp theo
        time.sleep(WAIT_TIME_BETWEEN_QUESTIONS)
    
    def end_game(self):
        """Kết thúc game"""
        final_results = self.game_manager.end_game()
        
        self.broadcast_to_all(MessageType.GAME_END, {
            'final_results': final_results,
            'leaderboard': self.game_manager.get_leaderboard()
        })
        
        self.logger.info("Game ended")
        
        # Reset game sau một thời gian
        threading.Timer(10.0, self.game_manager.reset_game).start()
    
    def stop(self):
        """Dừng server"""
        self.running = False
        
        # Đóng tất cả client
        for client in self.clients.values():
            client.disconnect()
        
        # Đóng server socket
        if self.server_socket:
            self.server_socket.close()
        
        self.logger.info("Server stopped")

def main():
    """Hàm main để chạy server"""
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()

if __name__ == "__main__":
    main() 