import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class MainWindow:
    def __init__(self, root, viewmodel):
        self.root = root
        self.viewmodel = viewmodel
        self.current_frame = None
        
        # Bind viewmodel callbacks
        self.viewmodel.on_connection_changed = self._on_connection_changed
        self.viewmodel.on_question_received = self._on_question_received
        self.viewmodel.on_score_updated = self._on_score_updated
        self.viewmodel.on_players_updated = self._on_players_updated
        self.viewmodel.on_leaderboard_updated = self._on_leaderboard_updated
        self.viewmodel.on_game_status_changed = self._on_game_status_changed
        self.viewmodel.on_message_received = self._on_message_received
        
        # Create frames
        self.login_frame = None
        self.lobby_frame = None
        self.game_frame = None
        self.result_frame = None
        
        # Show login frame initially
        self._show_login_frame()
    
    def _show_login_frame(self):
        """Hiển thị frame đăng nhập"""
        if self.current_frame:
            self.current_frame.pack_forget()
        
        self.login_frame = LoginFrame(self.root, self.viewmodel, self._on_login_success)
        self.login_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = self.login_frame
    
    def _show_lobby_frame(self):
        """Hiển thị frame phòng chờ"""
        if self.current_frame:
            self.current_frame.pack_forget()
        
        self.lobby_frame = LobbyFrame(self.root, self.viewmodel, self._on_game_start)
        self.lobby_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = self.lobby_frame
    
    def _show_game_frame(self):
        """Hiển thị frame game"""
        if self.current_frame:
            self.current_frame.pack_forget()
        
        self.game_frame = GameFrame(self.root, self.viewmodel, self._on_game_end)
        self.game_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = self.game_frame
    
    def _show_result_frame(self):
        """Hiển thị frame kết quả"""
        if self.current_frame:
            self.current_frame.pack_forget()
        
        self.result_frame = ResultFrame(self.root, self.viewmodel, self._on_back_to_lobby)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        self.current_frame = self.result_frame
    
    def _on_login_success(self):
        """Callback khi đăng nhập thành công"""
        self._show_lobby_frame()
    
    def _on_game_start(self):
        """Callback khi game bắt đầu"""
        self._show_game_frame()
    
    def _on_game_end(self):
        """Callback khi game kết thúc"""
        self._show_result_frame()
    
    def _on_back_to_lobby(self):
        """Callback khi quay lại phòng chờ"""
        self._show_lobby_frame()
    
    def _on_connection_changed(self, connected):
        """Callback khi trạng thái kết nối thay đổi"""
        if not connected and self.current_frame != self.login_frame:
            messagebox.showerror("Lỗi kết nối", "Mất kết nối đến server!")
            self._show_login_frame()
    
    def _on_question_received(self, question):
        """Callback khi nhận câu hỏi"""
        if self.game_frame:
            self.game_frame.show_question(question)
    
    def _on_score_updated(self, score):
        """Callback khi điểm số cập nhật"""
        if self.game_frame:
            self.game_frame.update_score(score)
    
    def _on_players_updated(self, players):
        """Callback khi danh sách player cập nhật"""
        if self.lobby_frame:
            self.lobby_frame.update_players(players)
    
    def _on_leaderboard_updated(self, leaderboard):
        """Callback khi bảng xếp hạng cập nhật"""
        if self.game_frame:
            self.game_frame.update_leaderboard(leaderboard)
    
    def _on_game_status_changed(self, status):
        """Callback khi trạng thái game thay đổi"""
        if status == "playing" and self.current_frame != self.game_frame:
            self._show_game_frame()
        elif status == "finished" and self.current_frame != self.result_frame:
            self._show_result_frame()
    
    def _on_message_received(self, message):
        """Callback khi nhận message"""
        # Hiển thị message trong status bar hoặc popup
        pass


