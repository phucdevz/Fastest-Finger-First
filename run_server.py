#!/usr/bin/env python3
"""
Script chạy server Fastest Finger First
"""

import sys
import os
import json
import logging
from pathlib import Path

# Thêm thư mục gốc vào path
sys.path.insert(0, str(Path(__file__).parent))

from server.server import GameServer
from server.game_manager import Question
from data.questions_generator import QuestionGenerator

def load_questions_from_json(filename: str = "data/questions.json"):
    """Load câu hỏi từ file JSON"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        questions = []
        for q_data in data.get('questions', []):
            question = Question(
                question_text=q_data['question_text'],
                options=q_data['options'],
                correct_answer=q_data['correct_answer'],
                category=q_data.get('category', 'general'),
                difficulty=q_data.get('difficulty', 'medium')
            )
            questions.append(question)
        
        print(f"Loaded {len(questions)} questions from {filename}")
        return questions
        
    except FileNotFoundError:
        print(f"Question file {filename} not found. Generating questions...")
        return generate_questions()
    except Exception as e:
        print(f"Error loading questions: {e}")
        return generate_questions()

def generate_questions():
    """Tạo câu hỏi tự động"""
    generator = QuestionGenerator()
    questions = generator.generate_question_set(count=30, difficulty='medium')
    print(f"Generated {len(questions)} questions")
    return questions

def main():
    """Main function"""
    print("=" * 60)
    print("    FASTEST FINGER FIRST - SERVER")
    print("=" * 60)
    
    # Load câu hỏi
    questions = load_questions_from_json()
    
    # Tạo server
    server = GameServer()
    
    # Thiết lập câu hỏi cho game
    server.game_manager.set_questions(questions)
    
    print(f"Server ready with {len(questions)} questions")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Khởi động server
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()
    except Exception as e:
        print(f"Error: {e}")
        server.stop()

if __name__ == "__main__":
    main() 