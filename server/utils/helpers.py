"""
Helper Utilities - Hàm tiện ích, đọc file câu hỏi, format message, ...

Phụ trách: Nguyễn Trường Phục
Vai trò: Backend/Server & Database Developer
"""

import json
import os
import time
import hashlib
import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration manager for server settings
    
    Features:
    - Load/save configuration from JSON file
    - Default configuration values
    - Configuration validation
    - Hot-reload support
    """
    
    DEFAULT_CONFIG = {
        'server': {
            'host': 'localhost',
            'port': 5000,
            'max_connections': 50,
            'timeout': 60
        },
        'game': {
            'min_players': 2,
            'max_players': 10,
            'questions_per_game': 10,
            'question_time_limit': 30,
            'countdown_duration': 5,
            'answer_review_duration': 3
        },
        'logging': {
            'level': 'INFO',
            'file': 'server.log',
            'max_size': 10485760,  # 10MB
            'backup_count': 5
        },
        'data': {
            'questions_file': 'data/questions.json',
            'player_stats_file': 'data/player_stats.json',
            'game_history_file': 'data/game_history.json'
        }
    }
    
    def __init__(self, config_file: str = 'config.json'):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                    self._merge_config(file_config)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                self.save_config()
                logger.info(f"Created default configuration at {self.config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            dir_name = os.path.dirname(self.config_file)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def _merge_config(self, new_config: Dict[str, Any]) -> None:
        """Merge new configuration with existing config"""
        for section, values in new_config.items():
            if section in self.config:
                if isinstance(values, dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
            else:
                self.config[section] = values
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'server.port')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value using dot notation
        
        Args:
            key: Configuration key (e.g., 'server.port')
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate_config(self) -> List[str]:
        """
        Validate configuration values
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Validate server config
        port = self.get('server.port')
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors.append("Invalid server port")
        
        max_connections = self.get('server.max_connections')
        if not isinstance(max_connections, int) or max_connections < 1:
            errors.append("Invalid max connections")
        
        # Validate game config
        min_players = self.get('game.min_players')
        max_players = self.get('game.max_players')
        if min_players >= max_players:
            errors.append("min_players must be less than max_players")
        
        return errors

