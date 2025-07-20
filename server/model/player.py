"""
Player Model - Thông tin người chơi trên server

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import time
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import os

logger = logging.getLogger(__name__)

class PlayerStatus(Enum):
    """Player status enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    READY = "ready"
    PLAYING = "playing"
    FINISHED = "finished"
    SPECTATOR = "spectator"

class PlayerRole(Enum):
    """Player role enumeration"""
    PLAYER = "player"
    ADMIN = "admin"
    MODERATOR = "moderator"

@dataclass
class PlayerStats:
    """Player statistics data structure"""
    total_games: int = 0
    games_won: int = 0
    total_score: int = 0
    highest_score: int = 0
    total_questions_answered: int = 0
    correct_answers: int = 0
    total_response_time: float = 0.0
    fastest_response_time: float = float('inf')
    slowest_response_time: float = 0.0
    
    def get_accuracy(self) -> float:
        """Get player's answer accuracy percentage"""
        if self.total_questions_answered == 0:
            return 0.0
        return (self.correct_answers / self.total_questions_answered) * 100
    
    def get_average_response_time(self) -> float:
        """Get average response time in seconds"""
        if self.total_questions_answered == 0:
            return 0.0
        return self.total_response_time / self.total_questions_answered
    
    def get_win_rate(self) -> float:
        """Get player's win rate percentage"""
        if self.total_games == 0:
            return 0.0
        return (self.games_won / self.total_games) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return asdict(self)

