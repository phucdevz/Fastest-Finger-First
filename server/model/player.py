"""
Player Model - Thông tin người chơi trên server

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import time
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

class PlayerStatus(Enum):
    """Player status enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    READY = "ready"
    PLAYING = "playing"
    FINISHED = "finished"

@dataclass
class Player:
    """Player data structure"""
    id: str
    name: str
    connection: Any = None  # Socket connection
    status: PlayerStatus = PlayerStatus.CONNECTED
    score: int = 0
    correct_answers: int = 0
    total_answers: int = 0
    average_response_time: float = 0.0
    join_time: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert player to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'score': self.score,
            'correct_answers': self.correct_answers,
            'total_answers': self.total_answers,
            'average_response_time': self.average_response_time,
            'join_time': self.join_time,
            'last_activity': self.last_activity
        }
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()
    
    def add_score(self, points: int):
        """Add points to player score"""
        self.score += points
        self.update_activity()
    
    def record_answer(self, is_correct: bool, response_time: float):
        """Record player's answer and response time"""
        self.total_answers += 1
        if is_correct:
            self.correct_answers += 1
        
        # Update average response time
        if self.total_answers == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.total_answers - 1) + response_time) 
                / self.total_answers
            )
        
        self.update_activity()
    
    def get_accuracy(self) -> float:
        """Get player's answer accuracy percentage"""
        if self.total_answers == 0:
            return 0.0
        return (self.correct_answers / self.total_answers) * 100
    
    def is_active(self, timeout_seconds: int = 60) -> bool:
        """Check if player is still active based on timeout"""
        return (time.time() - self.last_activity) < timeout_seconds
    
    def reset_for_new_game(self):
        """Reset player stats for a new game"""
        self.score = 0
        self.correct_answers = 0
        self.total_answers = 0
        self.average_response_time = 0.0
        self.status = PlayerStatus.READY
        self.update_activity()

class PlayerManager:
    """Manager for handling multiple players"""
    
    def __init__(self):
        self.players: Dict[str, Player] = {}
        self.next_player_id = 1
    
    def add_player(self, name: str, connection: Any) -> Player:
        """Add a new player"""
        player_id = str(self.next_player_id)
        self.next_player_id += 1
        
        player = Player(
            id=player_id,
            name=name,
            connection=connection
        )
        
        self.players[player_id] = player
        return player
    
    def remove_player(self, player_id: str) -> Optional[Player]:
        """Remove a player by ID"""
        return self.players.pop(player_id, None)
    
    def get_player(self, player_id: str) -> Optional[Player]:
        """Get player by ID"""
        return self.players.get(player_id)
    
    def get_player_by_connection(self, connection: Any) -> Optional[Player]:
        """Get player by connection object"""
        for player in self.players.values():
            if player.connection == connection:
                return player
        return None
    
    def get_all_players(self) -> list[Player]:
        """Get all players"""
        return list(self.players.values())
    
    def get_active_players(self) -> list[Player]:
        """Get all active players"""
        return [p for p in self.players.values() if p.status != PlayerStatus.DISCONNECTED]
    
    def get_ready_players(self) -> list[Player]:
        """Get all ready players"""
        return [p for p in self.players.values() if p.status == PlayerStatus.READY]
    
    def get_playing_players(self) -> list[Player]:
        """Get all players currently playing"""
        return [p for p in self.players.values() if p.status == PlayerStatus.PLAYING]
    
    def disconnect_player(self, player_id: str):
        """Mark player as disconnected"""
        player = self.get_player(player_id)
        if player:
            player.status = PlayerStatus.DISCONNECTED
            player.update_activity()
    
    def cleanup_inactive_players(self, timeout_seconds: int = 60):
        """Remove inactive players"""
        inactive_players = []
        for player_id, player in self.players.items():
            if not player.is_active(timeout_seconds):
                inactive_players.append(player_id)
        
        for player_id in inactive_players:
            self.remove_player(player_id)
        
        return inactive_players
    
    def reset_all_players(self):
        """Reset all players for a new game"""
        for player in self.players.values():
            player.reset_for_new_game()
    
    def get_players_dict(self) -> Dict[str, Dict]:
        """Get all players as dictionary for broadcasting"""
        return {player_id: player.to_dict() for player_id, player in self.players.items()} 