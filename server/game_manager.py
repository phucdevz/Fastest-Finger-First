"""
Module quản lý logic game cho Fastest Finger First
Xử lý câu hỏi, tính điểm, quản lý trạng thái game
"""

import json
import time
import random
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .config import (
    GameState, MessageType, QUESTION_TIME_LIMIT, 
    POINTS_FOR_CORRECT_ANSWER, BONUS_POINTS_FOR_SPEED,
    WAIT_TIME_BETWEEN_QUESTIONS, MAX_QUESTIONS_PER_GAME
)
from .database import GameDatabase

class Player:
    """Lớp đại diện cho một người chơi"""
    def __init__(self, username: str, client_socket=None):
        self.username = username
        self.client_socket = client_socket
        self.score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.response_times = []
        self.is_connected = True
        self.last_answer_time = None
    
    def add_response_time(self, response_time: float):
        """Thêm thời gian phản hồi"""
        self.response_times.append(response_time)
    
    def get_average_response_time(self) -> float:
        """Tính thời gian phản hồi trung bình"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def to_dict(self) -> Dict:
        """Chuyển đổi thành dictionary"""
        return {
            'username': self.username,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'average_response_time': self.get_average_response_time()
        }

class Question:
    """Lớp đại diện cho một câu hỏi"""
    def __init__(self, question_text: str, options: List[str], correct_answer: str, 
                 category: str = "general", difficulty: str = "medium"):
        self.question_text = question_text
        self.options = options
        self.correct_answer = correct_answer
        self.category = category
        self.difficulty = difficulty
        self.start_time = None
    
    def to_dict(self) -> Dict:
        """Chuyển đổi thành dictionary"""
        return {
            'question_text': self.question_text,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

class GameManager:
    """Quản lý logic game chính"""
    
    def __init__(self, database: GameDatabase):
        self.database = database
        self.logger = logging.getLogger(__name__)
        
        # Trạng thái game
        self.game_state = GameState.WAITING
        self.players: Dict[str, Player] = {}
        self.current_question: Optional[Question] = None
        self.question_index = 0
        self.questions: List[Question] = []
        self.game_id = None
        
        # Thời gian
        self.question_start_time = None
        self.game_start_time = None
        
        # Kết quả
        self.player_answers = {}
        self.fastest_answer = None
    
    def add_player(self, username: str, client_socket=None) -> bool:
        """Thêm người chơi mới"""
        if username in self.players:
            return False
        
        player = Player(username, client_socket)
        self.players[username] = player
        
        # Thêm vào database
        self.database.add_player(username)
        
        self.logger.info(f"Player {username} joined the game")
        return True
    
    def remove_player(self, username: str):
        """Xóa người chơi"""
        if username in self.players:
            self.players[username].is_connected = False
            self.logger.info(f"Player {username} left the game")
    
    def set_questions(self, questions: List[Question]):
        """Thiết lập danh sách câu hỏi cho game"""
        self.questions = questions
        self.logger.info(f"Set {len(questions)} questions for the game")
    
    def can_start_game(self) -> bool:
        """Kiểm tra có thể bắt đầu game không"""
        connected_players = sum(1 for p in self.players.values() if p.is_connected)
        return connected_players >= 2 and len(self.questions) > 0
    
    def start_game(self) -> bool:
        """Bắt đầu game"""
        if not self.can_start_game():
            return False
        
        self.game_state = GameState.PLAYING
        self.game_start_time = time.time()
        self.question_index = 0
        
        # Tạo game trong database
        self.game_id = self.database.create_game(
            len(self.players), 
            min(len(self.questions), MAX_QUESTIONS_PER_GAME)
        )
        
        self.logger.info(f"Game started with {len(self.players)} players")
        return True
    
    def get_next_question(self) -> Optional[Question]:
        """Lấy câu hỏi tiếp theo"""
        if self.question_index >= len(self.questions) or self.question_index >= MAX_QUESTIONS_PER_GAME:
            return None
        
        self.current_question = self.questions[self.question_index]
        self.question_start_time = time.time()
        self.player_answers = {}
        self.fastest_answer = None
        
        self.logger.info(f"Question {self.question_index + 1}: {self.current_question.question_text}")
        return self.current_question
    
    def submit_answer(self, username: str, answer: str) -> Dict:
        """Xử lý đáp án từ người chơi"""
        if not self.current_question or username not in self.players:
            return {'valid': False, 'message': 'Invalid submission'}
        
        if username in self.player_answers:
            return {'valid': False, 'message': 'Already answered'}
        
        current_time = time.time()
        response_time = current_time - self.question_start_time
        
        # Lưu đáp án
        self.player_answers[username] = {
            'answer': answer,
            'response_time': response_time,
            'timestamp': current_time
        }
        
        # Cập nhật thời gian phản hồi
        self.players[username].add_response_time(response_time)
        self.players[username].last_answer_time = current_time
        
        # Kiểm tra đáp án nhanh nhất
        if self.fastest_answer is None or response_time < self.fastest_answer['response_time']:
            self.fastest_answer = {
                'username': username,
                'response_time': response_time
            }
        
        self.logger.info(f"Player {username} answered in {response_time:.2f}s")
        
        return {
            'valid': True,
            'response_time': response_time,
            'is_fastest': self.fastest_answer['username'] == username
        }
    
    def end_question(self) -> Dict:
        """Kết thúc câu hỏi và tính điểm"""
        if not self.current_question:
            return {}
        
        results = {}
        correct_answers = []
        
        # Tính điểm cho từng người chơi
        for username, answer_data in self.player_answers.items():
            player = self.players[username]
            is_correct = answer_data['answer'].lower() == self.current_question.correct_answer.lower()
            
            points = 0
            if is_correct:
                points = POINTS_FOR_CORRECT_ANSWER
                player.correct_answers += 1
                correct_answers.append(username)
                
                # Điểm thưởng cho người trả lời nhanh nhất
                if self.fastest_answer and self.fastest_answer['username'] == username:
                    points += BONUS_POINTS_FOR_SPEED
            
            player.score += points
            
            results[username] = {
                'answer': answer_data['answer'],
                'correct': is_correct,
                'points': points,
                'response_time': answer_data['response_time'],
                'total_score': player.score
            }
        
        # Lưu kết quả câu hỏi vào database
        if self.game_id:
            self.database.save_question_result(
                self.game_id,
                self.current_question.question_text,
                self.current_question.correct_answer,
                self.player_answers
            )
        
        self.question_index += 1
        self.logger.info(f"Question ended. Correct answers: {len(correct_answers)}")
        
        return results
    
    def is_game_finished(self) -> bool:
        """Kiểm tra game đã kết thúc chưa"""
        return self.question_index >= len(self.questions) or self.question_index >= MAX_QUESTIONS_PER_GAME
    
    def end_game(self) -> Dict:
        """Kết thúc game và trả về kết quả cuối cùng"""
        self.game_state = GameState.FINISHED
        
        # Tìm người thắng
        winner = None
        max_score = -1
        
        for player in self.players.values():
            if player.score > max_score:
                max_score = player.score
                winner = player.username
        
        # Lưu kết quả vào database
        if self.game_id and winner:
            self.database.end_game(self.game_id, winner)
            
            player_results = [player.to_dict() for player in self.players.values()]
            self.database.save_game_result(self.game_id, player_results)
        
        # Tạo kết quả cuối cùng
        final_results = {
            'winner': winner,
            'winner_score': max_score,
            'players': [player.to_dict() for player in self.players.values()],
            'total_questions': self.question_index
        }
        
        self.logger.info(f"Game ended. Winner: {winner} with {max_score} points")
        return final_results
    
    def get_leaderboard(self) -> List[Dict]:
        """Lấy bảng xếp hạng hiện tại"""
        sorted_players = sorted(
            self.players.values(),
            key=lambda p: (p.score, -p.get_average_response_time()),
            reverse=True
        )
        
        leaderboard = []
        for i, player in enumerate(sorted_players, 1):
            leaderboard.append({
                'rank': i,
                'username': player.username,
                'score': player.score,
                'correct_answers': player.correct_answers,
                'average_response_time': player.get_average_response_time()
            })
        
        return leaderboard
    
    def get_game_status(self) -> Dict:
        """Lấy trạng thái hiện tại của game"""
        return {
            'game_state': self.game_state,
            'total_players': len(self.players),
            'connected_players': sum(1 for p in self.players.values() if p.is_connected),
            'current_question': self.question_index + 1 if self.current_question else 0,
            'total_questions': len(self.questions),
            'can_start': self.can_start_game(),
            'is_finished': self.is_game_finished()
        }
    
    def reset_game(self):
        """Reset game về trạng thái ban đầu"""
        self.game_state = GameState.WAITING
        self.current_question = None
        self.question_index = 0
        self.question_start_time = None
        self.game_start_time = None
        self.player_answers = {}
        self.fastest_answer = None
        self.game_id = None
        
        # Reset điểm số người chơi
        for player in self.players.values():
            player.score = 0
            player.correct_answers = 0
            player.wrong_answers = 0
            player.response_times = []
            player.last_answer_time = None
        
        self.logger.info("Game reset to initial state") 