@dataclass
class Player:
    """
    Player data structure
    
    Attributes:
        id: Unique player identifier
        name: Player display name
        connection: Socket connection object
        status: Current player status
        role: Player role (player, admin, moderator)
        score: Current game score
        stats: Player statistics across all games
        join_time: Timestamp when player joined
        last_activity: Timestamp of last activity
        current_game_id: ID of current game session
    """
    id: str
    name: str
    connection: Any = None  # Socket connection
    status: PlayerStatus = PlayerStatus.CONNECTED
    role: PlayerRole = PlayerRole.PLAYER
    score: int = 0
    stats: PlayerStats = field(default_factory=PlayerStats)
    join_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    current_game_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for JSON serialization"""
        data = asdict(self)
        data['status'] = self.status.value
        data['role'] = self.role.value
        data['stats'] = self.stats.to_dict()
        # Remove connection object as it can't be serialized
        data.pop('connection', None)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create player from dictionary"""
        # Convert enum strings back to enums
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = PlayerStatus(data['status'])
        if 'role' in data and isinstance(data['role'], str):
            data['role'] = PlayerRole(data['role'])
        if 'stats' in data and isinstance(data['stats'], dict):
            data['stats'] = PlayerStats(**data['stats'])
        return cls(**data)
    
    def update_activity(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    def add_score(self, points: int) -> None:
        """Add points to player score"""
        self.score += points
        self.stats.total_score += points
        if self.score > self.stats.highest_score:
            self.stats.highest_score = self.score
        self.update_activity()
    
    def record_answer(self, is_correct: bool, response_time: float, points: int = 0) -> None:
        """
        Record player's answer and response time
        
        Args:
            is_correct: Whether the answer was correct
            response_time: Response time in seconds
            points: Points earned for this answer
        """
        self.stats.total_questions_answered += 1
        if is_correct:
            self.stats.correct_answers += 1
            self.add_score(points)
        
        # Update response time statistics
        self.stats.total_response_time += response_time
        if response_time < self.stats.fastest_response_time:
            self.stats.fastest_response_time = response_time
        if response_time > self.stats.slowest_response_time:
            self.stats.slowest_response_time = response_time
        
        self.update_activity()
    
    def record_game_result(self, won: bool, final_score: int) -> None:
        """
        Record game result
        
        Args:
            won: Whether the player won the game
            final_score: Final score in the game
        """
        self.stats.total_games += 1
        if won:
            self.stats.games_won += 1
        self.update_activity()
    
    def is_active(self, timeout_seconds: int = 60) -> bool:
        """
        Check if player is still active based on timeout
        
        Args:
            timeout_seconds: Timeout in seconds
            
        Returns:
            True if player is active, False otherwise
        """
        return (time.time() - self.last_activity) < timeout_seconds
    
    def reset_for_new_game(self) -> None:
        """Reset player stats for a new game"""
        self.score = 0
        self.status = PlayerStatus.READY
        self.current_game_id = None
        self.update_activity()
    
    def disconnect(self) -> None:
        """Mark player as disconnected"""
        self.status = PlayerStatus.DISCONNECTED
        self.update_activity()
        logger.info(f"Player {self.name} (ID: {self.id}) disconnected")
    
    def get_display_info(self) -> Dict[str, Any]:
        """Get player information for display (without sensitive data)"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'score': self.score,
            'accuracy': self.stats.get_accuracy(),
            'average_response_time': self.stats.get_average_response_time(),
            'total_games': self.stats.total_games,
            'win_rate': self.stats.get_win_rate()
        }

class PlayerManager:
    """
    Manager for handling multiple players
    
    Features:
    - Player registration and management
    - Connection tracking
    - Statistics aggregation
    - Player search and filtering
    """
    
    def __init__(self):
        """Initialize player manager"""
        self.players: Dict[str, Player] = {}
        self.next_player_id = 1
        self.player_stats_file = "data/player_stats.json"
        self.load_player_stats()
    
    def load_player_stats(self) -> None:
        """Load player statistics from file"""
        try:
            if os.path.exists(self.player_stats_file):
                with open(self.player_stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for player_data in data.get('players', []):
                        player = Player.from_dict(player_data)
                        self.players[player.id] = player
                logger.info(f"Loaded {len(self.players)} player profiles")
        except Exception as e:
            logger.error(f"Error loading player stats: {e}")
    
    def save_player_stats(self) -> None:
        """Save player statistics to file"""
        try:
            os.makedirs(os.path.dirname(self.player_stats_file), exist_ok=True)
            data = {
                'players': [player.to_dict() for player in self.players.values()],
                'metadata': {
                    'total_players': len(self.players),
                    'last_updated': time.time()
                }
            }
            with open(self.player_stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.players)} player profiles")
        except Exception as e:
            logger.error(f"Error saving player stats: {e}")
    
    def add_player(self, name: str, connection: Any, role: PlayerRole = PlayerRole.PLAYER) -> Player:
        """
        Add a new player
        
        Args:
            name: Player name
            connection: Socket connection
            role: Player role
            
        Returns:
            Created player object
        """
        # Check if player with this name already exists
        existing_player = self.get_player_by_name(name)
        if existing_player:
            # Update existing player's connection
            existing_player.connection = connection
            existing_player.status = PlayerStatus.CONNECTED
            existing_player.update_activity()
            logger.info(f"Reconnected existing player: {name}")
            return existing_player
        
        # Create new player
        player_id = str(self.next_player_id)
        self.next_player_id += 1
        
        player = Player(
            id=player_id,
            name=name,
            connection=connection,
            role=role
        )
        
        self.players[player_id] = player
        logger.info(f"Added new player: {name} (ID: {player_id})")
        return player
    
    def remove_player(self, player_id: str) -> Optional[Player]:
        """
        Remove a player by ID
        
        Args:
            player_id: Player ID to remove
            
        Returns:
            Removed player object or None if not found
        """
        player = self.players.pop(player_id, None)
        if player:
            logger.info(f"Removed player: {player.name} (ID: {player_id})")
            self.save_player_stats()
        return player
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        return self.players.get(player_id)
    
    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get player by name"""
        for player in self.players.values():
            if player.name == name:
                return player
        return None
    
    def get_player_by_connection(self, connection: Any) -> Optional[Player]:
        """Get player by connection object"""
        for player in self.players.values():
            if player.connection == connection:
                return player
        return None
    
    def get_all_players(self) -> List[Player]:
        """Get all players"""
        return list(self.players.values())
    
    def get_active_players(self) -> List[Player]:
        """Get all active players"""
        return [p for p in self.players.values() if p.status != PlayerStatus.DISCONNECTED]
    
    def get_ready_players(self) -> List[Player]:
        """Get all ready players"""
        return [p for p in self.players.values() if p.status == PlayerStatus.READY]
    
    def get_playing_players(self) -> List[Player]:
        """Get all players currently playing"""
        return [p for p in self.players.values() if p.status == PlayerStatus.PLAYING]
    
    def get_players_by_role(self, role: PlayerRole) -> List[Player]:
        """Get all players with specific role"""
        return [p for p in self.players.values() if p.role == role]
    
    def disconnect_player(self, player_id: str) -> None:
        """Mark player as disconnected"""
        player = self.get_player(player_id)
        if player:
            player.disconnect()
    
    def cleanup_inactive_players(self, timeout_seconds: int = 60) -> List[str]:
        """
        Remove inactive players
        
        Args:
            timeout_seconds: Timeout in seconds
            
        Returns:
            List of removed player IDs
        """
        inactive_players = []
        for player_id, player in self.players.items():
            if not player.is_active(timeout_seconds):
                inactive_players.append(player_id)
        
        for player_id in inactive_players:
            self.remove_player(player_id)
        
        if inactive_players:
            logger.info(f"Cleaned up {len(inactive_players)} inactive players")
        
        return inactive_players
    
    def reset_all_players(self) -> None:
        """Reset all players for a new game"""
        for player in self.players.values():
            player.reset_for_new_game()
        logger.info("Reset all players for new game")
    
    def get_players_dict(self) -> Dict[str, Dict[str, Any]]:
        """Get all players as dictionary for broadcasting"""
        return {player_id: player.get_display_info() 
                for player_id, player in self.players.items()}
    
    def get_top_players(self, limit: int = 10) -> List[Player]:
        """
        Get top players by total score
        
        Args:
            limit: Number of top players to return
            
        Returns:
            List of top players sorted by total score
        """
        sorted_players = sorted(
            self.players.values(),
            key=lambda p: p.stats.total_score,
            reverse=True
        )
        return sorted_players[:limit]
    
    def get_player_statistics(self) -> Dict[str, Any]:
        """Get overall player statistics"""
        if not self.players:
            return {}
        
        total_players = len(self.players)
        active_players = len(self.get_active_players())
        
        total_games = sum(p.stats.total_games for p in self.players.values())
        total_questions = sum(p.stats.total_questions_answered for p in self.players.values())
        total_correct = sum(p.stats.correct_answers for p in self.players.values())
        
        avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        avg_games = total_games / total_players if total_players > 0 else 0
        
        return {
            'total_players': total_players,
            'active_players': active_players,
            'total_games_played': total_games,
            'total_questions_answered': total_questions,
            'average_accuracy': avg_accuracy,
            'average_games_per_player': avg_games,
            'top_player': max(self.players.values(), key=lambda p: p.stats.total_score).name
        }
    
    def broadcast_to_all(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all connected players
        
        Args:
            message: Message to broadcast
        """
        for player in self.get_active_players():
            if player.connection:
                try:
                    # This will be implemented in network_manager
                    pass
                except Exception as e:
                    logger.error(f"Error broadcasting to {player.name}: {e}")
    
    def __len__(self) -> int:
        """Return number of players"""
        return len(self.players) 