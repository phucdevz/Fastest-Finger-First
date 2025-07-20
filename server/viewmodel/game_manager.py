"""
Game Manager - Điều phối phòng chờ, gửi câu hỏi, nhận đáp án, tính điểm

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import time
import threading
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from server.model.question import QuestionBank, Question
from server.model.player import PlayerManager, Player, PlayerStatus
from server.model.scoreboard import Scoreboard, GameStatus

logger = logging.getLogger(__name__)

class GamePhase(Enum):
    """Game phase enumeration"""
    WAITING = "waiting"
    COUNTDOWN = "countdown"
    QUESTION = "question"
    ANSWER_REVIEW = "answer_review"
    GAME_END = "game_end"

@dataclass
class GameConfig:
    """Game configuration settings"""
    min_players: int = 2
    max_players: int = 10
    questions_per_game: int = 10
    question_time_limit: int = 30
    countdown_duration: int = 5
    answer_review_duration: int = 3
    auto_start_delay: int = 10  # seconds to wait before auto-starting

class GameManager:
    """
    Game manager for coordinating game flow and logic
    
    Features:
    - Game state management
    - Question broadcasting
    - Answer processing
    - Score calculation
    - Game flow control
    - Player coordination
    """
    
    def __init__(self, question_bank: QuestionBank, player_manager: PlayerManager):
        """
        Initialize game manager
        
        Args:
            question_bank: Question bank instance
            player_manager: Player manager instance
        """
        self.question_bank = question_bank
        self.player_manager = player_manager
        self.scoreboard = Scoreboard()
        
        # Game state
        self.current_game_id: Optional[str] = None
        self.game_phase = GamePhase.WAITING
        self.game_config = GameConfig()
        
        # Current question state
        self.current_question: Optional[Question] = None
        self.question_start_time: Optional[float] = None
        self.answers_received: Dict[str, Dict[str, Any]] = {}
        
        # Game statistics
        self.questions_asked = 0
        self.game_start_time: Optional[float] = None
        
        # Callbacks for network communication
        self.broadcast_callback: Optional[Callable[[Dict[str, Any]], None]] = None
        self.send_to_player_callback: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        # Threading
        self.game_thread: Optional[threading.Thread] = None
        self.game_running = False
        
        logger.info("Game manager initialized")
    
    def set_callbacks(self, broadcast_callback: Callable[[Dict[str, Any]], None],
                     send_to_player_callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """
        Set network communication callbacks
        
        Args:
            broadcast_callback: Function to broadcast messages to all players
            send_to_player_callback: Function to send message to specific player
        """
        self.broadcast_callback = broadcast_callback
        self.send_to_player_callback = send_to_player_callback
    
    def start_game(self, game_id: Optional[str] = None) -> bool:
        """
        Start a new game
        
        Args:
            game_id: Optional game ID, will generate if not provided
            
        Returns:
            True if game started successfully, False otherwise
        """
        if self.game_running:
            logger.warning("Game already running")
            return False
        
        ready_players = self.player_manager.get_ready_players()
        if len(ready_players) < self.game_config.min_players:
            logger.warning(f"Not enough players to start game. Need {self.game_config.min_players}, got {len(ready_players)}")
            return False
        
        # Generate game ID if not provided
        if not game_id:
            game_id = str(uuid.uuid4())
        
        self.current_game_id = game_id
        self.game_phase = GamePhase.WAITING
        self.questions_asked = 0
        self.game_start_time = time.time()
        
        # Initialize scoreboard
        player_ids = [p.id for p in ready_players]
        player_names = {p.id: p.name for p in ready_players}
        self.scoreboard.start_new_game(game_id, player_ids, player_names)
        
        # Mark players as playing
        for player in ready_players:
            player.status = PlayerStatus.PLAYING
            player.current_game_id = game_id
        
        # Start game thread
        self.game_running = True
        self.game_thread = threading.Thread(target=self._game_loop, daemon=True)
        self.game_thread.start()
        
        logger.info(f"Started game {game_id} with {len(ready_players)} players")
        return True
    
    def stop_game(self) -> None:
        """Stop the current game"""
        if not self.game_running:
            return
        
        self.game_running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=5)
        
        # Finish game in scoreboard
        if self.scoreboard.is_game_active():
            game_result = self.scoreboard.finish_game()
            logger.info(f"Game {game_result.game_id} finished. Winner: {game_result.winner_id}")
        
        # Reset players
        self.player_manager.reset_all_players()
        
        # Reset game state
        self.current_game_id = None
        self.game_phase = GamePhase.WAITING
        self.current_question = None
        self.answers_received.clear()
        
        logger.info("Game stopped")
    
    def _game_loop(self) -> None:
        """Main game loop"""
        try:
            # Countdown phase
            self._start_countdown()
            
            # Question phases
            while (self.game_running and 
                   self.questions_asked < self.game_config.questions_per_game and
                   len(self.player_manager.get_playing_players()) >= self.game_config.min_players):
                
                self._ask_question()
                if not self.game_running:
                    break
                
                self._wait_for_answers()
                if not self.game_running:
                    break
                
                self._review_answers()
                if not self.game_running:
                    break
            
            # End game
            self._end_game()
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            self.stop_game()
    
    def _start_countdown(self) -> None:
        """Start countdown phase"""
        self.game_phase = GamePhase.COUNTDOWN
        self.scoreboard.start_playing()
        
        logger.info("Starting countdown...")
        
        # Broadcast countdown
        for i in range(self.game_config.countdown_duration, 0, -1):
            if not self.game_running:
                return
            
            self._broadcast({
                'type': 'countdown',
                'seconds': i,
                'game_id': self.current_game_id
            })
            time.sleep(1)
        
        self._broadcast({
            'type': 'game_start',
            'game_id': self.current_game_id,
            'total_questions': self.game_config.questions_per_game
        })
    
    def _ask_question(self) -> None:
        """Ask a new question"""
        self.game_phase = GamePhase.QUESTION
        self.answers_received.clear()
        
        # Get random question
        self.current_question = self.question_bank.get_random_question()
        if not self.current_question:
            logger.error("No questions available")
            self.stop_game()
            return
        
        self.question_start_time = time.time()
        self.questions_asked += 1
        
        # Prepare question data
        question_data = {
            'type': 'question',
            'question_id': self.current_question.id,
            'question': self.current_question.question,
            'options': self.current_question.options,
            'time_limit': self.current_question.time_limit,
            'question_number': self.questions_asked,
            'total_questions': self.game_config.questions_per_game
        }
        
        logger.info(f"Asking question {self.questions_asked}: {self.current_question.question[:50]}...")
        
        # Broadcast question
        self._broadcast(question_data)
    
    def _wait_for_answers(self) -> None:
        """Wait for players to answer the current question"""
        if not self.current_question:
            return
        
        time_limit = self.current_question.time_limit
        start_time = time.time()
        
        while time.time() - start_time < time_limit and self.game_running:
            # Check if all players have answered
            playing_players = self.player_manager.get_playing_players()
            if len(self.answers_received) >= len(playing_players):
                break
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
        
        logger.info(f"Question phase ended. Received {len(self.answers_received)} answers")
    
    def _review_answers(self) -> None:
        """Review and process answers"""
        self.game_phase = GamePhase.ANSWER_REVIEW
        
        if not self.current_question:
            return
        
        # Process answers and calculate scores
        correct_answers = []
        incorrect_answers = []
        
        for player_id, answer_data in self.answers_received.items():
            player = self.player_manager.get_player(player_id)
            if not player:
                continue
            
            answer = answer_data.get('answer', '')
            answer_time = answer_data.get('answer_time', 0)
            is_correct = answer == self.current_question.correct_answer
            
            # Record answer in scoreboard
            self.scoreboard.record_answer(
                player_id=player_id,
                is_correct=is_correct,
                answer_time=answer_time,
                points=self.current_question.points if is_correct else 0
            )
            
            # Record in player stats
            player.record_answer(is_correct, answer_time, 
                               self.current_question.points if is_correct else 0)
            
            if is_correct:
                correct_answers.append({
                    'player_id': player_id,
                    'player_name': player.name,
                    'answer_time': answer_time
                })
            else:
                incorrect_answers.append({
                    'player_id': player_id,
                    'player_name': player.name,
                    'answer': answer
                })
        
        # Sort correct answers by speed
        correct_answers.sort(key=lambda x: x['answer_time'])
        
        # Prepare review data
        review_data = {
            'type': 'answer_review',
            'correct_answer': self.current_question.correct_answer,
            'explanation': self.current_question.explanation,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'current_rankings': self.scoreboard.get_current_rankings()
        }
        
        logger.info(f"Answer review: {len(correct_answers)} correct, {len(incorrect_answers)} incorrect")
        
        # Broadcast review
        self._broadcast(review_data)
        
        # Wait for review duration
        time.sleep(self.game_config.answer_review_duration)
    
    def _end_game(self) -> None:
        """End the game and show final results"""
        self.game_phase = GamePhase.GAME_END
        
        # Finish game in scoreboard
        game_result = self.scoreboard.finish_game()
        
        # Update player statistics
        winner = self.player_manager.get_player(game_result.winner_id) if game_result.winner_id else None
        for player in self.player_manager.get_playing_players():
            won = player.id == game_result.winner_id
            player.record_game_result(won, player.score)
        
        # Prepare final results
        final_results = {
            'type': 'game_end',
            'game_id': self.current_game_id,
            'winner': {
                'id': game_result.winner_id,
                'name': winner.name if winner else None,
                'score': game_result.winner_score
            },
            'final_rankings': self.scoreboard.get_current_rankings(),
            'game_statistics': self.scoreboard.get_game_statistics(),
            'game_duration': game_result.game_duration
        }
        
        logger.info(f"Game ended. Winner: {winner.name if winner else 'None'}")
        
        # Broadcast final results
        self._broadcast(final_results)
        
        # Reset players
        self.player_manager.reset_all_players()
        
        # Stop game
        self.game_running = False
    
    def handle_player_answer(self, player_id: str, answer: str, answer_time: float) -> bool:
        """
        Handle a player's answer
        
        Args:
            player_id: Player ID
            answer: Player's answer
            answer_time: Time taken to answer
            
        Returns:
            True if answer was processed, False otherwise
        """
        if self.game_phase != GamePhase.QUESTION:
            logger.warning(f"Received answer from {player_id} but not in question phase")
            return False
        
        if player_id in self.answers_received:
            logger.warning(f"Player {player_id} already answered")
            return False
        
        # Record answer
        self.answers_received[player_id] = {
            'answer': answer,
            'answer_time': answer_time,
            'timestamp': time.time()
        }
        
        logger.debug(f"Player {player_id} answered: {answer} in {answer_time:.2f}s")
        return True
    
    def add_player_to_game(self, player_id: str) -> bool:
        """
        Add a player to the current game
        
        Args:
            player_id: Player ID to add
            
        Returns:
            True if added successfully, False otherwise
        """
        player = self.player_manager.get_player(player_id)
        if not player:
            return False
        
        if self.game_phase != GamePhase.WAITING:
            logger.warning(f"Cannot add player {player_id} - game already started")
            return False
        
        player.status = PlayerStatus.READY
        self.scoreboard.add_waiting_player(player_id, player.name)
        
        logger.info(f"Added player {player.name} to game")
        return True
    
    def remove_player_from_game(self, player_id: str) -> bool:
        """
        Remove a player from the current game
        
        Args:
            player_id: Player ID to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        player = self.player_manager.get_player(player_id)
        if not player:
            return False
        
        if self.game_phase == GamePhase.WAITING:
            self.scoreboard.remove_waiting_player(player_id)
        else:
            player.status = PlayerStatus.FINISHED
        
        logger.info(f"Removed player {player.name} from game")
        return True
    
    def get_game_status(self) -> Dict[str, Any]:
        """Get current game status"""
        return {
            'game_id': self.current_game_id,
            'phase': self.game_phase.value,
            'questions_asked': self.questions_asked,
            'total_questions': self.game_config.questions_per_game,
            'players_count': len(self.player_manager.get_playing_players()),
            'scoreboard': self.scoreboard.export_scoreboard(),
            'game_running': self.game_running
        }
    
    def _broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all players"""
        if self.broadcast_callback:
            try:
                self.broadcast_callback(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
    
    def _send_to_player(self, player_id: str, message: Dict[str, Any]) -> None:
        """Send message to specific player"""
        if self.send_to_player_callback:
            try:
                self.send_to_player_callback(player_id, message)
            except Exception as e:
                logger.error(f"Error sending message to player {player_id}: {e}")
    
    def update_config(self, config: GameConfig) -> None:
        """Update game configuration"""
        self.game_config = config
        logger.info("Game configuration updated")
    
    def get_available_questions_count(self) -> int:
        """Get number of available questions"""
        return len(self.question_bank.questions)
    
    def is_game_full(self) -> bool:
        """Check if game is full"""
        return len(self.player_manager.get_ready_players()) >= self.game_config.max_players
    
    def can_start_game(self) -> bool:
        """Check if game can be started"""
        ready_players = self.player_manager.get_ready_players()
        return (len(ready_players) >= self.game_config.min_players and 
                not self.game_running) 