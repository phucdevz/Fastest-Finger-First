"""
Question Model - Định nghĩa class Câu hỏi, quản lý bộ đề

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import json
import random
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    """Question types enumeration"""
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

class QuestionDifficulty(Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

@dataclass
class Question:
    """
    Question data structure
    
    Attributes:
        id: Unique question identifier
        question: Question text
        options: List of answer options
        correct_answer: Correct answer text
        explanation: Optional explanation for the answer
        category: Question category (e.g., "Math", "Science")
        difficulty: Question difficulty level
        time_limit: Time limit in seconds for answering
        points: Points awarded for correct answer
    """
    id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    category: Optional[str] = None
    difficulty: QuestionDifficulty = QuestionDifficulty.EASY
    time_limit: int = 30
    points: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert question to dictionary for JSON serialization"""
        data = asdict(self)
        data['difficulty'] = self.difficulty.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """Create question from dictionary"""
        # Convert difficulty string back to enum
        if 'difficulty' in data and isinstance(data['difficulty'], str):
            data['difficulty'] = QuestionDifficulty(data['difficulty'])
        return cls(**data)
    
    def validate(self) -> bool:
        """Validate question data integrity"""
        if not self.id or not self.question:
            return False
        if not self.options or len(self.options) < 2:
            return False
        if self.correct_answer not in self.options:
            return False
        if self.time_limit <= 0:
            return False
        return True

