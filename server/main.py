#!/usr/bin/env python3
"""
Fastest Finger First - Server Main Entry Point
Entry point khởi động server

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.viewmodel.network_manager import NetworkManager
from server.viewmodel.game_manager import GameManager
from server.view.server_ui import ServerUI
import logging

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('server.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main server entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting Fastest Finger First Server...")
        
        # Initialize game manager
        game_manager = GameManager()
        
        # Initialize network manager
        network_manager = NetworkManager(game_manager)
        
        # Initialize server UI (optional)
        server_ui = ServerUI(game_manager, network_manager)
        
        # Start the server
        network_manager.start_server()
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 