class LoginFrame(tk.Frame):
    def __init__(self, parent, viewmodel, on_success):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.on_success = on_success
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Tạo các widget cho frame đăng nhập"""
        # Main container
        main_container = tk.Frame(self, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="VUA TỐC ĐỘ",
            font=("Arial", 36, "bold"),
            fg="#FFD700",
            bg="#1a1a1a"
        )
        title_label.pack(pady=(0, 30))
        
        subtitle_label = tk.Label(
            main_container,
            text="Fastest Finger First",
            font=("Arial", 18),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        subtitle_label.pack(pady=(0, 50))
        
        # Login form
        form_frame = tk.Frame(main_container, bg="#1a1a1a")
        form_frame.pack()
        
        # Player name
        name_label = tk.Label(
            form_frame,
            text="Tên người chơi:",
            font=("Arial", 14),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        name_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.name_entry = tk.Entry(
            form_frame,
            font=("Arial", 14),
            width=30,
            bg="#333333",
            fg="#FFFFFF",
            insertbackground="#FFFFFF"
        )
        self.name_entry.pack(pady=(0, 20))
        self.name_entry.insert(0, "Player")
        
        # Room ID
        room_label = tk.Label(
            form_frame,
            text="Mã phòng:",
            font=("Arial", 14),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        room_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.room_entry = tk.Entry(
            form_frame,
            font=("Arial", 14),
            width=30,
            bg="#333333",
            fg="#FFFFFF",
            insertbackground="#FFFFFF"
        )
        self.room_entry.pack(pady=(0, 30))
        self.room_entry.insert(0, "default")
        
        # Connect button
        self.connect_btn = tk.Button(
            form_frame,
            text="KẾT NỐI",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="#FFFFFF",
            width=20,
            height=2,
            command=self._connect
        )
        self.connect_btn.pack()
        
        # Status label
        self.status_label = tk.Label(
            form_frame,
            text="",
            font=("Arial", 12),
            fg="#FF6B6B",
            bg="#1a1a1a"
        )
        self.status_label.pack(pady=(20, 0))
    
    def _connect(self):
        """Kết nối đến server"""
        player_name = self.name_entry.get().strip()
        room_id = self.room_entry.get().strip()
        
        if not player_name:
            self.status_label.config(text="Vui lòng nhập tên người chơi!")
            return
        
        self.connect_btn.config(state=tk.DISABLED, text="Đang kết nối...")
        self.status_label.config(text="Đang kết nối đến server...")
        
        # Connect in separate thread
        def connect_thread():
            success = self.viewmodel.connect_to_server(player_name, room_id)
            self.root.after(0, self._on_connect_result, success)
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _on_connect_result(self, success):
        """Xử lý kết quả kết nối"""
        if success:
            self.on_success()
        else:
            self.connect_btn.config(state=tk.NORMAL, text="KẾT NỐI")
            self.status_label.config(text="Không thể kết nối đến server!")


class LobbyFrame(tk.Frame):
    def __init__(self, parent, viewmodel, on_game_start):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.on_game_start = on_game_start
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Tạo các widget cho frame phòng chờ"""
        # Main container
        main_container = tk.Frame(self, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_container, bg="#1a1a1a")
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = tk.Label(
            header_frame,
            text="PHÒNG CHỜ",
            font=("Arial", 24, "bold"),
            fg="#FFD700",
            bg="#1a1a1a"
        )
        title_label.pack(side=tk.LEFT)
        
        # Room info
        room_info = tk.Label(
            header_frame,
            text=f"Phòng: {self.viewmodel.get_room_id()}",
            font=("Arial", 14),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        room_info.pack(side=tk.RIGHT)
        
        # Players list
        players_frame = tk.Frame(main_container, bg="#1a1a1a")
        players_frame.pack(fill=tk.BOTH, expand=True)
        
        players_label = tk.Label(
            players_frame,
            text="NGƯỜI CHƠI",
            font=("Arial", 18, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        players_label.pack(pady=(0, 20))
        
        # Players listbox
        self.players_listbox = tk.Listbox(
            players_frame,
            font=("Arial", 14),
            bg="#333333",
            fg="#FFFFFF",
            selectbackground="#4CAF50",
            height=8
        )
        self.players_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Ready button
        self.ready_btn = tk.Button(
            main_container,
            text="SẴN SÀNG",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="#FFFFFF",
            width=20,
            height=2,
            command=self._send_ready
        )
        self.ready_btn.pack(pady=(30, 0))
        
        # Status label
        self.status_label = tk.Label(
            main_container,
            text="Chờ người chơi khác...",
            font=("Arial", 12),
            fg="#FFD700",
            bg="#1a1a1a"
        )
        self.status_label.pack(pady=(20, 0))
    
    def update_players(self, players):
        """Cập nhật danh sách player"""
        self.players_listbox.delete(0, tk.END)
        for player in players:
            status = "✓ Sẵn sàng" if player.get('ready') else "⏳ Chờ..."
            self.players_listbox.insert(tk.END, f"{player['name']} - {status}")
    
    def _send_ready(self):
        """Gửi tín hiệu sẵn sàng"""
        self.viewmodel.send_ready()
        self.ready_btn.config(state=tk.DISABLED, text="ĐÃ SẴN SÀNG")
        self.status_label.config(text="Đã sẵn sàng! Chờ người chơi khác...")


class GameFrame(tk.Frame):
    def __init__(self, parent, viewmodel, on_game_end):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.on_game_end = on_game_end
        self.current_question = None
        self.timer_running = False
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Tạo các widget cho frame game"""
        # Main container
        main_container = tk.Frame(self, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header
        header_frame = tk.Frame(main_container, bg="#1a1a1a")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Score
        self.score_label = tk.Label(
            header_frame,
            text="Điểm: 0",
            font=("Arial", 18, "bold"),
            fg="#FFD700",
            bg="#1a1a1a"
        )
        self.score_label.pack(side=tk.LEFT)
        
        # Timer
        self.timer_label = tk.Label(
            header_frame,
            text="Thời gian: 30s",
            font=("Arial", 18, "bold"),
            fg="#FF6B6B",
            bg="#1a1a1a"
        )
        self.timer_label.pack(side=tk.RIGHT)
        
        # Question frame
        self.question_frame = tk.Frame(main_container, bg="#1a1a1a")
        self.question_frame.pack(fill=tk.BOTH, expand=True)
        
        # Question label
        self.question_label = tk.Label(
            self.question_frame,
            text="Chờ câu hỏi...",
            font=("Arial", 20, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a",
            wraplength=800
        )
        self.question_label.pack(pady=(50, 30))
        
        # Options frame
        self.options_frame = tk.Frame(self.question_frame, bg="#1a1a1a")
        self.options_frame.pack()
        
        # Create option buttons
        self.option_buttons = []
        for i in range(4):
            btn = tk.Button(
                self.options_frame,
                text=f"Lựa chọn {i+1}",
                font=("Arial", 16),
                bg="#333333",
                fg="#FFFFFF",
                width=30,
                height=2,
                command=lambda x=i: self._select_answer(x)
            )
            btn.pack(pady=10)
            self.option_buttons.append(btn)
        
        # Leaderboard frame
        leaderboard_frame = tk.Frame(main_container, bg="#1a1a1a")
        leaderboard_frame.pack(fill=tk.X, pady=(30, 0))
        
        leaderboard_label = tk.Label(
            leaderboard_frame,
            text="BẢNG XẾP HẠNG",
            font=("Arial", 16, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        leaderboard_label.pack()
        
        self.leaderboard_text = tk.Text(
            leaderboard_frame,
            height=6,
            font=("Arial", 12),
            bg="#333333",
            fg="#FFFFFF",
            state=tk.DISABLED
        )
        self.leaderboard_text.pack(fill=tk.X)
    
    def show_question(self, question):
        """Hiển thị câu hỏi"""
        self.current_question = question
        
        # Update question text
        self.question_label.config(
            text=f"Câu {question['question_number']}/{question['total_questions']}: {question['question']}"
        )
        
        # Update options
        for i, option in enumerate(question['options']):
            self.option_buttons[i].config(text=f"{i+1}. {option}")
        
        # Start timer
        self._start_timer(question['time_limit'])
    
    def _start_timer(self, duration):
        """Bắt đầu đếm ngược"""
        self.timer_running = True
        self._update_timer(duration)
    
    def _update_timer(self, remaining):
        """Cập nhật timer"""
        if not self.timer_running:
            return
        
        self.timer_label.config(text=f"Thời gian: {remaining}s")
        
        if remaining > 0:
            self.root.after(1000, self._update_timer, remaining - 1)
        else:
            self.timer_running = False
    
    def _select_answer(self, answer):
        """Chọn đáp án"""
        if not self.timer_running:
            return
        
        self.timer_running = False
        self.viewmodel.send_answer(answer)
        
        # Disable all buttons
        for btn in self.option_buttons:
            btn.config(state=tk.DISABLED)
    
    def update_score(self, score):
        """Cập nhật điểm số"""
        self.score_label.config(text=f"Điểm: {score}")
    
    def update_leaderboard(self, leaderboard):
        """Cập nhật bảng xếp hạng"""
        self.leaderboard_text.config(state=tk.NORMAL)
        self.leaderboard_text.delete(1.0, tk.END)
        
        for i, player in enumerate(leaderboard[:5]):  # Top 5
            self.leaderboard_text.insert(tk.END, f"{player['rank']}. {player['name']}: {player['score']} điểm\n")
        
        self.leaderboard_text.config(state=tk.DISABLED)


class ResultFrame(tk.Frame):
    def __init__(self, parent, viewmodel, on_back_to_lobby):
        super().__init__(parent)
        self.viewmodel = viewmodel
        self.on_back_to_lobby = on_back_to_lobby
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Tạo các widget cho frame kết quả"""
        # Main container
        main_container = tk.Frame(self, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="KẾT QUẢ",
            font=("Arial", 36, "bold"),
            fg="#FFD700",
            bg="#1a1a1a"
        )
        title_label.pack(pady=(0, 30))
        
        # Final score
        self.score_label = tk.Label(
            main_container,
            text=f"Điểm cuối cùng: {self.viewmodel.get_score()}",
            font=("Arial", 24, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        self.score_label.pack(pady=(0, 30))
        
        # Leaderboard
        leaderboard_frame = tk.Frame(main_container, bg="#1a1a1a")
        leaderboard_frame.pack(fill=tk.BOTH, expand=True)
        
        leaderboard_label = tk.Label(
            leaderboard_frame,
            text="BẢNG XẾP HẠNG CUỐI CÙNG",
            font=("Arial", 18, "bold"),
            fg="#FFFFFF",
            bg="#1a1a1a"
        )
        leaderboard_label.pack(pady=(0, 20))
        
        self.leaderboard_text = tk.Text(
            leaderboard_frame,
            height=10,
            font=("Arial", 14),
            bg="#333333",
            fg="#FFFFFF",
            state=tk.DISABLED
        )
        self.leaderboard_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        buttons_frame = tk.Frame(main_container, bg="#1a1a1a")
        buttons_frame.pack(pady=(30, 0))
        
        play_again_btn = tk.Button(
            buttons_frame,
            text="CHƠI LẠI",
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="#FFFFFF",
            width=15,
            height=2,
            command=self._play_again
        )
        play_again_btn.pack(side=tk.LEFT, padx=(0, 20))
        
        quit_btn = tk.Button(
            buttons_frame,
            text="THOÁT",
            font=("Arial", 16, "bold"),
            bg="#FF6B6B",
            fg="#FFFFFF",
            width=15,
            height=2,
            command=self._quit_game
        )
        quit_btn.pack(side=tk.RIGHT)
    
    def _play_again(self):
        """Chơi lại"""
        self.on_back_to_lobby()
    
    def _quit_game(self):
        """Thoát game"""
        self.viewmodel.disconnect()
        self.master.quit() 