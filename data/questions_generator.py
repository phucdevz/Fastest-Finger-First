"""
Module tạo câu hỏi tự động cho Fastest Finger First
Tạo câu hỏi toán học, logic và các chủ đề khác
"""

import random
import json
from typing import List, Dict
from server.game_manager import Question

class QuestionGenerator:
    """Tạo câu hỏi tự động"""
    
    def __init__(self):
        self.math_operators = ['+', '-', '*', '/']
        self.categories = ['math', 'logic', 'general', 'science']
    
    def generate_math_question(self, difficulty: str = 'medium') -> Question:
        """Tạo câu hỏi toán học"""
        if difficulty == 'easy':
            return self._generate_easy_math()
        elif difficulty == 'medium':
            return self._generate_medium_math()
        else:
            return self._generate_hard_math()
    
    def _generate_easy_math(self) -> Question:
        """Tạo câu hỏi toán học dễ"""
        a = random.randint(1, 20)
        b = random.randint(1, 20)
        operator = random.choice(['+', '-', '*'])
        
        if operator == '+':
            result = a + b
            question_text = f"{a} + {b} = ?"
        elif operator == '-':
            result = a - b
            question_text = f"{a} - {b} = ?"
        else:  # *
            result = a * b
            question_text = f"{a} × {b} = ?"
        
        # Tạo các lựa chọn
        options = [str(result)]
        while len(options) < 4:
            wrong_answer = result + random.randint(-5, 5)
            if wrong_answer != result and str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(str(result)))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="math",
            difficulty="easy"
        )
    
    def _generate_medium_math(self) -> Question:
        """Tạo câu hỏi toán học trung bình"""
        a = random.randint(10, 50)
        b = random.randint(2, 15)
        operator = random.choice(['*', '/', '+'])
        
        if operator == '*':
            result = a * b
            question_text = f"{a} × {b} = ?"
        elif operator == '/':
            result = a // b
            question_text = f"{a} ÷ {b} = ?"
        else:  # +
            result = a + b
            question_text = f"{a} + {b} = ?"
        
        # Tạo các lựa chọn
        options = [str(result)]
        while len(options) < 4:
            if operator == '/':
                wrong_answer = result + random.randint(-2, 2)
            else:
                wrong_answer = result + random.randint(-10, 10)
            
            if wrong_answer != result and str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(str(result)))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="math",
            difficulty="medium"
        )
    
    def _generate_hard_math(self) -> Question:
        """Tạo câu hỏi toán học khó"""
        # Bình phương hoặc căn bậc hai
        if random.choice([True, False]):
            a = random.randint(10, 30)
            result = a * a
            question_text = f"{a}² = ?"
        else:
            a = random.randint(10, 20)
            result = a
            question_text = f"√{a * a} = ?"
        
        # Tạo các lựa chọn
        options = [str(result)]
        while len(options) < 4:
            wrong_answer = result + random.randint(-20, 20)
            if wrong_answer != result and str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(str(result)))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="math",
            difficulty="hard"
        )
    
    def generate_logic_question(self, difficulty: str = 'medium') -> Question:
        """Tạo câu hỏi logic"""
        if difficulty == 'easy':
            return self._generate_easy_logic()
        elif difficulty == 'medium':
            return self._generate_medium_logic()
        else:
            return self._generate_hard_logic()
    
    def _generate_easy_logic(self) -> Question:
        """Tạo câu hỏi logic dễ"""
        patterns = [
            ("2, 4, 6, 8, ?", "10", "Số chẵn tăng dần"),
            ("1, 3, 5, 7, ?", "9", "Số lẻ tăng dần"),
            ("1, 2, 4, 8, ?", "16", "Nhân 2"),
            ("10, 9, 8, 7, ?", "6", "Giảm 1"),
            ("1, 4, 9, 16, ?", "25", "Bình phương")
        ]
        
        pattern, answer, description = random.choice(patterns)
        question_text = f"Tìm số tiếp theo trong dãy: {pattern}"
        
        # Tạo các lựa chọn
        options = [answer]
        while len(options) < 4:
            wrong_answer = int(answer) + random.randint(-5, 5)
            if str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(answer))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="logic",
            difficulty="easy"
        )
    
    def _generate_medium_logic(self) -> Question:
        """Tạo câu hỏi logic trung bình"""
        patterns = [
            ("1, 1, 2, 3, 5, ?", "8", "Dãy Fibonacci"),
            ("2, 6, 12, 20, ?", "30", "Tăng dần: +4, +6, +8, +10"),
            ("1, 3, 6, 10, ?", "15", "Tổng các số từ 1"),
            ("3, 6, 11, 18, ?", "27", "Tăng: +3, +5, +7, +9"),
            ("1, 2, 6, 24, ?", "120", "Nhân: ×2, ×3, ×4, ×5")
        ]
        
        pattern, answer, description = random.choice(patterns)
        question_text = f"Tìm số tiếp theo trong dãy: {pattern}"
        
        # Tạo các lựa chọn
        options = [answer]
        while len(options) < 4:
            wrong_answer = int(answer) + random.randint(-10, 10)
            if str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(answer))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="logic",
            difficulty="medium"
        )
    
    def _generate_hard_logic(self) -> Question:
        """Tạo câu hỏi logic khó"""
        patterns = [
            ("1, 2, 4, 7, 11, ?", "16", "Tăng: +1, +2, +3, +4, +5"),
            ("2, 3, 5, 7, 11, ?", "13", "Số nguyên tố"),
            ("1, 4, 10, 22, ?", "46", "Nhân 2 + 2"),
            ("3, 7, 15, 31, ?", "63", "Nhân 2 + 1"),
            ("1, 2, 6, 24, 120, ?", "720", "Giai thừa")
        ]
        
        pattern, answer, description = random.choice(patterns)
        question_text = f"Tìm số tiếp theo trong dãy: {pattern}"
        
        # Tạo các lựa chọn
        options = [answer]
        while len(options) < 4:
            wrong_answer = int(answer) + random.randint(-20, 20)
            if str(wrong_answer) not in options:
                options.append(str(wrong_answer))
        
        random.shuffle(options)
        correct_answer = chr(ord('A') + options.index(answer))
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="logic",
            difficulty="hard"
        )
    
    def generate_science_question(self, difficulty: str = 'medium') -> Question:
        """Tạo câu hỏi khoa học"""
        questions = {
            'easy': [
                ("Công thức hóa học của nước là gì?", ["H2O", "CO2", "O2", "N2"], "A"),
                ("Hành tinh nào gần Mặt Trời nhất?", ["Sao Thủy", "Sao Kim", "Trái Đất", "Sao Hỏa"], "A"),
                ("Có bao nhiêu chân của một con bò?", ["2", "4", "6", "8"], "B"),
                ("Màu sắc của lá cây chủ yếu là gì?", ["Đỏ", "Xanh", "Vàng", "Trắng"], "B")
            ],
            'medium': [
                ("Thành phần chính của không khí là gì?", ["Nitơ", "Oxy", "CO2", "Hơi nước"], "A"),
                ("Nhiệt độ sôi của nước ở áp suất thường là bao nhiêu?", ["90°C", "100°C", "110°C", "120°C"], "B"),
                ("Có bao nhiêu xương trong cơ thể người trưởng thành?", ["206", "216", "226", "236"], "A"),
                ("Tốc độ ánh sáng là bao nhiêu km/s?", ["300,000", "250,000", "350,000", "400,000"], "A")
            ],
            'hard': [
                ("Thành phần chính của protein là gì?", ["Axit amin", "Glucose", "Lipid", "Vitamin"], "A"),
                ("Số nguyên tử trong phân tử glucose là bao nhiêu?", ["6", "12", "24", "36"], "C"),
                ("Nhiệt độ tuyệt đối 0°K tương đương bao nhiêu °C?", ["-273", "-173", "-373", "-473"], "A"),
                ("Chu kỳ bán rã của Carbon-14 là bao nhiêu năm?", ["5,730", "4,730", "6,730", "7,730"], "A")
            ]
        }
        
        question_data = random.choice(questions.get(difficulty, questions['medium']))
        question_text, options, correct_answer = question_data
        
        return Question(
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            category="science",
            difficulty=difficulty
        )
    
    def generate_question_set(self, count: int = 10, difficulty: str = 'medium') -> List[Question]:
        """Tạo một bộ câu hỏi"""
        questions = []
        
        for _ in range(count):
            category = random.choice(self.categories)
            
            if category == 'math':
                questions.append(self.generate_math_question(difficulty))
            elif category == 'logic':
                questions.append(self.generate_logic_question(difficulty))
            elif category == 'science':
                questions.append(self.generate_science_question(difficulty))
            else:
                # Tạo câu hỏi tổng hợp
                if random.choice([True, False]):
                    questions.append(self.generate_math_question(difficulty))
                else:
                    questions.append(self.generate_logic_question(difficulty))
        
        return questions
    
    def save_questions_to_json(self, questions: List[Question], filename: str = "generated_questions.json"):
        """Lưu câu hỏi vào file JSON"""
        questions_data = []
        
        for question in questions:
            questions_data.append({
                "question_text": question.question_text,
                "options": question.options,
                "correct_answer": question.correct_answer,
                "category": question.category,
                "difficulty": question.difficulty
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"questions": questions_data}, f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu {len(questions)} câu hỏi vào {filename}")

def main():
    """Test function"""
    generator = QuestionGenerator()
    
    # Tạo bộ câu hỏi
    print("Tạo bộ câu hỏi...")
    questions = generator.generate_question_set(count=20, difficulty='medium')
    
    # Hiển thị một số câu hỏi
    print("\nMột số câu hỏi được tạo:")
    for i, question in enumerate(questions[:5], 1):
        print(f"\n{i}. {question.question_text}")
        for j, option in enumerate(question.options):
            print(f"   {chr(ord('A') + j)}. {option}")
        print(f"   Đáp án: {question.correct_answer}")
        print(f"   Thể loại: {question.category}, Độ khó: {question.difficulty}")
    
    # Lưu vào file
    generator.save_questions_to_json(questions, "data/generated_questions.json")

if __name__ == "__main__":
    main() 