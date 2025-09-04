"""
Base class cho UI interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class UIBase(ABC):
    """Base class cho tất cả UI interface"""
    
    def __init__(self, view_model):
        self.view_model = view_model
        self.running = False
    
    @abstractmethod
    def start(self):
        """Khởi động UI"""
        pass
    
    @abstractmethod
    def stop(self):
        """Dừng UI"""
        pass
    
    @abstractmethod
    def update(self):
        """Cập nhật UI"""
        pass
    
    @abstractmethod
    def on_state_changed(self, new_state: str):
        """Xử lý thay đổi trạng thái"""
        pass
    
    @abstractmethod
    def on_question_received(self, question_data: dict):
        """Xử lý nhận câu hỏi"""
        pass
    
    @abstractmethod
    def on_score_updated(self, results: dict):
        """Xử lý cập nhật điểm"""
        pass
    
    @abstractmethod
    def on_leaderboard_updated(self, leaderboard: list):
        """Xử lý cập nhật bảng xếp hạng"""
        pass
    
    @abstractmethod
    def on_game_started(self, data: dict):
        """Xử lý bắt đầu game"""
        pass
    
    @abstractmethod
    def on_game_ended(self, final_results: dict):
        """Xử lý kết thúc game"""
        pass
    
    @abstractmethod
    def on_error_occurred(self, error_message: str):
        """Xử lý lỗi"""
        pass
    
    @abstractmethod
    def on_info_received(self, info_message: str):
        """Xử lý thông tin"""
        pass
    
    def display_question(self, question_data: dict):
        """Hiển thị câu hỏi"""
        pass
    
    def display_leaderboard(self, leaderboard: list):
        """Hiển thị bảng xếp hạng"""
        pass
    
    def display_game_status(self, status: dict):
        """Hiển thị trạng thái game"""
        pass
    
    def display_final_results(self, results: dict):
        """Hiển thị kết quả cuối cùng"""
        pass
    
    def get_user_input(self, prompt: str = "") -> str:
        """Lấy input từ người dùng"""
        pass
    
    def show_message(self, message: str, message_type: str = "info"):
        """Hiển thị thông báo"""
        pass 