class MessageFormatter:
    """
    Message formatting utilities
    
    Features:
    - JSON message formatting
    - Message validation
    - Error message formatting
    - Response formatting
    """
    
    @staticmethod
    def format_message(message_type: str, data: Dict[str, Any], 
                      player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Format a standard message
        
        Args:
            message_type: Type of message
            data: Message data
            player_id: Optional player ID
            
        Returns:
            Formatted message dictionary
        """
        return {
            'type': message_type,
            'data': data,
            'timestamp': time.time(),
            'player_id': player_id
        }
    
    @staticmethod
    def format_error(error_message: str, error_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Format error message
        
        Args:
            error_message: Error description
            error_code: Optional error code
            
        Returns:
            Formatted error message
        """
        return {
            'type': 'error',
            'data': {
                'message': error_message,
                'code': error_code
            },
            'timestamp': time.time()
        }
    
    @staticmethod
    def format_success(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Format success message
        
        Args:
            message: Success message
            data: Optional additional data
            
        Returns:
            Formatted success message
        """
        result = {'message': message}
        if data:
            result.update(data)
        return {
            'type': 'success',
            'data': result,
            'timestamp': time.time()
        }
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> List[str]:
        """
        Validate message format
        
        Args:
            message: Message to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if 'type' not in message:
            errors.append("Message missing 'type' field")
        
        if 'data' not in message:
            errors.append("Message missing 'data' field")
        
        if 'timestamp' not in message:
            errors.append("Message missing 'timestamp' field")
        
        return errors

class DataValidator:
    """
    Data validation utilities
    
    Features:
    - Input validation
    - Data sanitization
    - Type checking
    """
    
    @staticmethod
    def validate_player_name(name: str) -> tuple[bool, str]:
        """
        Validate player name
        
        Args:
            name: Player name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Player name cannot be empty"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Player name must be at least 2 characters"
        
        if len(name) > 20:
            return False, "Player name must be at most 20 characters"
        
        # Check for invalid characters
        if not re.match(r'^[a-zA-Z0-9_\-\s]+$', name):
            return False, "Player name contains invalid characters"
        
        return True, ""
    
    @staticmethod
    def validate_answer(answer: str, options: List[str]) -> tuple[bool, str]:
        """
        Validate player answer
        
        Args:
            answer: Player's answer
            options: Valid answer options
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not answer or not answer.strip():
            return False, "Answer cannot be empty"
        
        answer = answer.strip()
        
        if answer not in options:
            return False, "Invalid answer option"
        
        return True, ""
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """
        Sanitize user input
        
        Args:
            text: Input text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f]', '', text)
        
        # Trim whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """
        Validate JSON data structure
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            List of missing fields
        """
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
        
        return missing_fields

class FileManager:
    """
    File management utilities
    
    Features:
    - Safe file operations
    - Backup creation
    - File validation
    - Directory management
    """
    
    @staticmethod
    def safe_read_json(file_path: str, default: Any = None) -> Any:
        """
        Safely read JSON file
        
        Args:
            file_path: Path to JSON file
            default: Default value if file doesn't exist or is invalid
            
        Returns:
            Parsed JSON data or default value
        """
        try:
            if not os.path.exists(file_path):
                return default
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return default
    
    @staticmethod
    def safe_write_json(file_path: str, data: Any, backup: bool = True) -> bool:
        """
        Safely write JSON file
        
        Args:
            file_path: Path to JSON file
            data: Data to write
            backup: Whether to create backup before writing
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create backup if requested and file exists
            if backup and os.path.exists(file_path):
                backup_path = f"{file_path}.backup"
                os.replace(file_path, backup_path)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except Exception as e:
            logger.error(f"Error writing JSON file {file_path}: {e}")
            return False
    
    @staticmethod
    def create_backup(file_path: str) -> Optional[str]:
        """
        Create backup of file
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            Backup file path or None if failed
        """
        try:
            if not os.path.exists(file_path):
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}.{timestamp}.backup"
            
            import shutil
            shutil.copy2(file_path, backup_path)
            
            logger.info(f"Created backup: {backup_path}")
            return backup_path
        
        except Exception as e:
            logger.error(f"Error creating backup of {file_path}: {e}")
            return None
    
    @staticmethod
    def cleanup_old_backups(file_path: str, max_backups: int = 5) -> None:
        """
        Clean up old backup files
        
        Args:
            file_path: Base file path
            max_backups: Maximum number of backups to keep
        """
        try:
            backup_pattern = f"{file_path}.*.backup"
            backup_files = []
            
            for file in os.listdir(os.path.dirname(file_path)):
                if file.startswith(os.path.basename(file_path)) and file.endswith('.backup'):
                    backup_files.append(os.path.join(os.path.dirname(file_path), file))
            
            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: os.path.getmtime(x))
            
            # Remove old backups
            while len(backup_files) > max_backups:
                old_backup = backup_files.pop(0)
                try:
                    os.remove(old_backup)
                    logger.info(f"Removed old backup: {old_backup}")
                except Exception as e:
                    logger.error(f"Error removing old backup {old_backup}: {e}")
        
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}")

class SecurityUtils:
    """
    Security utilities
    
    Features:
    - Input sanitization
    - Rate limiting
    - Hash generation
    """
    
    @staticmethod
    def generate_hash(data: str) -> str:
        """
        Generate SHA-256 hash of data
        
        Args:
            data: Data to hash
            
        Returns:
            Hash string
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename for safe file operations
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove or replace dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Remove control characters
        filename = re.sub(r'[\x00-\x1f\x7f]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def validate_file_path(file_path: str) -> bool:
        """
        Validate file path for security
        
        Args:
            file_path: File path to validate
            
        Returns:
            True if path is safe, False otherwise
        """
        # Check for path traversal attempts
        if '..' in file_path or '//' in file_path:
            return False
        
        # Check for absolute paths (if not allowed)
        if os.path.isabs(file_path):
            return False
        
        return True

class TimeUtils:
    """
    Time utility functions
    
    Features:
    - Time formatting
    - Duration calculation
    - Timestamp utilities
    """
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in human-readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"
        else:
            hours = int(seconds // 3600)
            remaining_minutes = int((seconds % 3600) // 60)
            return f"{hours}h {remaining_minutes}m"
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """
        Format timestamp in human-readable format
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted timestamp string
        """
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_time_diff(start_time: float, end_time: Optional[float] = None) -> float:
        """
        Calculate time difference
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp (uses current time if None)
            
        Returns:
            Time difference in seconds
        """
        if end_time is None:
            end_time = time.time()
        return end_time - start_time

# Global instances
config_manager = ConfigManager()
message_formatter = MessageFormatter()
data_validator = DataValidator()
file_manager = FileManager()
security_utils = SecurityUtils()
time_utils = TimeUtils() 