class QuestionBank:
    """
    Question bank manager for loading, storing, and retrieving questions
    
    Supports:
    - Loading questions from JSON file
    - Random question selection
    - Filtering by category/difficulty
    - Question validation
    - Auto-creation of sample questions
    """
    
    def __init__(self, questions_file: str = "data/questions.json"):
        """
        Initialize question bank
        
        Args:
            questions_file: Path to JSON file containing questions
        """
        self.questions_file = questions_file
        self.questions: List[Question] = []
        self.categories: set = set()
        self.difficulties: set = set()
        self.load_questions()
    
    def load_questions(self) -> None:
        """Load questions from JSON file or create sample questions if file doesn't exist"""
        try:
            if os.path.exists(self.questions_file):
                with open(self.questions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    questions_data = data.get('questions', [])
                    self.questions = [Question.from_dict(q) for q in questions_data]
                    logger.info(f"Loaded {len(self.questions)} questions from {self.questions_file}")
            else:
                logger.warning(f"Questions file {self.questions_file} not found. Creating sample questions.")
                self.create_sample_questions()
                
            self._update_metadata()
            self._validate_all_questions()
            
        except Exception as e:
            logger.error(f"Error loading questions: {e}")
            self.create_sample_questions()
    
    def create_sample_questions(self) -> None:
        """Create sample questions for testing purposes"""
        sample_questions = [
            {
                'id': '1',
                'question': 'What is the capital of Vietnam?',
                'options': ['Hanoi', 'Ho Chi Minh City', 'Da Nang', 'Hue'],
                'correct_answer': 'Hanoi',
                'explanation': 'Hanoi is the capital and second-largest city of Vietnam.',
                'category': 'Geography',
                'difficulty': QuestionDifficulty.EASY,
                'time_limit': 30,
                'points': 10
            },
            {
                'id': '2',
                'question': 'Which planet is closest to the Sun?',
                'options': ['Venus', 'Mercury', 'Earth', 'Mars'],
                'correct_answer': 'Mercury',
                'explanation': 'Mercury is the first planet from the Sun.',
                'category': 'Science',
                'difficulty': QuestionDifficulty.EASY,
                'time_limit': 30,
                'points': 10
            },
            {
                'id': '3',
                'question': 'What is 15 + 27?',
                'options': ['40', '42', '43', '41'],
                'correct_answer': '42',
                'explanation': 'Basic arithmetic: 15 + 27 = 42',
                'category': 'Math',
                'difficulty': QuestionDifficulty.EASY,
                'time_limit': 20,
                'points': 10
            },
            {
                'id': '4',
                'question': 'Which programming language is this game written in?',
                'options': ['Java', 'Python', 'C++', 'JavaScript'],
                'correct_answer': 'Python',
                'explanation': 'This game is built using Python with socket programming.',
                'category': 'Programming',
                'difficulty': QuestionDifficulty.MEDIUM,
                'time_limit': 25,
                'points': 15
            },
            {
                'id': '5',
                'question': 'What is the largest ocean on Earth?',
                'options': ['Atlantic Ocean', 'Indian Ocean', 'Arctic Ocean', 'Pacific Ocean'],
                'correct_answer': 'Pacific Ocean',
                'explanation': 'The Pacific Ocean is the largest and deepest ocean on Earth.',
                'category': 'Geography',
                'difficulty': QuestionDifficulty.MEDIUM,
                'time_limit': 30,
                'points': 15
            }
        ]
        
        self.questions = [Question.from_dict(q) for q in sample_questions]
        self.save_questions()
        logger.info(f"Created {len(self.questions)} sample questions")
    
    def save_questions(self) -> None:
        """Save questions to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.questions_file), exist_ok=True)
            data = {
                'questions': [q.to_dict() for q in self.questions],
                'metadata': {
                    'total_questions': len(self.questions),
                    'categories': list(self.categories),
                    'difficulties': list(self.difficulties)
                }
            }
            with open(self.questions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.questions)} questions to {self.questions_file}")
        except Exception as e:
            logger.error(f"Error saving questions: {e}")
    
    def _update_metadata(self) -> None:
        """Update internal metadata (categories, difficulties)"""
        self.categories = {q.category for q in self.questions if q.category}
        self.difficulties = {q.difficulty for q in self.questions}
    
    def _validate_all_questions(self) -> None:
        """Validate all loaded questions and log any issues"""
        invalid_questions = []
        for question in self.questions:
            if not question.validate():
                invalid_questions.append(question.id)
        
        if invalid_questions:
            logger.warning(f"Found {len(invalid_questions)} invalid questions: {invalid_questions}")
    
    def get_random_question(self, category: Optional[str] = None, 
                          difficulty: Optional[QuestionDifficulty] = None) -> Optional[Question]:
        """
        Get a random question with optional filtering
        
        Args:
            category: Filter by category
            difficulty: Filter by difficulty level
            
        Returns:
            Random question or None if no questions match criteria
        """
        filtered_questions = self.questions
        
        if category:
            filtered_questions = [q for q in filtered_questions if q.category == category]
        
        if difficulty:
            filtered_questions = [q for q in filtered_questions if q.difficulty == difficulty]
        
        if not filtered_questions:
            logger.warning(f"No questions found for category={category}, difficulty={difficulty}")
            return None
            
        return random.choice(filtered_questions)
    
    def get_questions_by_category(self, category: str) -> List[Question]:
        """Get all questions in a specific category"""
        return [q for q in self.questions if q.category == category]
    
    def get_questions_by_difficulty(self, difficulty: QuestionDifficulty) -> List[Question]:
        """Get all questions of a specific difficulty level"""
        return [q for q in self.questions if q.difficulty == difficulty]
    
    def add_question(self, question: Question) -> bool:
        """
        Add a new question to the bank
        
        Args:
            question: Question object to add
            
        Returns:
            True if added successfully, False otherwise
        """
        if not question.validate():
            logger.error(f"Invalid question data: {question.id}")
            return False
        
        # Check for duplicate ID
        if any(q.id == question.id for q in self.questions):
            logger.error(f"Question with ID {question.id} already exists")
            return False
        
        self.questions.append(question)
        self._update_metadata()
        self.save_questions()
        logger.info(f"Added question: {question.id}")
        return True
    
    def remove_question(self, question_id: str) -> bool:
        """
        Remove a question by ID
        
        Args:
            question_id: ID of question to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        initial_count = len(self.questions)
        self.questions = [q for q in self.questions if q.id != question_id]
        
        if len(self.questions) < initial_count:
            self._update_metadata()
            self.save_questions()
            logger.info(f"Removed question: {question_id}")
            return True
        else:
            logger.warning(f"Question with ID {question_id} not found")
            return False
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        for question in self.questions:
            if question.id == question_id:
                return question
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get question bank statistics"""
        return {
            'total_questions': len(self.questions),
            'categories': list(self.categories),
            'difficulties': [d.value for d in self.difficulties],
            'questions_per_category': {cat: len(self.get_questions_by_category(cat)) 
                                     for cat in self.categories},
            'questions_per_difficulty': {diff.value: len(self.get_questions_by_difficulty(diff)) 
                                       for diff in self.difficulties}
        }
    
    def reload_questions(self) -> None:
        """Reload questions from file"""
        logger.info("Reloading questions from file")
        self.load_questions() 