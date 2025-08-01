"""
Module xử lý kết nối mạng cho client
"""

import socket
import json
import time
import threading
import logging
from typing import Optional, Callable, Dict, Any
from client.config import (
    SERVER_HOST, SERVER_PORT, BUFFER_SIZE, ENCODING, DELIMITER,
    RECONNECT_ATTEMPTS, RECONNECT_DELAY, MessageType
)

class NetworkManager:
    """Quản lý kết nối mạng với server"""
    
    def __init__(self):
        self.socket = None
        self.is_connected = False
        self.is_running = False
        self.receive_thread = None
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.message_handlers: Dict[str, Callable] = {}
        self.connection_handlers: Dict[str, Callable] = {}
        
        # Buffer cho message
        self.message_buffer = ""
    
    def connect(self, host: str = SERVER_HOST, port: int = SERVER_PORT) -> bool:
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.is_connected = True
            self.is_running = True
            
            # Khởi động thread nhận message
            self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
            self.receive_thread.start()
            
            self.logger.info(f"Connected to server {host}:{port}")
            self._notify_connection_handlers('connected')
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {e}")
            self._notify_connection_handlers('failed', str(e))
            return False
    
    def disconnect(self):
        """Ngắt kết nối"""
        self.is_running = False
        self.is_connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        self.logger.info("Disconnected from server")
        self._notify_connection_handlers('disconnected')
    
    def send_message(self, message_type: str, data: Dict[str, Any] = None) -> bool:
        """Gửi message đến server"""
        if not self.is_connected or not self.socket:
            self.logger.warning("Not connected to server")
            return False
        
        try:
            message = {
                'type': message_type,
                'data': data or {},
                'timestamp': time.time()
            }
            message_str = json.dumps(message, ensure_ascii=False) + DELIMITER
            self.socket.send(message_str.encode(ENCODING))
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending message: {e}")
            self.disconnect()
            return False
    
    def _receive_loop(self):
        """Vòng lặp nhận message từ server"""
        while self.is_running and self.is_connected:
            try:
                data = self.socket.recv(BUFFER_SIZE)
                if not data:
                    break
                
                message_str = data.decode(ENCODING)
                self.message_buffer += message_str
                
                # Xử lý các message hoàn chỉnh
                while DELIMITER in self.message_buffer:
                    message_end = self.message_buffer.find(DELIMITER)
                    complete_message = self.message_buffer[:message_end]
                    self.message_buffer = self.message_buffer[message_end + len(DELIMITER):]
                    
                    if complete_message.strip():
                        self._process_message(complete_message)
                        
            except Exception as e:
                if self.is_running:
                    self.logger.error(f"Error receiving message: {e}")
                break
        
        self.disconnect()
    
    def _process_message(self, message_str: str):
        """Xử lý message nhận được"""
        try:
            message = json.loads(message_str)
            message_type = message.get('type')
            data = message.get('data', {})
            
            self.logger.debug(f"Received message: {message_type}")
            
            # Gọi handler tương ứng
            if message_type in self.message_handlers:
                self.message_handlers[message_type](data)
            else:
                self.logger.warning(f"No handler for message type: {message_type}")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON message: {e}")
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """Đăng ký handler cho loại message"""
        self.message_handlers[message_type] = handler
    
    def register_connection_handler(self, event: str, handler: Callable):
        """Đăng ký handler cho sự kiện kết nối"""
        self.connection_handlers[event] = handler
    
    def _notify_connection_handlers(self, event: str, *args):
        """Thông báo cho các connection handler"""
        if event in self.connection_handlers:
            try:
                self.connection_handlers[event](*args)
            except Exception as e:
                self.logger.error(f"Error in connection handler: {e}")
    
    def reconnect(self, max_attempts: int = RECONNECT_ATTEMPTS) -> bool:
        """Thử kết nối lại"""
        for attempt in range(max_attempts):
            self.logger.info(f"Reconnection attempt {attempt + 1}/{max_attempts}")
            
            if self.connect():
                return True
            
            if attempt < max_attempts - 1:
                time.sleep(RECONNECT_DELAY)
        
        self.logger.error("Failed to reconnect after all attempts")
        return False
    
    def is_server_available(self, host: str = SERVER_HOST, port: int = SERVER_PORT) -> bool:
        """Kiểm tra server có khả dụng không"""
        try:
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(5)
            result = test_socket.connect_ex((host, port))
            test_socket.close()
            return result == 0
        except:
            return False 