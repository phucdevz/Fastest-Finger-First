"""
Network Manager - Quản lý socket, kết nối đa client

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import socket
import threading
import json
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import select

from server.model.player import PlayerManager, Player, PlayerStatus, PlayerRole
from server.viewmodel.game_manager import GameManager

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for client-server communication"""
    # Connection messages
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    
    # Game control messages
    JOIN_GAME = "join_game"
    LEAVE_GAME = "leave_game"
    START_GAME = "start_game"
    STOP_GAME = "stop_game"
    
    # Gameplay messages
    ANSWER = "answer"
    READY = "ready"
    NOT_READY = "not_ready"
    
    # Status messages
    GET_STATUS = "get_status"
    GET_PLAYERS = "get_players"
    GET_SCOREBOARD = "get_scoreboard"
    
    # Admin messages
    ADMIN_KICK = "admin_kick"
    ADMIN_BAN = "admin_ban"
    ADMIN_MESSAGE = "admin_message"

@dataclass
class NetworkMessage:
    """Network message structure"""
    type: str
    data: Dict[str, Any]
    timestamp: float
    player_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'type': self.type,
            'data': self.data,
            'timestamp': self.timestamp,
            'player_id': self.player_id
        }

class ClientHandler:
    """
    Handler for individual client connections
    
    Features:
    - Message parsing and validation
    - Connection state management
    - Error handling
    """
    
    def __init__(self, connection: socket.socket, address: tuple, 
                 player_manager: PlayerManager, message_handler: Callable):
        """
        Initialize client handler
        
        Args:
            connection: Socket connection
            address: Client address
            player_manager: Player manager instance
            message_handler: Function to handle parsed messages
        """
        self.connection = connection
        self.address = address
        self.player_manager = player_manager
        self.message_handler = message_handler
        
        self.player: Optional[Player] = None
        self.running = False
        self.buffer = ""
        
        # Set socket timeout
        self.connection.settimeout(1.0)
        
        logger.info(f"Client handler created for {address}")
    
    def start(self) -> None:
        """Start handling client messages"""
        self.running = True
        logger.info(f"Started client handler for {self.address}")
        
        try:
            while self.running:
                try:
                    # Receive data
                    data = self.connection.recv(4096)
                    if not data:
                        logger.info(f"Client {self.address} disconnected")
                        break
                    
                    # Decode and process
                    message = data.decode('utf-8')
                    self.buffer += message
                    
                    # Process complete messages
                    while '\n' in self.buffer:
                        line, self.buffer = self.buffer.split('\n', 1)
                        if line.strip():
                            self._process_message(line.strip())
                
                except socket.timeout:
                    # Timeout is expected, continue
                    continue
                except socket.error as e:
                    logger.error(f"Socket error for {self.address}: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error handling client {self.address}: {e}")
                    break
        
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop client handler"""
        self.running = False
        try:
            self.connection.close()
        except:
            pass
        
        # Remove player if connected
        if self.player:
            self.player_manager.disconnect_player(self.player.id)
        
        logger.info(f"Stopped client handler for {self.address}")
    
    def _process_message(self, message_str: str) -> None:
        """
        Process a single message
        
        Args:
            message_str: JSON string message
        """
        try:
            # Parse JSON message
            message_data = json.loads(message_str)
            message_type = message_data.get('type')
            data = message_data.get('data', {})
            
            # Create message object
            message = NetworkMessage(
                type=message_type,
                data=data,
                timestamp=time.time(),
                player_id=self.player.id if self.player else None
            )
            
            # Handle message
            self.message_handler(message, self)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {self.address}: {e}")
            self._send_error("Invalid message format")
        except Exception as e:
            logger.error(f"Error processing message from {self.address}: {e}")
            self._send_error("Internal server error")
    
    def send_message(self, message: Dict[str, Any]) -> bool:
        """
        Send message to client
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            message_str = json.dumps(message) + '\n'
            self.connection.sendall(message_str.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending message to {self.address}: {e}")
            return False
    
    def _send_error(self, error_message: str) -> None:
        """Send error message to client"""
        self.send_message({
            'type': 'error',
            'data': {'message': error_message},
            'timestamp': time.time()
        })

class NetworkManager:
    """
    Network manager for handling socket server and client connections
    
    Features:
    - Multi-threaded socket server
    - Client connection management
    - Message routing
    - Connection monitoring
    - Error handling and recovery
    """
    
    def __init__(self, player_manager: PlayerManager, game_manager: GameManager,
                 host: str = 'localhost', port: int = 5000):
        """
        Initialize network manager
        
        Args:
            player_manager: Player manager instance
            game_manager: Game manager instance
            host: Server host address
            port: Server port
        """
        self.player_manager = player_manager
        self.game_manager = game_manager
        self.host = host
        self.port = port
        
        # Server socket
        self.server_socket: Optional[socket.socket] = None
        self.running = False
        
        # Client handlers
        self.client_handlers: Dict[socket.socket, ClientHandler] = {}
        self.handler_lock = threading.Lock()
        
        # Set up game manager callbacks
        self.game_manager.set_callbacks(
            broadcast_callback=self.broadcast_message,
            send_to_player_callback=self.send_to_player
        )
        
        logger.info(f"Network manager initialized for {host}:{port}")
    
    def start_server(self) -> None:
        """Start the socket server"""
        try:
            # Create server socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.server_socket.settimeout(1.0)
            
            self.running = True
            logger.info(f"Server started on {self.host}:{port}")
            
            # Start connection monitoring thread
            monitor_thread = threading.Thread(target=self._connection_monitor, daemon=True)
            monitor_thread.start()
            
            # Main server loop
            while self.running:
                try:
                    # Accept new connections
                    client_socket, address = self.server_socket.accept()
                    self._handle_new_connection(client_socket, address)
                
                except socket.timeout:
                    # Timeout is expected, continue
                    continue
                except Exception as e:
                    if self.running:
                        logger.error(f"Server error: {e}")
        
        except Exception as e:
            logger.error(f"Failed to start server: {e}")
        finally:
            self.stop_server()
    
    def stop_server(self) -> None:
        """Stop the server and close all connections"""
        self.running = False
        
        # Close all client connections
        with self.handler_lock:
            for handler in self.client_handlers.values():
                handler.stop()
            self.client_handlers.clear()
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        logger.info("Server stopped")
    
    def _handle_new_connection(self, client_socket: socket.socket, address: tuple) -> None:
        """
        Handle new client connection
        
        Args:
            client_socket: Client socket
            address: Client address
        """
        try:
            # Create client handler
            handler = ClientHandler(
                connection=client_socket,
                address=address,
                player_manager=self.player_manager,
                message_handler=self._handle_message
            )
            
            # Add to handlers
            with self.handler_lock:
                self.client_handlers[client_socket] = handler
            
            # Start handler thread
            handler_thread = threading.Thread(target=handler.start, daemon=True)
            handler_thread.start()
            
            logger.info(f"New connection from {address}")
            
        except Exception as e:
            logger.error(f"Error handling new connection from {address}: {e}")
            try:
                client_socket.close()
            except:
                pass
    
    def _handle_message(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """
        Handle incoming message from client
        
        Args:
            message: Parsed message
            handler: Client handler
        """
        try:
            message_type = message.type
            
            if message_type == MessageType.CONNECT.value:
                self._handle_connect(message, handler)
            
            elif message_type == MessageType.JOIN_GAME.value:
                self._handle_join_game(message, handler)
            
            elif message_type == MessageType.LEAVE_GAME.value:
                self._handle_leave_game(message, handler)
            
            elif message_type == MessageType.ANSWER.value:
                self._handle_answer(message, handler)
            
            elif message_type == MessageType.READY.value:
                self._handle_ready(message, handler)
            
            elif message_type == MessageType.GET_STATUS.value:
                self._handle_get_status(message, handler)
            
            elif message_type == MessageType.GET_PLAYERS.value:
                self._handle_get_players(message, handler)
            
            elif message_type == MessageType.START_GAME.value:
                self._handle_start_game(message, handler)
            
            elif message_type == MessageType.ADMIN_KICK.value:
                self._handle_admin_kick(message, handler)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                handler._send_error(f"Unknown message type: {message_type}")
        
        except Exception as e:
            logger.error(f"Error handling message {message.type}: {e}")
            handler._send_error("Internal server error")
    
    def _handle_connect(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle client connection request"""
        data = message.data
        player_name = data.get('player_name', '').strip()
        
        if not player_name:
            handler._send_error("Player name is required")
            return
        
        # Check if name is already taken
        existing_player = self.player_manager.get_player_by_name(player_name)
        if existing_player and existing_player.connection:
            handler._send_error("Player name already in use")
            return
        
        # Add or reconnect player
        player = self.player_manager.add_player(player_name, handler.connection)
        handler.player = player
        
        # Send connection confirmation
        handler.send_message({
            'type': 'connected',
            'data': {
                'player_id': player.id,
                'player_name': player.name,
                'server_status': self.game_manager.get_game_status()
            },
            'timestamp': time.time()
        })
        
        logger.info(f"Player {player_name} connected (ID: {player.id})")
    
    def _handle_join_game(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle player join game request"""
        if not handler.player:
            handler._send_error("Not connected")
            return
        
        success = self.game_manager.add_player_to_game(handler.player.id)
        if success:
            handler.send_message({
                'type': 'joined_game',
                'data': {'game_status': self.game_manager.get_game_status()},
                'timestamp': time.time()
            })
        else:
            handler._send_error("Cannot join game")
    
    def _handle_leave_game(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle player leave game request"""
        if not handler.player:
            handler._send_error("Not connected")
            return
        
        success = self.game_manager.remove_player_from_game(handler.player.id)
        if success:
            handler.send_message({
                'type': 'left_game',
                'data': {'message': 'Left game successfully'},
                'timestamp': time.time()
            })
        else:
            handler._send_error("Cannot leave game")
    
    def _handle_answer(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle player answer"""
        if not handler.player:
            handler._send_error("Not connected")
            return
        
        data = message.data
        answer = data.get('answer', '')
        answer_time = data.get('answer_time', 0)
        
        success = self.game_manager.handle_player_answer(
            handler.player.id, answer, answer_time
        )
        
        if success:
            handler.send_message({
                'type': 'answer_received',
                'data': {'message': 'Answer received'},
                'timestamp': time.time()
            })
        else:
            handler._send_error("Cannot process answer")
    
    def _handle_ready(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle player ready status"""
        if not handler.player:
            handler._send_error("Not connected")
            return
        
        handler.player.status = PlayerStatus.READY
        handler.send_message({
            'type': 'ready_status',
            'data': {'status': 'ready'},
            'timestamp': time.time()
        })
    
    def _handle_get_status(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle status request"""
        handler.send_message({
            'type': 'status',
            'data': self.game_manager.get_game_status(),
            'timestamp': time.time()
        })
    
    def _handle_get_players(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle players list request"""
        handler.send_message({
            'type': 'players',
            'data': self.player_manager.get_players_dict(),
            'timestamp': time.time()
        })
    
    def _handle_start_game(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle start game request (admin only)"""
        if not handler.player or handler.player.role != PlayerRole.ADMIN:
            handler._send_error("Admin privileges required")
            return
        
        success = self.game_manager.start_game()
        if success:
            handler.send_message({
                'type': 'game_started',
                'data': {'message': 'Game started successfully'},
                'timestamp': time.time()
            })
        else:
            handler._send_error("Cannot start game")
    
    def _handle_admin_kick(self, message: NetworkMessage, handler: ClientHandler) -> None:
        """Handle admin kick request"""
        if not handler.player or handler.player.role != PlayerRole.ADMIN:
            handler._send_error("Admin privileges required")
            return
        
        data = message.data
        target_player_id = data.get('player_id')
        
        if not target_player_id:
            handler._send_error("Player ID required")
            return
        
        target_player = self.player_manager.get_player(target_player_id)
        if not target_player:
            handler._send_error("Player not found")
            return
        
        # Kick player
        self.player_manager.remove_player(target_player_id)
        
        handler.send_message({
            'type': 'player_kicked',
            'data': {'player_id': target_player_id, 'message': 'Player kicked'},
            'timestamp': time.time()
        })
    
    def broadcast_message(self, message: Dict[str, Any]) -> None:
        """
        Broadcast message to all connected players
        
        Args:
            message: Message to broadcast
        """
        with self.handler_lock:
            disconnected_handlers = []
            
            for handler in self.client_handlers.values():
                if not handler.send_message(message):
                    disconnected_handlers.append(handler.connection)
            
            # Remove disconnected handlers
            for connection in disconnected_handlers:
                handler = self.client_handlers.pop(connection, None)
                if handler:
                    handler.stop()
    
    def send_to_player(self, player_id: str, message: Dict[str, Any]) -> bool:
        """
        Send message to specific player
        
        Args:
            player_id: Player ID
            message: Message to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        with self.handler_lock:
            for handler in self.client_handlers.values():
                if handler.player and handler.player.id == player_id:
                    return handler.send_message(message)
        return False
    
    def _connection_monitor(self) -> None:
        """Monitor and clean up disconnected clients"""
        while self.running:
            try:
                time.sleep(30)  # Check every 30 seconds
                
                # Clean up inactive players
                inactive_players = self.player_manager.cleanup_inactive_players()
                if inactive_players:
                    logger.info(f"Cleaned up {len(inactive_players)} inactive players")
                
                # Remove disconnected handlers
                with self.handler_lock:
                    disconnected_handlers = []
                    for connection, handler in self.client_handlers.items():
                        try:
                            # Test connection
                            connection.send(b'')
                        except:
                            disconnected_handlers.append(connection)
                    
                    for connection in disconnected_handlers:
                        handler = self.client_handlers.pop(connection, None)
                        if handler:
                            handler.stop()
                
            except Exception as e:
                logger.error(f"Error in connection monitor: {e}")
    
    def get_server_status(self) -> Dict[str, Any]:
        """Get server status information"""
        with self.handler_lock:
            active_connections = len(self.client_handlers)
        
        return {
            'host': self.host,
            'port': self.port,
            'running': self.running,
            'active_connections': active_connections,
            'total_players': len(self.player_manager),
            'active_players': len(self.player_manager.get_active_players()),
            'game_status': self.game_manager.get_game_status()
        }
    
    def shutdown(self) -> None:
        """Graceful shutdown"""
        logger.info("Shutting down network manager...")
        self.stop_server() 