import time
from datetime import datetime

class Player:
    def __init__(self, name, socket, address):
        self.name = name
        self.socket = socket
        self.address = address
        self.score = 0
        self.ready = False
        self.answers = []
        self.join_time = time.time()
        self.last_activity = time.time()
        
    def update_activity(self):
        """Cập nhật thời gian hoạt động cuối"""
        self.last_activity = time.time()
    
    def add_answer(self, question_id, answer, is_correct, answer_time, points_earned):
        """Thêm câu trả lời của player"""
        answer_data = {
            'question_id': question_id,
            'answer': answer,
            'is_correct': is_correct,
            'answer_time': answer_time,
            'points_earned': points_earned,
            'timestamp': datetime.now().isoformat()
        }
        self.answers.append(answer_data)
        self.score += points_earned
        self.update_activity()
    
    def set_ready(self, ready=True):
        """Đặt trạng thái sẵn sàng"""
        self.ready = ready
        self.update_activity()
    
    def get_info(self):
        """Lấy thông tin player"""
        return {
            'name': self.name,
            'score': self.score,
            'ready': self.ready,
            'answers_count': len(self.answers)
        }
    
    def get_stats(self):
        """Lấy thống kê player"""
        correct_answers = sum(1 for answer in self.answers if answer['is_correct'])
        total_answers = len(self.answers)
        
        return {
            'name': self.name,
            'score': self.score,
            'correct_answers': correct_answers,
            'total_answers': total_answers,
            'accuracy': (correct_answers / total_answers * 100) if total_answers > 0 else 0,
            'join_time': self.join_time,
            'last_activity': self.last_activity
        }
    
    def is_active(self, timeout=300):
        """Kiểm tra player có còn hoạt động không"""
        return (time.time() - self.last_activity) < timeout 