"""
GUI Interface cho Fastest Finger First sử dụng Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from ui.ui_base import UIBase
from client.config import ClientState

class GUIInterface(UIBase):
    """Giao diện GUI cho game"""
    
    def __init__(self, view_model):
        super().__init__(view_model)
        self.root = None
        self.update_thread = None
        self.status_label = None
        self.question_label = None
        self.answer_var = None
        self.leaderboard_text = None
    
    def start(self):
        """Khởi động GUI"""
        self.root = tk.Tk()
        self.setup_gui()
        self.running = True
        
        # Khởi động update thread
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Chạy GUI
        self.root.mainloop()
    
    def stop(self):
        """Dừng GUI"""
        self.running = False
        if self.root:
            self.root.quit()
    
    def setup_gui(self):
        """Thiết lập giao diện GUI"""
        self.root.title("Fastest Finger First")
        self.root.geometry("600x400")
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status
        self.status_label = ttk.Label(main_frame, text="Disconnected", font=("Arial", 12))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=5)
        
        # Question area
        question_frame = ttk.LabelFrame(main_frame, text="Question", padding="10")
        question_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.question_label = ttk.Label(question_frame, text="Waiting for question...", wraplength=500)
        self.question_label.pack()
        
        # Answer area
        answer_frame = ttk.LabelFrame(main_frame, text="Your Answer", padding="10")
        answer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.answer_var = tk.StringVar()
        answer_entry = ttk.Entry(answer_frame, textvariable=self.answer_var, font=("Arial", 14))
        answer_entry.pack(side=tk.LEFT, padx=(0, 10))
        answer_entry.bind('<Return>', self.submit_answer)
        
        submit_btn = ttk.Button(answer_frame, text="Submit", command=self.submit_answer)
        submit_btn.pack(side=tk.LEFT)
        
        # Leaderboard
        leaderboard_frame = ttk.LabelFrame(main_frame, text="Leaderboard", padding="10")
        leaderboard_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.leaderboard_text = tk.Text(leaderboard_frame, height=8, width=50)
        self.leaderboard_text.pack()
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Connect", command=self.connect).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Join Room", command=self.join_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Leave Room", command=self.leave_room).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Quit", command=self.stop).pack(side=tk.LEFT, padx=5)
    
    def _update_loop(self):
        """Vòng lặp cập nhật GUI"""
        while self.running:
            try:
                self.root.after(0, self.update_gui)
                time.sleep(0.1)
            except:
                break
    
    def update_gui(self):
        """Cập nhật giao diện"""
        if not self.root:
            return
        
        # Cập nhật trạng thái
        state = self.view_model.get_state()
        self.status_label.config(text=f"Status: {state}")
        
        # Cập nhật câu hỏi
        question = self.view_model.get_current_question()
        if question:
            question_text = f"Question {question.get('question_number', '?')}: {question.get('question_text', '')}\n\n"
            options = question.get('options', [])
            for i, option in enumerate(options):
                question_text += f"{chr(ord('A') + i)}. {option}\n"
            self.question_label.config(text=question_text)
        
        # Cập nhật leaderboard
        leaderboard = self.view_model.get_leaderboard()
        if leaderboard:
            leaderboard_text = "Rank | Player | Score\n" + "-" * 30 + "\n"
            for i, player in enumerate(leaderboard[:10], 1):
                leaderboard_text += f"{i:2d}   | {player['username']:<10} | {player['score']:>5}\n"
            self.leaderboard_text.delete(1.0, tk.END)
            self.leaderboard_text.insert(1.0, leaderboard_text)
    
    def submit_answer(self, event=None):
        """Gửi đáp án"""
        answer = self.answer_var.get().strip().upper()
        if answer in ['A', 'B', 'C', 'D', '1', '2', '3', '4']:
            # Chuyển đổi số thành chữ cái
            answer_map = {'1': 'A', '2': 'B', '3': 'C', '4': 'D'}
            final_answer = answer_map.get(answer, answer)
            
            if self.view_model.submit_answer(final_answer):
                messagebox.showinfo("Success", f"Submitted answer: {final_answer}")
            else:
                messagebox.showerror("Error", "Failed to submit answer")
            
            self.answer_var.set("")
        else:
            messagebox.showwarning("Invalid Answer", "Please use A, B, C, D or 1, 2, 3, 4")
    
    def connect(self):
        """Kết nối server"""
        if self.view_model.connect_to_server():
            messagebox.showinfo("Success", "Connected to server")
        else:
            messagebox.showerror("Error", "Failed to connect")
    
    def join_room(self):
        """Tham gia phòng"""
        if self.view_model.join_room():
            messagebox.showinfo("Success", "Joined room")
        else:
            messagebox.showerror("Error", "Failed to join room")
    
    def leave_room(self):
        """Rời phòng"""
        if self.view_model.leave_room():
            messagebox.showinfo("Success", "Left room")
        else:
            messagebox.showerror("Error", "Failed to leave room")
    
    # UI Event Handlers
    def on_state_changed(self, new_state: str):
        """Xử lý thay đổi trạng thái"""
        pass
    
    def on_question_received(self, question_data: dict):
        """Xử lý nhận câu hỏi"""
        pass
    
    def on_score_updated(self, results: dict):
        """Xử lý cập nhật điểm"""
        pass
    
    def on_leaderboard_updated(self, leaderboard: list):
        """Xử lý cập nhật bảng xếp hạng"""
        pass
    
    def on_game_started(self, data: dict):
        """Xử lý bắt đầu game"""
        messagebox.showinfo("Game Started", "The game has begun!")
    
    def on_game_ended(self, final_results: dict):
        """Xử lý kết thúc game"""
        winner = final_results.get('winner', 'Unknown')
        messagebox.showinfo("Game Ended", f"Game ended! Winner: {winner}")
    
    def on_error_occurred(self, error_message: str):
        """Xử lý lỗi"""
        messagebox.showerror("Error", error_message)
    
    def on_info_received(self, info_message: str):
        """Xử lý thông tin"""
        pass
    
    def update(self):
        """Cập nhật UI"""
        pass 