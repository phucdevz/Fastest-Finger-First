import socket
import threading
import json
import time
import random
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.model.game_room import GameRoom
from server.model.player import Player
from server.utils.config_loader import ConfigLoader
from server.utils.question_manager import QuestionManager
from server.utils.logger import Logger

class GameServer:
    def __init__(self):
        self.config = ConfigLoader.load_config()
        self.logger = Logger()
        self.question_manager = QuestionManager()
        self.rooms = {}
        self.players = {}
        self.server_socket = None
        self.running = False
        
    def start(self):
        """Khởi động server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.config['server']['host'], self.config['server']['port']))
            self.server_socket.listen(10)
            
            self.running = True
            self.logger.info(f"Server started on {self.config['server']['host']}:{self.config['server']['port']}")
            
            # Start cleanup thread
            cleanup_thread = threading.Thread(target=self._cleanup_rooms, daemon=True)
            cleanup_thread.start()
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    self.logger.info(f"New connection from {address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except Exception as e:
                    self.logger.error(f"Error accepting connection: {e}")
                    
        except Exception as e:
            self.logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket, address):
        """Xử lý kết nối từ client"""
        try:
            while self.running:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                message = json.loads(data.decode('utf-8'))
                self._process_message(client_socket, message, address)
                
        except Exception as e:
            self.logger.error(f"Error handling client {address}: {e}")
        finally:
            self._disconnect_client(client_socket, address)
    
    def _process_message(self, client_socket, message, address):
        """Xử lý message từ client"""
        try:
            msg_type = message.get('type')
            
            if msg_type == 'JOIN_ROOM':
                self._handle_join_room(client_socket, message, address)
            elif msg_type == 'ANSWER':
                self._handle_answer(client_socket, message, address)
            elif msg_type == 'READY':
                self._handle_ready(client_socket, message, address)
            elif msg_type == 'DISCONNECT':
                self._handle_disconnect(client_socket, message, address)
            else:
                self.logger.warning(f"Unknown message type: {msg_type}")
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def _handle_join_room(self, client_socket, message, address):
        """Xử lý yêu cầu tham gia phòng"""
        player_name = message.get('player_name', f'Player_{address[1]}')
        room_id = message.get('room_id', 'default')
        
        # Tạo hoặc tham gia phòng
        if room_id not in self.rooms:
            self.rooms[room_id] = GameRoom(room_id, self.config, self.question_manager)
        
        room = self.rooms[room_id]
        
        # Tạo player mới
        player = Player(player_name, client_socket, address)
        self.players[address] = player
        
        # Thêm player vào phòng
        success = room.add_player(player)
        
        if success:
            response = {
                'type': 'JOIN_SUCCESS',
                'room_id': room_id,
                'players': room.get_players_info(),
                'status': room.get_status()
            }
            self._send_message(client_socket, response)
            
            # Thông báo cho các player khác
            self._broadcast_to_room(room_id, {
                'type': 'PLAYER_JOINED',
                'player_name': player_name,
                'players': room.get_players_info()
            }, exclude_address=address)
            
        else:
            response = {
                'type': 'JOIN_FAILED',
                'message': 'Room is full or game in progress'
            }
            self._send_message(client_socket, response)
    
    def _handle_answer(self, client_socket, message, address):
        """Xử lý câu trả lời từ player"""
        player = self.players.get(address)
        if not player:
            return
            
        room_id = message.get('room_id')
        answer = message.get('answer')
        answer_time = message.get('answer_time', time.time())
        
        if room_id in self.rooms:
            room = self.rooms[room_id]
            room.process_answer(player, answer, answer_time)
    
    def _handle_ready(self, client_socket, message, address):
        """Xử lý player sẵn sàng"""
        player = self.players.get(address)
        if not player:
            return
            
        room_id = message.get('room_id')
        if room_id in self.rooms:
            room = self.rooms[room_id]
            room.player_ready(player)
    
    def _handle_disconnect(self, client_socket, message, address):
        """Xử lý ngắt kết nối"""
        self._disconnect_client(client_socket, address)
    
    def _disconnect_client(self, client_socket, address):
        """Xử lý ngắt kết nối client"""
        try:
            player = self.players.get(address)
            if player:
                # Xóa player khỏi phòng
                for room in self.rooms.values():
                    room.remove_player(player)
                
                del self.players[address]
            
            client_socket.close()
            self.logger.info(f"Client {address} disconnected")
            
        except Exception as e:
            self.logger.error(f"Error disconnecting client {address}: {e}")
    
    def _send_message(self, client_socket, message):
        """Gửi message đến client"""
        try:
            data = json.dumps(message).encode('utf-8')
            client_socket.send(data)
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
    
    def _broadcast_to_room(self, room_id, message, exclude_address=None):
        """Gửi message đến tất cả player trong phòng"""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            for player in room.players:
                if exclude_address is None or player.address != exclude_address:
                    self._send_message(player.socket, message)
    
    def _cleanup_rooms(self):
        """Dọn dẹp phòng trống"""
        while self.running:
            time.sleep(30)  # Check every 30 seconds
            empty_rooms = []
            for room_id, room in self.rooms.items():
                if len(room.players) == 0:
                    empty_rooms.append(room_id)
            
            for room_id in empty_rooms:
                del self.rooms[room_id]
                self.logger.info(f"Removed empty room: {room_id}")
    
    def stop(self):
        """Dừng server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        self.logger.info("Server stopped")

if __name__ == "__main__":
    server = GameServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop() 