"""
ViewModel cho client Fastest Finger First
Xử lý logic nghiệp vụ và quản lý trạng thái
"""

import time
import logging
from typing import Dict, List, Optional, Callable
from client.config import MessageType, ClientState, DEFAULT_USERNAME, AUTO_JOIN_ROOM
from client.network import NetworkManager

class GameViewModel:
    """ViewModel chính quản lý logic game"""
    
    def __init__(self):
        self.network = NetworkManager()
        self.logger = logging.getLogger(__name__)
        
        # Trạng thái client
        self.state = ClientState.DISCONNECTED
        self.username = DEFAULT_USERNAME
        
        # Dữ liệu game
        self.current_question = None
        self.leaderboard = []
        self.game_status = {}
        self.final_results = None
        
        # Thông tin người chơi
        self.player_score = 0
        self.player_rank = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        
        # Callbacks cho UI
        self.ui_callbacks: Dict[str, List[Callable]] = {
            'state_changed': [],
            'question_received': [],
            'score_updated': [],
            'leaderboard_updated': [],
            'game_started': [],
            'game_ended': [],
            'error_occurred': [],
            'info_received': []
        }
        
        # Thiết lập message handlers
        self._setup_message_handlers()
        self._setup_connection_handlers()
    
    def _setup_message_handlers(self):
        """Thiết lập các handler cho message từ server"""
        self.network.register_message_handler(MessageType.CONNECT, self._handle_connect)
        self.network.register_message_handler(MessageType.JOIN_ROOM, self._handle_join_room)
        self.network.register_message_handler(MessageType.QUESTION, self._handle_question)
        self.network.register_message_handler(MessageType.SCORE_UPDATE, self._handle_score_update)
        self.network.register_message_handler(MessageType.LEADERBOARD, self._handle_leaderboard)
        self.network.register_message_handler(MessageType.GAME_START, self._handle_game_start)
        self.network.register_message_handler(MessageType.GAME_END, self._handle_game_end)
        self.network.register_message_handler(MessageType.ERROR, self._handle_error)
        self.network.register_message_handler(MessageType.INFO, self._handle_info)
    
    def _setup_connection_handlers(self):
        """Thiết lập các handler cho sự kiện kết nối"""
        self.network.register_connection_handler('connected', self._handle_connected)
        self.network.register_connection_handler('disconnected', self._handle_disconnected)
        self.network.register_connection_handler('failed', self._handle_connection_failed)
    
    def connect_to_server(self, username: str = None) -> bool:
        """Kết nối đến server"""
        if username:
            self.username = username
        
        self.state = ClientState.CONNECTING
        self._notify_ui('state_changed', self.state)
        
        success = self.network.connect()
        if success:
            # Gửi message kết nối
            self.network.send_message(MessageType.CONNECT, {
                'username': self.username
            })
        
        return success
    
    def disconnect_from_server(self):
        """Ngắt kết nối khỏi server"""
        self.network.disconnect()
        self.state = ClientState.DISCONNECTED
        self._notify_ui('state_changed', self.state)
    
    def join_room(self) -> bool:
        """Tham gia phòng chơi"""
        if self.state != ClientState.CONNECTED:
            return False
        
        success = self.network.send_message(MessageType.JOIN_ROOM, {})
        if success:
            self.state = ClientState.IN_ROOM
            self._notify_ui('state_changed', self.state)
        
        return success
    
    def leave_room(self) -> bool:
        """Rời khỏi phòng chơi"""
        success = self.network.send_message(MessageType.LEAVE_ROOM, {})
        if success:
            self.state = ClientState.CONNECTED
            self._notify_ui('state_changed', self.state)
        
        return success
    
    def submit_answer(self, answer: str) -> bool:
        """Gửi đáp án"""
        if not self.current_question:
            return False
        
        success = self.network.send_message(MessageType.ANSWER, {
            'answer': answer
        })
        
        if success:
            self.logger.info(f"Submitted answer: {answer}")
        
        return success
    
    def register_ui_callback(self, event: str, callback: Callable):
        """Đăng ký callback cho UI"""
        if event in self.ui_callbacks:
            self.ui_callbacks[event].append(callback)
    
    def _notify_ui(self, event: str, *args):
        """Thông báo cho UI"""
        if event in self.ui_callbacks:
            for callback in self.ui_callbacks[event]:
                try:
                    callback(*args)
                except Exception as e:
                    self.logger.error(f"Error in UI callback {event}: {e}")
    
    # Message handlers
    def _handle_connect(self, data: Dict):
        """Xử lý message kết nối"""
        if data.get('success'):
            self.state = ClientState.CONNECTED
            self._notify_ui('state_changed', self.state)
            
            if AUTO_JOIN_ROOM:
                self.join_room()
        else:
            self._notify_ui('error_occurred', data.get('message', 'Connection failed'))
    
    def _handle_join_room(self, data: Dict):
        """Xử lý message tham gia phòng"""
        if data.get('success'):
            self.state = ClientState.IN_ROOM
            self._notify_ui('state_changed', self.state)
        else:
            self._notify_ui('error_occurred', data.get('message', 'Failed to join room'))
    
    def _handle_question(self, data: Dict):
        """Xử lý message câu hỏi"""
        self.current_question = data
        self.state = ClientState.PLAYING
        self._notify_ui('state_changed', self.state)
        self._notify_ui('question_received', data)
    
    def _handle_score_update(self, data: Dict):
        """Xử lý message cập nhật điểm"""
        results = data.get('results', {})
        leaderboard = data.get('leaderboard', [])
        
        # Cập nhật điểm số người chơi
        if self.username in results:
            result = results[self.username]
            self.player_score = result.get('total_score', 0)
            if result.get('correct'):
                self.correct_answers += 1
            else:
                self.wrong_answers += 1
        
        self.leaderboard = leaderboard
        self._notify_ui('score_updated', results)
        self._notify_ui('leaderboard_updated', leaderboard)
    
    def _handle_leaderboard(self, data: Dict):
        """Xử lý message bảng xếp hạng"""
        self.leaderboard = data.get('leaderboard', [])
        self._notify_ui('leaderboard_updated', self.leaderboard)
    
    def _handle_game_start(self, data: Dict):
        """Xử lý message bắt đầu game"""
        self.state = ClientState.PLAYING
        self._notify_ui('state_changed', self.state)
        self._notify_ui('game_started', data)
    
    def _handle_game_end(self, data: Dict):
        """Xử lý message kết thúc game"""
        self.state = ClientState.GAME_ENDED
        self.final_results = data.get('final_results', {})
        self.leaderboard = data.get('leaderboard', [])
        
        self._notify_ui('state_changed', self.state)
        self._notify_ui('game_ended', self.final_results)
        self._notify_ui('leaderboard_updated', self.leaderboard)
    
    def _handle_error(self, data: Dict):
        """Xử lý message lỗi"""
        error_message = data.get('message', 'Unknown error')
        self._notify_ui('error_occurred', error_message)
    
    def _handle_info(self, data: Dict):
        """Xử lý message thông tin"""
        info_message = data.get('message', '')
        game_status = data.get('game_status', {})
        leaderboard = data.get('leaderboard', [])
        
        if game_status:
            self.game_status = game_status
        
        if leaderboard:
            self.leaderboard = leaderboard
            self._notify_ui('leaderboard_updated', leaderboard)
        
        if info_message:
            self._notify_ui('info_received', info_message)
    
    # Connection handlers
    def _handle_connected(self):
        """Xử lý sự kiện kết nối thành công"""
        self.state = ClientState.CONNECTED
        self._notify_ui('state_changed', self.state)
    
    def _handle_disconnected(self):
        """Xử lý sự kiện ngắt kết nối"""
        self.state = ClientState.DISCONNECTED
        self.current_question = None
        self._notify_ui('state_changed', self.state)
    
    def _handle_connection_failed(self, error: str):
        """Xử lý sự kiện kết nối thất bại"""
        self.state = ClientState.DISCONNECTED
        self._notify_ui('error_occurred', f"Connection failed: {error}")
        self._notify_ui('state_changed', self.state)
    
    # Getters
    def get_state(self) -> str:
        """Lấy trạng thái hiện tại"""
        return self.state
    
    def get_username(self) -> str:
        """Lấy tên người chơi"""
        return self.username
    
    def get_current_question(self) -> Optional[Dict]:
        """Lấy câu hỏi hiện tại"""
        return self.current_question
    
    def get_leaderboard(self) -> List[Dict]:
        """Lấy bảng xếp hạng"""
        return self.leaderboard
    
    def get_game_status(self) -> Dict:
        """Lấy trạng thái game"""
        return self.game_status
    
    def get_final_results(self) -> Optional[Dict]:
        """Lấy kết quả cuối cùng"""
        return self.final_results
    
    def get_player_stats(self) -> Dict:
        """Lấy thống kê người chơi"""
        return {
            'score': self.player_score,
            'correct_answers': self.correct_answers,
            'wrong_answers': self.wrong_answers,
            'rank': self.player_rank
        }
    
    def is_connected(self) -> bool:
        """Kiểm tra có kết nối không"""
        return self.network.is_connected
    
    def is_in_game(self) -> bool:
        """Kiểm tra có đang trong game không"""
        return self.state in [ClientState.PLAYING, ClientState.IN_ROOM]
    
    def can_submit_answer(self) -> bool:
        """Kiểm tra có thể gửi đáp án không"""
        return (self.state == ClientState.PLAYING and 
                self.current_question is not None)
    
    def reset_game_data(self):
        """Reset dữ liệu game"""
        self.current_question = None
        self.player_score = 0
        self.correct_answers = 0
        self.wrong_answers = 0
        self.final_results = None
        self.game_status = {} 