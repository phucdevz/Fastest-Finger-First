#!/usr/bin/env python3
"""
Fastest Finger First - Server Main Entry Point
Entry point khởi động server

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import sys
import os
import signal
import argparse
import logging
import logging.handlers
from typing import Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.model.question import QuestionBank
from server.model.player import PlayerManager
from server.viewmodel.game_manager import GameManager, GameConfig
from server.viewmodel.network_manager import NetworkManager
from server.utils.helpers import ConfigManager, file_manager
from server.view.server_ui import ServerUI

class FastestFingerFirstServer:
    """
    Main server class for Fastest Finger First game
    
    Features:
    - Complete server lifecycle management
    - Configuration management
    - Logging setup
    - Graceful shutdown
    - Health monitoring
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize server
        
        Args:
            config_file: Optional path to configuration file
        """
        self.config_file = config_file or 'config.json'
        self.config_manager = ConfigManager(self.config_file)
        
        # Initialize components
        self.question_bank: Optional[QuestionBank] = None
        self.player_manager: Optional[PlayerManager] = None
        self.game_manager: Optional[GameManager] = None
        self.network_manager: Optional[NetworkManager] = None
        self.server_ui: Optional[ServerUI] = None
        
        # Server state
        self.running = False
        
        # Setup logging
        self._setup_logging()
        
        logger = logging.getLogger(__name__)
        logger.info("Fastest Finger First Server initializing...")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration"""
        log_level = self.config_manager.get('logging.level', 'INFO')
        log_file = self.config_manager.get('logging.file', 'server.log')
        max_size = self.config_manager.get('logging.max_size', 10485760)  # 10MB
        backup_count = self.config_manager.get('logging.backup_count', 5)
        
        # Create logs directory if needed
        dir_name = os.path.dirname(log_file)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=max_size, backupCount=backup_count
                ),
                logging.StreamHandler()
            ]
        )
    
    def initialize_components(self) -> bool:
        """
        Initialize all server components
        
        Returns:
            True if initialization successful, False otherwise
        """
        logger = logging.getLogger(__name__)
        
        try:
            # Validate configuration
            config_errors = self.config_manager.validate_config()
            if config_errors:
                logger.error(f"Configuration errors: {config_errors}")
                return False
            
            # Initialize question bank
            questions_file = self.config_manager.get('data.questions_file', 'data/questions.json')
            self.question_bank = QuestionBank(questions_file)
            logger.info(f"Question bank initialized with {len(self.question_bank.questions)} questions")
            
            # Initialize player manager
            self.player_manager = PlayerManager()
            logger.info("Player manager initialized")
            
            # Initialize game manager
            game_config = GameConfig(
                min_players=self.config_manager.get('game.min_players', 2),
                max_players=self.config_manager.get('game.max_players', 10),
                questions_per_game=self.config_manager.get('game.questions_per_game', 10),
                question_time_limit=self.config_manager.get('game.question_time_limit', 30),
                countdown_duration=self.config_manager.get('game.countdown_duration', 5),
                answer_review_duration=self.config_manager.get('game.answer_review_duration', 3)
            )
            
            self.game_manager = GameManager(self.question_bank, self.player_manager)
            self.game_manager.update_config(game_config)
            logger.info("Game manager initialized")
            
            # Initialize network manager
            host = self.config_manager.get('server.host', 'localhost')
            port = self.config_manager.get('server.port', 5000)
            
            self.network_manager = NetworkManager(
                self.player_manager, 
                self.game_manager,
                host=host,
                port=port
            )
            logger.info(f"Network manager initialized for {host}:{port}")
            
            # Initialize server UI (optional)
            try:
                self.server_ui = ServerUI(self.game_manager, self.network_manager)
                logger.info("Server UI initialized")
            except Exception as e:
                logger.warning(f"Server UI initialization failed: {e}")
            
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Component initialization failed: {e}")
            return False
    
    def start(self) -> None:
        """Start the server"""
        logger = logging.getLogger(__name__)
        
        if not self.initialize_components():
            logger.error("Failed to initialize components")
            sys.exit(1)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self.running = True
        logger.info("Starting Fastest Finger First Server...")
        
        try:
            # Start network manager (this will block)
            self.network_manager.start_server()
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the server gracefully"""
        logger = logging.getLogger(__name__)
        
        if not self.running:
            return
        
        logger.info("Stopping server...")
        self.running = False
        
        # Stop game manager
        if self.game_manager:
            self.game_manager.stop_game()
            logger.info("Game manager stopped")
        
        # Stop network manager
        if self.network_manager:
            self.network_manager.stop_server()
            logger.info("Network manager stopped")
        
        # Save player statistics
        if self.player_manager:
            self.player_manager.save_player_stats()
            logger.info("Player statistics saved")
        
        logger.info("Server stopped")
    
    def _signal_handler(self, signum, frame) -> None:
        """Handle shutdown signals"""
        logger = logging.getLogger(__name__)
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def get_status(self) -> dict:
        """Get server status information"""
        if not self.running:
            return {'status': 'stopped'}
        
        status = {
            'status': 'running',
            'uptime': 0,  # TODO: Calculate uptime
            'components': {}
        }
        
        if self.question_bank:
            status['components']['question_bank'] = {
                'questions_count': len(self.question_bank.questions),
                'categories': list(self.question_bank.categories)
            }
        
        if self.player_manager:
            status['components']['player_manager'] = {
                'total_players': len(self.player_manager),
                'active_players': len(self.player_manager.get_active_players())
            }
        
        if self.game_manager:
            status['components']['game_manager'] = self.game_manager.get_game_status()
        
        if self.network_manager:
            status['components']['network_manager'] = self.network_manager.get_server_status()
        
        return status

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Fastest Finger First Server')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--host', help='Server host address')
    parser.add_argument('--port', type=int, help='Server port')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Logging level')
    
    args = parser.parse_args()
    
    # Create server instance
    server = FastestFingerFirstServer(args.config)
    
    # Override config with command line arguments
    if args.host:
        server.config_manager.set('server.host', args.host)
    if args.port:
        server.config_manager.set('server.port', args.port)
    if args.log_level:
        server.config_manager.set('logging.level', args.log_level)
    
    # Start server
    server.start()

if __name__ == "__main__":
    main() 