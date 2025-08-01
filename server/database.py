"""
Module quản lý cơ sở dữ liệu cho Fastest Finger First
Sử dụng SQLite để lưu trữ dữ liệu người chơi, trận đấu và câu hỏi
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .config import DATABASE_FILE

class GameDatabase:
    def __init__(self, db_file: str = DATABASE_FILE):
        """Khởi tạo database"""
        self.db_file = db_file
        self.logger = logging.getLogger(__name__)
        self.init_database()
    
    def init_database(self):
        """Khởi tạo các bảng trong database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Bảng người chơi
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        total_games INTEGER DEFAULT 0,
                        total_score INTEGER DEFAULT 0,
                        best_score INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Bảng trận đấu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS games (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        total_players INTEGER,
                        total_questions INTEGER,
                        winner TEXT,
                        status TEXT DEFAULT 'finished'
                    )
                ''')
                
                # Bảng chi tiết trận đấu
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS game_details (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        player_username TEXT,
                        score INTEGER,
                        correct_answers INTEGER,
                        wrong_answers INTEGER,
                        average_response_time REAL,
                        FOREIGN KEY (game_id) REFERENCES games (id)
                    )
                ''')
                
                # Bảng câu hỏi đã sử dụng
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS used_questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        game_id INTEGER,
                        question_text TEXT,
                        correct_answer TEXT,
                        player_answers TEXT,  -- JSON string
                        question_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (game_id) REFERENCES games (id)
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
            raise
    
    def add_player(self, username: str) -> bool:
        """Thêm người chơi mới"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR IGNORE INTO players (username) VALUES (?)",
                    (username,)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            self.logger.error(f"Error adding player {username}: {e}")
            return False
    
    def get_player_stats(self, username: str) -> Optional[Dict]:
        """Lấy thống kê người chơi"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM players WHERE username = ?",
                    (username,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'total_games': row[2],
                        'total_score': row[3],
                        'best_score': row[4],
                        'created_at': row[5]
                    }
                return None
        except Exception as e:
            self.logger.error(f"Error getting player stats for {username}: {e}")
            return None
    
    def create_game(self, total_players: int, total_questions: int) -> int:
        """Tạo trận đấu mới và trả về game_id"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO games (total_players, total_questions) VALUES (?, ?)",
                    (total_players, total_questions)
                )
                game_id = cursor.lastrowid
                conn.commit()
                self.logger.info(f"Created new game with ID: {game_id}")
                return game_id
        except Exception as e:
            self.logger.error(f"Error creating game: {e}")
            return -1
    
    def end_game(self, game_id: int, winner: str):
        """Kết thúc trận đấu"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE games SET end_time = CURRENT_TIMESTAMP, winner = ? WHERE id = ?",
                    (winner, game_id)
                )
                conn.commit()
                self.logger.info(f"Game {game_id} ended, winner: {winner}")
        except Exception as e:
            self.logger.error(f"Error ending game {game_id}: {e}")
    
    def save_game_result(self, game_id: int, player_results: List[Dict]):
        """Lưu kết quả trận đấu"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                for result in player_results:
                    # Lưu chi tiết trận đấu
                    cursor.execute('''
                        INSERT INTO game_details 
                        (game_id, player_username, score, correct_answers, wrong_answers, average_response_time)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        game_id,
                        result['username'],
                        result['score'],
                        result['correct_answers'],
                        result['wrong_answers'],
                        result.get('average_response_time', 0)
                    ))
                    
                    # Cập nhật thống kê người chơi
                    cursor.execute('''
                        UPDATE players 
                        SET total_games = total_games + 1,
                            total_score = total_score + ?,
                            best_score = CASE WHEN ? > best_score THEN ? ELSE best_score END
                        WHERE username = ?
                    ''', (
                        result['score'],
                        result['score'],
                        result['score'],
                        result['username']
                    ))
                
                conn.commit()
                self.logger.info(f"Saved game results for game {game_id}")
                
        except Exception as e:
            self.logger.error(f"Error saving game results for game {game_id}: {e}")
    
    def save_question_result(self, game_id: int, question_text: str, correct_answer: str, player_answers: Dict):
        """Lưu kết quả câu hỏi"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO used_questions 
                    (game_id, question_text, correct_answer, player_answers)
                    VALUES (?, ?, ?, ?)
                ''', (
                    game_id,
                    question_text,
                    correct_answer,
                    json.dumps(player_answers)
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error saving question result: {e}")
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Lấy bảng xếp hạng"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT username, total_score, total_games, best_score
                    FROM players
                    ORDER BY total_score DESC, best_score DESC
                    LIMIT ?
                ''', (limit,))
                
                leaderboard = []
                for row in cursor.fetchall():
                    leaderboard.append({
                        'username': row[0],
                        'total_score': row[1],
                        'total_games': row[2],
                        'best_score': row[3]
                    })
                
                return leaderboard
        except Exception as e:
            self.logger.error(f"Error getting leaderboard: {e}")
            return []
    
    def get_recent_games(self, limit: int = 5) -> List[Dict]:
        """Lấy các trận đấu gần đây"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, start_time, end_time, total_players, winner
                    FROM games
                    ORDER BY start_time DESC
                    LIMIT ?
                ''', (limit,))
                
                games = []
                for row in cursor.fetchall():
                    games.append({
                        'id': row[0],
                        'start_time': row[1],
                        'end_time': row[2],
                        'total_players': row[3],
                        'winner': row[4]
                    })
                
                return games
        except Exception as e:
            self.logger.error(f"Error getting recent games: {e}")
            return []
    
    def get_player_history(self, username: str) -> List[Dict]:
        """Lấy lịch sử trận đấu của người chơi"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT g.id, g.start_time, g.end_time, g.total_players, g.winner,
                           gd.score, gd.correct_answers, gd.wrong_answers
                    FROM games g
                    JOIN game_details gd ON g.id = gd.game_id
                    WHERE gd.player_username = ?
                    ORDER BY g.start_time DESC
                ''', (username,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'game_id': row[0],
                        'start_time': row[1],
                        'end_time': row[2],
                        'total_players': row[3],
                        'winner': row[4],
                        'score': row[5],
                        'correct_answers': row[6],
                        'wrong_answers': row[7]
                    })
                
                return history
        except Exception as e:
            self.logger.error(f"Error getting player history for {username}: {e}")
            return [] 