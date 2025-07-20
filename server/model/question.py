"""
Question Model - Định nghĩa class Câu hỏi, quản lý bộ đề

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import os

class QuestionType(Enum):
    """Question types"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

@dataclass
class Question:
    """Question data structure"""
    id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: int = 30  # seconds
    
    def to_dict(self) -> Dict:
        """Convert question to dictionary"""
        return {
            'id': self.id,
            'question': self.question,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'category': self.category,
            'difficulty': self.difficulty,
            'time_limit': self.time_limit
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Question':
        """Create question from dictionary"""
        return cls(**data)

class QuestionBank:
    """Question bank manager"""
    
    def __init__(self, questions_file: str = "data/questions.json"):
        self.questions_file = questions_file
        self.questions: List[Question] = []
        self.load_questions()
    
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open(self.questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = [Question.from_dict(q) for q in data.get('questions', [])]
        except FileNotFoundError:
            print(f"Questions file {self.questions_file} not found. Creating sample questions.")
            self.create_sample_questions()
        except Exception as e:
            print(f"Error loading questions: {e}")
            self.create_sample_questions()
    
    def create_sample_questions(self):
        """Create sample questions if file doesn't exist"""
        sample_questions = [
            {
                'id': '1',
                'question': 'What is the capital of Vietnam?',
                'options': ['Hanoi', 'Ho Chi Minh City', 'Da Nang', 'Hue'],
                'correct_answer': 'Hanoi',
                'explanation': 'Hanoi is the capital and second-largest city of Vietnam.',
                'category': 'Geography',
                'difficulty': 'easy',
                'time_limit': 30
            },
            {
                'id': '2',
                'question': 'Which planet is closest to the Sun?',
                'options': ['Venus', 'Mercury', 'Earth', 'Mars'],
                'correct_answer': 'Mercury',
                'explanation': 'Mercury is the first planet from the Sun.',
                'category': 'Science',
                'difficulty': 'easy',
                'time_limit': 30
            },
            {
                'id': '3',
                'question': 'What is 2 + 2?',
                'options': ['3', '4', '5', '6'],
                'correct_answer': '4',
                'explanation': 'Basic arithmetic.',
                'category': 'Math',
                'difficulty': 'easy',
                'time_limit': 15
            }
        ]
        
        self.questions = [Question.from_dict(q) for q in sample_questions]
        self.save_questions()
    
    def save_questions(self):
        """Save questions to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.questions_file), exist_ok=True)
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump({'questions': [q.to_dict() for q in self.questions]}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving questions: {e}")
    
    def get_random_question(self) -> Optional[Question]:
        """Get a random question"""
        if not self.questions:
            return None
        return random.choice(self.questions)
    
    def get_questions_by_category(self, category: str) -> List[Question]:
        """Get questions by category"""
        return [q for q in self.questions if q.category == category]
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Question]:
        """Get questions by difficulty"""
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def add_question(self, question: Question):
        """Add a new question"""
        self.questions.append(question)
        self.save_questions()
    
    def remove_question(self, question_id: str):
        """Remove a question by ID"""
        self.questions = [q for q in self.questions if q.id != question_id]
        self.save_questions()
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None 