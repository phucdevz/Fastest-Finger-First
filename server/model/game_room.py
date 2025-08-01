import threading
import time
import json
from datetime import datetime

class GameRoom:
    def __init__(self, room_id, config, question_manager):
        self.room_id = room_id
        self.config = config
        self.question_manager = question_manager
        self.players = []
        self.status = 'waiting'  # waiting, playing, finished
        self.current_question = None
        self.question_start_time = None
        self.question_timer = None
        self.game_thread = None
        self.ready_count = 0
        self.max_players = config['server']['max_players']
        self.question_time = config['server']['question_time']
        self.questions_per_round = config['game']['questions_per_round']
        self.current_question_index = 0
        self.questions = []
        
    def add_player(self, player):
        """Thêm player vào phòng"""
        if len(self.players) >= self.max_players:
            return False
            
        if self.status != 'waiting':
            return False
            
        self.players.append(player)
        return True
    
    def remove_player(self, player):
        """Xóa player khỏi phòng"""
        if player in self.players:
            self.players.remove(player)
            
            # Nếu không còn player nào, dừng game
            if len(self.players) == 0:
                self.stop_game()
    
    def player_ready(self, player):
        """Player báo sẵn sàng"""
        if player in self.players:
            player.set_ready(True)
            self.ready_count += 1
            
            # Kiểm tra nếu tất cả player đã sẵn sàng
            if self.ready_count >= len(self.players) and len(self.players) >= 2:
                self.start_game()
    
    def start_game(self):
        """Bắt đầu game"""
        if self.status != 'waiting':
            return
            
        self.status = 'playing'
        self.current_question_index = 0
        self.questions = self.question_manager.get_random_questions(self.questions_per_round)
        
        # Thông báo bắt đầu game
        self._broadcast_message({
            'type': 'GAME_START',
            'total_questions': len(self.questions),
            'players': self.get_players_info()
        })
        
        # Bắt đầu thread game
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
    
    def _game_loop(self):
        """Vòng lặp game chính"""
        for i, question in enumerate(self.questions):
            if self.status != 'playing':
                break
                
            self.current_question = question
            self.current_question_index = i
            self.question_start_time = time.time()
            
            # Gửi câu hỏi
            self._send_question(question)
            
            # Chờ thời gian trả lời
            time.sleep(self.question_time)
            
            # Hiển thị kết quả
            self._show_results()
            
            # Chờ một chút trước câu hỏi tiếp theo
            time.sleep(2)
        
        # Kết thúc game
        self._end_game()
    
    def _send_question(self, question):
        """Gửi câu hỏi đến tất cả player"""
        message = {
            'type': 'QUESTION',
            'question_id': question['id'],
            'question': question['question'],
            'options': question['options'],
            'time_limit': self.question_time,
            'question_number': self.current_question_index + 1,
            'total_questions': len(self.questions)
        }
        
        self._broadcast_message(message)
        
        # Bắt đầu timer
        self.question_timer = threading.Timer(self.question_time, self._timeout_question)
        self.question_timer.start()
    
    def _timeout_question(self):
        """Xử lý timeout câu hỏi"""
        if self.current_question:
            # Gửi thông báo timeout
            self._broadcast_message({
                'type': 'QUESTION_TIMEOUT',
                'question_id': self.current_question['id']
            })
    
    def process_answer(self, player, answer, answer_time):
        """Xử lý câu trả lời từ player"""
        if not self.current_question or self.status != 'playing':
            return
            
        # Tính thời gian trả lời
        response_time = answer_time - self.question_start_time
        
        # Kiểm tra đáp án đúng
        is_correct = answer == self.current_question['correct_answer']
        
        # Tính điểm
        points = self._calculate_points(is_correct, response_time)
        
        # Cập nhật player
        player.add_answer(
            self.current_question['id'],
            answer,
            is_correct,
            response_time,
            points
        )
        
        # Gửi thông báo cập nhật điểm
        self._broadcast_message({
            'type': 'SCORE_UPDATE',
            'player_name': player.name,
            'score': player.score,
            'points_earned': points,
            'is_correct': is_correct
        })
    
    def _calculate_points(self, is_correct, response_time):
        """Tính điểm dựa trên độ chính xác và tốc độ"""
        if not is_correct:
            return 0
            
        base_points = self.config['game']['points_per_correct']
        bonus_points = self.config['game']['bonus_points_fast']
        
        # Bonus điểm cho trả lời nhanh
        if response_time < 5:  # Trả lời trong 5 giây đầu
            return base_points + bonus_points
        elif response_time < 10:  # Trả lời trong 10 giây đầu
            return base_points + (bonus_points // 2)
        else:
            return base_points
    
    def _show_results(self):
        """Hiển thị kết quả câu hỏi"""
        if not self.current_question:
            return
            
        # Dừng timer
        if self.question_timer:
            self.question_timer.cancel()
        
        # Gửi kết quả
        self._broadcast_message({
            'type': 'QUESTION_RESULT',
            'question_id': self.current_question['id'],
            'correct_answer': self.current_question['correct_answer'],
            'leaderboard': self.get_leaderboard()
        })
    
    def _end_game(self):
        """Kết thúc game"""
        self.status = 'finished'
        
        # Tính toán kết quả cuối cùng
        final_results = self.get_final_results()
        
        # Gửi kết quả cuối
        self._broadcast_message({
            'type': 'GAME_END',
            'final_results': final_results,
            'leaderboard': self.get_leaderboard()
        })
    
    def stop_game(self):
        """Dừng game"""
        self.status = 'finished'
        if self.question_timer:
            self.question_timer.cancel()
    
    def get_players_info(self):
        """Lấy thông tin tất cả player"""
        return [player.get_info() for player in self.players]
    
    def get_leaderboard(self):
        """Lấy bảng xếp hạng"""
        sorted_players = sorted(self.players, key=lambda p: p.score, reverse=True)
        leaderboard = []
        
        for i, player in enumerate(sorted_players):
            leaderboard.append({
                'rank': i + 1,
                'name': player.name,
                'score': player.score
            })
        
        return leaderboard
    
    def get_final_results(self):
        """Lấy kết quả cuối cùng"""
        results = []
        for player in self.players:
            stats = player.get_stats()
            results.append({
                'name': player.name,
                'final_score': player.score,
                'correct_answers': stats['correct_answers'],
                'total_answers': stats['total_answers'],
                'accuracy': stats['accuracy']
            })
        
        return sorted(results, key=lambda x: x['final_score'], reverse=True)
    
    def get_status(self):
        """Lấy trạng thái phòng"""
        return {
            'room_id': self.room_id,
            'status': self.status,
            'player_count': len(self.players),
            'max_players': self.max_players,
            'ready_count': self.ready_count
        }
    
    def _broadcast_message(self, message):
        """Gửi message đến tất cả player trong phòng"""
        for player in self.players:
            try:
                data = json.dumps(message).encode('utf-8')
                player.socket.send(data)
            except Exception as e:
                print(f"Error sending message to {player.name}: {e}")
    
    def _send_message(self, player, message):
        """Gửi message đến một player cụ thể"""
        try:
            data = json.dumps(message).encode('utf-8')
            player.socket.send(data)
        except Exception as e:
            print(f"Error sending message to {player.name}: {e}") 