"""
Test cho server Fastest Finger First
"""

import unittest
import sys
import os
import time
import threading
from pathlib import Path

# Thêm thư mục gốc vào path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.game_manager import GameManager, Question, Player
from server.database import GameDatabase

class TestGameManager(unittest.TestCase):
    """Test cho GameManager"""
    
    def setUp(self):
        """Thiết lập test"""
        self.database = GameDatabase(":memory:")  # Sử dụng database trong bộ nhớ
        self.game_manager = GameManager(self.database)
        
        # Tạo câu hỏi test
        self.test_questions = [
            Question("1 + 1 = ?", ["1", "2", "3", "4"], "B", "math", "easy"),
            Question("Thủ đô Việt Nam?", ["Hà Nội", "TP.HCM", "Đà Nẵng", "Huế"], "A", "geography", "easy")
        ]
        self.game_manager.set_questions(self.test_questions)
    
    def test_add_player(self):
        """Test thêm người chơi"""
        # Test thêm người chơi thành công
        result = self.game_manager.add_player("Player1")
        self.assertTrue(result)
        self.assertIn("Player1", self.game_manager.players)
        
        # Test thêm người chơi trùng tên
        result = self.game_manager.add_player("Player1")
        self.assertFalse(result)
    
    def test_remove_player(self):
        """Test xóa người chơi"""
        self.game_manager.add_player("Player1")
        self.game_manager.remove_player("Player1")
        self.assertFalse(self.game_manager.players["Player1"].is_connected)
    
    def test_can_start_game(self):
        """Test kiểm tra có thể bắt đầu game"""
        # Chưa đủ người chơi
        self.assertFalse(self.game_manager.can_start_game())
        
        # Thêm đủ người chơi
        self.game_manager.add_player("Player1")
        self.game_manager.add_player("Player2")
        self.assertTrue(self.game_manager.can_start_game())
    
    def test_start_game(self):
        """Test bắt đầu game"""
        self.game_manager.add_player("Player1")
        self.game_manager.add_player("Player2")
        
        result = self.game_manager.start_game()
        self.assertTrue(result)
        self.assertEqual(self.game_manager.game_state, "playing")
    
    def test_submit_answer(self):
        """Test gửi đáp án"""
        self.game_manager.add_player("Player1")
        self.game_manager.add_player("Player2")
        self.game_manager.start_game()
        self.game_manager.get_next_question()
        
        # Test gửi đáp án hợp lệ
        result = self.game_manager.submit_answer("Player1", "A")
        self.assertTrue(result['valid'])
        
        # Test gửi đáp án trùng
        result = self.game_manager.submit_answer("Player1", "B")
        self.assertFalse(result['valid'])
    
    def test_end_question(self):
        """Test kết thúc câu hỏi"""
        self.game_manager.add_player("Player1")
        self.game_manager.add_player("Player2")
        self.game_manager.start_game()
        self.game_manager.get_next_question()
        
        # Gửi đáp án
        self.game_manager.submit_answer("Player1", "A")
        self.game_manager.submit_answer("Player2", "B")
        
        # Kết thúc câu hỏi
        results = self.game_manager.end_question()
        self.assertIn("Player1", results)
        self.assertIn("Player2", results)
    
    def test_leaderboard(self):
        """Test bảng xếp hạng"""
        self.game_manager.add_player("Player1")
        self.game_manager.add_player("Player2")
        self.game_manager.start_game()
        self.game_manager.get_next_question()
        
        # Gửi đáp án
        self.game_manager.submit_answer("Player1", "A")
        self.game_manager.submit_answer("Player2", "B")
        self.game_manager.end_question()
        
        leaderboard = self.game_manager.get_leaderboard()
        self.assertEqual(len(leaderboard), 2)
    
    def test_game_status(self):
        """Test trạng thái game"""
        status = self.game_manager.get_game_status()
        self.assertIn('game_state', status)
        self.assertIn('total_players', status)
        self.assertIn('connected_players', status)

class TestDatabase(unittest.TestCase):
    """Test cho Database"""
    
    def setUp(self):
        """Thiết lập test"""
        self.database = GameDatabase(":memory:")
    
    def test_add_player(self):
        """Test thêm người chơi vào database"""
        result = self.database.add_player("TestPlayer")
        self.assertTrue(result)
        
        # Test thêm trùng
        result = self.database.add_player("TestPlayer")
        self.assertFalse(result)
    
    def test_get_player_stats(self):
        """Test lấy thống kê người chơi"""
        self.database.add_player("TestPlayer")
        stats = self.database.get_player_stats("TestPlayer")
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['username'], "TestPlayer")
        self.assertEqual(stats['total_games'], 0)
    
    def test_create_game(self):
        """Test tạo game"""
        game_id = self.database.create_game(2, 10)
        self.assertGreater(game_id, 0)
    
    def test_leaderboard(self):
        """Test bảng xếp hạng"""
        # Thêm một số người chơi
        self.database.add_player("Player1")
        self.database.add_player("Player2")
        self.database.add_player("Player3")
        
        leaderboard = self.database.get_leaderboard()
        self.assertEqual(len(leaderboard), 3)

if __name__ == '__main__':
    unittest.main() 