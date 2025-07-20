"""
Scoreboard Model - Bảng điểm, lưu trạng thái trận đấu

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import os

logger = logging.getLogger(__name__)

class GameStatus(Enum):
    """Game status enumeration"""
    WAITING = "waiting"
    STARTING = "starting"
    PLAYING = "playing"
    FINISHED = "finished"
    CANCELLED = "cancelled"

@dataclass
class GameResult:
    """Game result data structure"""
    game_id: str
    start_time: float
    end_time: float
    total_questions: int
    players: List[str]  # Player IDs
    winner_id: Optional[str] = None
    winner_score: int = 0
    game_duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

@dataclass
class ScoreboardEntry:
    """Scoreboard entry for a player in a game"""
    player_id: str
    player_name: str
    score: int = 0
    correct_answers: int = 0
    total_answers: int = 0
    fastest_answer_time: float = float('inf')
    average_answer_time: float = 0.0
    total_answer_time: float = 0.0
    last_answer_time: float = 0.0
    
    def update_score(self, points: int) -> None:
        """Update player score"""
        self.score += points
    
    def record_answer(self, is_correct: bool, answer_time: float) -> None:
        """
        Record player's answer
        
        Args:
            is_correct: Whether the answer was correct
            answer_time: Time taken to answer in seconds
        """
        self.total_answers += 1
        if is_correct:
            self.correct_answers += 1
        
        # Update timing statistics
        self.total_answer_time += answer_time
        self.average_answer_time = self.total_answer_time / self.total_answers
        if answer_time < self.fastest_answer_time:
            self.fastest_answer_time = answer_time
        self.last_answer_time = time.time()
    
    def get_accuracy(self) -> float:
        """Get answer accuracy percentage"""
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['accuracy'] = self.get_accuracy()
        return data

class Scoreboard:
    """
    Scoreboard manager for tracking game scores and rankings
    
    Features:
    - Real-time score tracking
    - Player rankings
    - Game history
    - Statistics calculation
    - Persistent storage
    """
    
    def __init__(self, history_file: str = "data/game_history.json"):
        """
        Initialize scoreboard
        
        Args:
            history_file: Path to file for storing game history
        """
        self.history_file = history_file
        self.current_game_id: Optional[str] = None
        self.current_game_start: Optional[float] = None
        self.game_status: GameStatus = GameStatus.WAITING
        self.entries: Dict[str, ScoreboardEntry] = {}
        self.game_history: List[GameResult] = []
        self.load_game_history()
    
    def load_game_history(self) -> None:
        """Load game history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.game_history = [GameResult(**game) for game in data.get('games', [])]
                logger.info(f"Loaded {len(self.game_history)} game records")
        except Exception as e:
            logger.error(f"Error loading game history: {e}")
    
    def save_game_history(self) -> None:
        """Save game history to file"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            data = {
                'games': [game.to_dict() for game in self.game_history],
                'metadata': {
                    'total_games': len(self.game_history),
                    'last_updated': time.time()
                }
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.game_history)} game records")
        except Exception as e:
            logger.error(f"Error saving game history: {e}")
    
    def start_new_game(self, game_id: str, player_ids: List[str], 
                      player_names: Dict[str, str]) -> None:
        """
        Start a new game
        
        Args:
            game_id: Unique game identifier
            player_ids: List of player IDs participating
            player_names: Dictionary mapping player IDs to names
        """
        self.current_game_id = game_id
        self.current_game_start = time.time()
        self.game_status = GameStatus.STARTING
        
        # Initialize scoreboard entries
        self.entries.clear()
        for player_id in player_ids:
            self.entries[player_id] = ScoreboardEntry(
                player_id=player_id,
                player_name=player_names.get(player_id, f"Player_{player_id}")
            )
        
        logger.info(f"Started new game {game_id} with {len(player_ids)} players")
    
    def start_playing(self) -> None:
        """Mark game as playing"""
        self.game_status = GameStatus.PLAYING
        logger.info(f"Game {self.current_game_id} is now playing")
    
    def record_answer(self, player_id: str, is_correct: bool, 
                     answer_time: float, points: int = 0) -> None:
        """
        Record a player's answer
        
        Args:
            player_id: Player ID
            is_correct: Whether the answer was correct
            answer_time: Time taken to answer in seconds
            points: Points earned for this answer
        """
        if player_id not in self.entries:
            logger.warning(f"Player {player_id} not found in current game")
            return
        
        entry = self.entries[player_id]
        entry.record_answer(is_correct, answer_time)
        
        if is_correct:
            entry.update_score(points)
        
        logger.debug(f"Player {entry.player_name} answered {'correctly' if is_correct else 'incorrectly'} "
                    f"in {answer_time:.2f}s, score: {entry.score}")
    
    def get_current_rankings(self) -> List[Dict[str, Any]]:
        """
        Get current player rankings sorted by score
        
        Returns:
            List of player rankings with score and stats
        """
        sorted_entries = sorted(
            self.entries.values(),
            key=lambda e: (e.score, -e.average_answer_time),  # Higher score first, then faster time
            reverse=True
        )
        
        rankings = []
        for i, entry in enumerate(sorted_entries, 1):
            ranking_data = entry.to_dict()
            ranking_data['rank'] = i
            rankings.append(ranking_data)
        
        return rankings
    
    def get_player_score(self, player_id: str) -> Optional[ScoreboardEntry]:
        """Get scoreboard entry for a specific player"""
        return self.entries.get(player_id)
    
    def get_leader(self) -> Optional[ScoreboardEntry]:
        """Get the current leader (player with highest score)"""
        if not self.entries:
            return None
        
        return max(self.entries.values(), key=lambda e: e.score)
    
    def finish_game(self) -> GameResult:
        """
        Finish the current game and save results
        
        Returns:
            GameResult object with game summary
        """
        if not self.current_game_id:
            raise ValueError("No active game to finish")
        
        end_time = time.time()
        game_duration = end_time - self.current_game_start
        
        # Find winner
        winner_entry = self.get_leader()
        winner_id = winner_entry.player_id if winner_entry else None
        winner_score = winner_entry.score if winner_entry else 0
        
        # Create game result
        game_result = GameResult(
            game_id=self.current_game_id,
            start_time=self.current_game_start,
            end_time=end_time,
            total_questions=0,  # TODO: Track total questions asked
            players=list(self.entries.keys()),
            winner_id=winner_id,
            winner_score=winner_score,
            game_duration=game_duration
        )
        
        # Add to history
        self.game_history.append(game_result)
        self.save_game_history()
        
        # Reset current game
        self.current_game_id = None
        self.current_game_start = None
        self.game_status = GameStatus.FINISHED
        self.entries.clear()
        
        logger.info(f"Finished game {game_result.game_id}. "
                   f"Winner: {winner_entry.player_name if winner_entry else 'None'} "
                   f"with {winner_score} points")
        
        return game_result
    
    def cancel_game(self) -> None:
        """Cancel the current game"""
        if self.current_game_id:
            self.game_status = GameStatus.CANCELLED
            logger.info(f"Cancelled game {self.current_game_id}")
            
            # Reset current game
            self.current_game_id = None
            self.current_game_start = None
            self.entries.clear()
    
    def get_game_statistics(self) -> Dict[str, Any]:
        """Get statistics for the current game"""
        if not self.entries:
            return {}
        
        total_players = len(self.entries)
        total_score = sum(entry.score for entry in self.entries.values())
        total_answers = sum(entry.total_answers for entry in self.entries.values())
        total_correct = sum(entry.correct_answers for entry in self.entries.values())
        
        avg_score = total_score / total_players if total_players > 0 else 0
        avg_accuracy = (total_correct / total_answers * 100) if total_answers > 0 else 0
        
        # Find fastest responder
        fastest_player = min(
            self.entries.values(),
            key=lambda e: e.fastest_answer_time if e.fastest_answer_time != float('inf') else float('inf')
        )
        
        return {
            'total_players': total_players,
            'total_score': total_score,
            'average_score': avg_score,
            'total_answers': total_answers,
            'total_correct_answers': total_correct,
            'average_accuracy': avg_accuracy,
            'fastest_player': fastest_player.player_name if fastest_player.fastest_answer_time != float('inf') else None,
            'fastest_answer_time': fastest_player.fastest_answer_time if fastest_player.fastest_answer_time != float('inf') else None,
            'game_duration': time.time() - self.current_game_start if self.current_game_start else 0
        }
    
    def get_recent_games(self, limit: int = 10) -> List[GameResult]:
        """
        Get recent game results
        
        Args:
            limit: Number of recent games to return
            
        Returns:
            List of recent GameResult objects
        """
        return sorted(self.game_history, key=lambda g: g.end_time, reverse=True)[:limit]
    
    def get_player_history(self, player_id: str) -> List[GameResult]:
        """
        Get game history for a specific player
        
        Args:
            player_id: Player ID to get history for
            
        Returns:
            List of games the player participated in
        """
        return [game for game in self.game_history if player_id in game.players]
    
    def get_overall_statistics(self) -> Dict[str, Any]:
        """Get overall statistics across all games"""
        if not self.game_history:
            return {}
        
        total_games = len(self.game_history)
        completed_games = len([g for g in self.game_history if g.winner_id])
        
        # Calculate average game duration
        avg_duration = sum(g.game_duration for g in self.game_history) / total_games
        
        # Find most active player
        player_game_count = {}
        for game in self.game_history:
            for player_id in game.players:
                player_game_count[player_id] = player_game_count.get(player_id, 0) + 1
        
        most_active_player = max(player_game_count.items(), key=lambda x: x[1]) if player_game_count else None
        
        return {
            'total_games': total_games,
            'completed_games': completed_games,
            'completion_rate': (completed_games / total_games * 100) if total_games > 0 else 0,
            'average_game_duration': avg_duration,
            'most_active_player': most_active_player[0] if most_active_player else None,
            'most_active_player_games': most_active_player[1] if most_active_player else 0
        }
    
    def export_scoreboard(self) -> Dict[str, Any]:
        """Export current scoreboard data for client consumption"""
        return {
            'game_id': self.current_game_id,
            'status': self.game_status.value,
            'start_time': self.current_game_start,
            'rankings': self.get_current_rankings(),
            'statistics': self.get_game_statistics(),
            'total_players': len(self.entries)
        }
    
    def is_game_active(self) -> bool:
        """Check if there's an active game"""
        return (self.current_game_id is not None and 
                self.game_status in [GameStatus.STARTING, GameStatus.PLAYING])
    
    def get_waiting_players(self) -> List[str]:
        """Get list of players waiting to start"""
        return list(self.entries.keys()) if self.game_status == GameStatus.WAITING else []
    
    def add_waiting_player(self, player_id: str, player_name: str) -> None:
        """Add a player to the waiting list"""
        if self.game_status == GameStatus.WAITING:
            self.entries[player_id] = ScoreboardEntry(
                player_id=player_id,
                player_name=player_name
            )
            logger.info(f"Added {player_name} to waiting list")
    
    def remove_waiting_player(self, player_id: str) -> bool:
        """Remove a player from the waiting list"""
        if player_id in self.entries and self.game_status == GameStatus.WAITING:
            player_name = self.entries[player_id].player_name
            del self.entries[player_id]
            logger.info(f"Removed {player_name} from waiting list")
            return True
        return False 