"""
Client chính cho Fastest Finger First
Kết hợp ViewModel và UI để tạo ứng dụng hoàn chỉnh
"""

import sys
import logging
import threading
import time
import os
from pathlib import Path
from typing import Optional

# Add the project root to Python path for proper imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from client.view_model import GameViewModel
from client.config import UI_TYPE, REFRESH_RATE

class GameClient:
    """Client chính quản lý game"""
    
    def __init__(self, ui_type: str = UI_TYPE):
        self.view_model = GameViewModel()
        self.ui_type = ui_type
        self.ui = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        
        # Thiết lập logging
        self._setup_logging()
        
        # Khởi tạo UI
        self._init_ui()
        
        # Đăng ký callbacks
        self._register_callbacks()
    
    def _setup_logging(self):
        """Thiết lập logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _init_ui(self):
        """Khởi tạo UI"""
        try:
            if self.ui_type == 'gui':
                from ui.gui_ui import GUIInterface
                self.ui = GUIInterface(self.view_model)
            else:
                from ui.console_ui import ConsoleInterface
                self.ui = ConsoleInterface(self.view_model)
            
            self.logger.info(f"Initialized {self.ui_type} interface")
            
        except ImportError as e:
            self.logger.error(f"Failed to import UI module: {e}")
            # Fallback to console UI
            try:
                from ui.console_ui import ConsoleInterface
                self.ui = ConsoleInterface(self.view_model)
                self.ui_type = 'console'
                self.logger.info("Falling back to console interface")
            except ImportError:
                self.logger.error("No UI interface available")
                sys.exit(1)
    
    def _register_callbacks(self):
        """Đăng ký các callback cho UI"""
        self.view_model.register_ui_callback('state_changed', self._on_state_changed)
        self.view_model.register_ui_callback('question_received', self._on_question_received)
        self.view_model.register_ui_callback('score_updated', self._on_score_updated)
        self.view_model.register_ui_callback('leaderboard_updated', self._on_leaderboard_updated)
        self.view_model.register_ui_callback('game_started', self._on_game_started)
        self.view_model.register_ui_callback('game_ended', self._on_game_ended)
        self.view_model.register_ui_callback('error_occurred', self._on_error_occurred)
        self.view_model.register_ui_callback('info_received', self._on_info_received)
    
    def start(self, username: str = None):
        """Khởi động client"""
        self.running = True
        
        try:
            # Kết nối đến server
            if not self.view_model.connect_to_server(username):
                self.logger.error("Failed to connect to server")
                return False
            
            # Khởi động UI
            if self.ui:
                self.ui.start()
            
            # Vòng lặp chính
            self._main_loop()
            
        except KeyboardInterrupt:
            self.logger.info("Client interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
        finally:
            self.stop()
        
        return True
    
    def stop(self):
        """Dừng client"""
        self.running = False
        
        if self.ui:
            self.ui.stop()
        
        self.view_model.disconnect_from_server()
        self.logger.info("Client stopped")
    
    def _main_loop(self):
        """Vòng lặp chính của client"""
        while self.running:
            try:
                # Cập nhật UI
                if self.ui:
                    self.ui.update()
                
                # Kiểm tra kết nối
                if not self.view_model.is_connected():
                    self.logger.warning("Lost connection to server")
                    if not self.view_model.network.reconnect():
                        self.logger.error("Failed to reconnect")
                        break
                
                time.sleep(REFRESH_RATE)
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    
    # UI Callbacks
    def _on_state_changed(self, new_state: str):
        """Xử lý thay đổi trạng thái"""
        self.logger.info(f"State changed to: {new_state}")
        if self.ui:
            self.ui.on_state_changed(new_state)
    
    def _on_question_received(self, question_data: dict):
        """Xử lý nhận câu hỏi"""
        self.logger.info("Received new question")
        if self.ui:
            self.ui.on_question_received(question_data)
    
    def _on_score_updated(self, results: dict):
        """Xử lý cập nhật điểm"""
        self.logger.info("Score updated")
        if self.ui:
            self.ui.on_score_updated(results)
    
    def _on_leaderboard_updated(self, leaderboard: list):
        """Xử lý cập nhật bảng xếp hạng"""
        if self.ui:
            self.ui.on_leaderboard_updated(leaderboard)
    
    def _on_game_started(self, data: dict):
        """Xử lý bắt đầu game"""
        self.logger.info("Game started")
        if self.ui:
            self.ui.on_game_started(data)
    
    def _on_game_ended(self, final_results: dict):
        """Xử lý kết thúc game"""
        self.logger.info("Game ended")
        if self.ui:
            self.ui.on_game_ended(final_results)
    
    def _on_error_occurred(self, error_message: str):
        """Xử lý lỗi"""
        self.logger.error(f"Error: {error_message}")
        if self.ui:
            self.ui.on_error_occurred(error_message)
    
    def _on_info_received(self, info_message: str):
        """Xử lý thông tin"""
        self.logger.info(f"Info: {info_message}")
        if self.ui:
            self.ui.on_info_received(info_message)

def main():
    """Hàm main để chạy client"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fastest Finger First Client')
    parser.add_argument('--username', '-u', type=str, help='Username for the game')
    parser.add_argument('--ui', type=str, choices=['console', 'gui'], 
                       default=UI_TYPE, help='UI type to use')
    parser.add_argument('--host', type=str, default='localhost', 
                       help='Server host')
    parser.add_argument('--port', type=int, default=5555, 
                       help='Server port')
    
    args = parser.parse_args()
    
    # Cập nhật cấu hình
    import client.config as client_config
    client_config.SERVER_HOST = args.host
    client_config.SERVER_PORT = args.port
    
    # Tạo và chạy client
    client = GameClient(ui_type=args.ui)
    
    try:
        client.start(username=args.username)
    except KeyboardInterrupt:
        print("\nShutting down client...")
        client.stop()

if __name__ == "__main__":
    main() 