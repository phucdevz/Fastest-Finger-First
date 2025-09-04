"""
GUI Interface cho Fastest Finger First sử dụng Tkinter (refactor)
- Không sử dụng thread cho UI (Tkinter chạy main thread)
- Tối ưu layout, style, và cập nhật định kỳ bằng `after`
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Any, Dict, List, Optional
import time

from ui.ui_base import UIBase  # dùng bản UIBase đã làm sạch
from client.config import ClientState  # giả định enum/str


class GUIInterface(UIBase):
    """Giao diện GUI cho game Fastest Finger First (Tkinter)."""

    POLL_INTERVAL_MS = 120  # chu kỳ refresh UI
    PROGRESS_INTERVAL_MS = 100  # chu kỳ tick progress

    def __init__(self, view_model):
        super().__init__(view_model)
        self.root: Optional[tk.Tk] = None

        # Widgets
        self.status_label: Optional[ttk.Label] = None
        self.connection_label: Optional[ttk.Label] = None
        self.question_label: Optional[ttk.Label] = None
        self.choice_vars: List[tk.StringVar] = []
        self.choice_buttons: List[ttk.Radiobutton] = []
        self.answer_var: tk.StringVar = tk.StringVar()
        self.submit_btn: Optional[ttk.Button] = None
        self.join_btn: Optional[ttk.Button] = None
        self.leave_btn: Optional[ttk.Button] = None
        self.connect_btn: Optional[ttk.Button] = None
        self.quit_btn: Optional[ttk.Button] = None
        self.progress: Optional[ttk.Progressbar] = None

        # Leaderboard
        self.lb_tree: Optional[ttk.Treeview] = None

        # State for progress/time-limit
        self._question_start_ts: Optional[float] = None
        self._question_time_limit: Optional[int] = None  # seconds

        # Debounce submit
        self._last_submit_ts: float = 0.0
        self._submit_cooldown_s: float = 0.35

    # ============ Lifecycle ============

    def start(self) -> None:
        """Khởi động GUI."""
        if self.root is not None:
            return

        self.root = tk.Tk()
        self.root.title("Fastest Finger First")
        self.root.geometry("780x520")
        self.root.minsize(720, 480)
        self.root.protocol("WM_DELETE_WINDOW", self.stop)

        self._setup_style()
        self._setup_gui()
        self.set_running(True)

        # tick vòng cập nhật
        self._schedule_poll()
        self._schedule_progress_tick()

        # focus phím tắt
        self.root.bind("<Return>", self._on_return_key)
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<Control-r>", lambda e: self._refresh_now())

        self.root.mainloop()

    def stop(self) -> None:
        """Dừng GUI và giải phóng tài nguyên."""
        self.set_running(False)
        if self.root is not None:
            try:
                self.root.quit()
            except Exception:
                pass

    # ============ Setup ============

    def _setup_style(self) -> None:
        style = ttk.Style()
        # Thử dùng theme có sẵn nếu khả dụng
        try:
            if "clam" in style.theme_names():
                style.theme_use("clam")
        except Exception:
            pass

        style.configure("Title.TLabel", font=("Segoe UI", 14, "bold"))
        style.configure("Status.TLabel", font=("Segoe UI", 10))
        style.configure("Question.TLabel", font=("Segoe UI", 12))
        style.configure("Header.TLabel", font=("Segoe UI", 11, "bold"))
        style.configure("Action.TButton", padding=6)
        style.configure("Danger.TButton", padding=6)
        style.map("Danger.TButton", foreground=[("active", "white")], background=[("active", "#c0392b")])

    def _setup_gui(self) -> None:
        assert self.root is not None
        root = self.root

        # Grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)  # body stretch

        # Header
        header = ttk.Frame(root, padding=(12, 8))
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Fastest Finger First", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")

        self.connection_label = ttk.Label(header, text="Chưa kết nối", style="Status.TLabel")
        self.connection_label.grid(row=0, column=1, sticky="e", padx=(10, 0))

        self.status_label = ttk.Label(header, text="Status: —", style="Status.TLabel")
        self.status_label.grid(row=1, column=0, sticky="w", pady=(6, 0))

        # Body (left: question & answer, right: leaderboard)
        body = ttk.Frame(root, padding=(12, 8))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3, uniform="body")
        body.columnconfigure(1, weight=2, uniform="body")
        body.rowconfigure(1, weight=1)

        # Question panel
        q_frame = ttk.LabelFrame(body, text="Câu hỏi", padding=12)
        q_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        q_frame.columnconfigure(0, weight=1)

        self.question_label = ttk.Label(q_frame, text="Đang chờ câu hỏi...", style="Question.TLabel", wraplength=680, justify="left")
        self.question_label.grid(row=0, column=0, sticky="w")

        # Progress (time limit)
        self.progress = ttk.Progressbar(q_frame, mode="determinate", maximum=100)
        self.progress.grid(row=1, column=0, sticky="ew", pady=(8, 0))

        # Answer panel (left column)
        a_frame = ttk.LabelFrame(body, text="Câu trả lời của bạn", padding=12)
        a_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        a_frame.columnconfigure(0, weight=1)

        # Radio buttons A-D (tạo trước 4 slot, sẽ gán text khi có câu hỏi)
        self.answer_var.set("")
        letters = ["A", "B", "C", "D"]
        for idx, letter in enumerate(letters):
            rb = ttk.Radiobutton(a_frame, text=f"{letter}. —", value=letter, variable=self.answer_var)
            rb.grid(row=idx, column=0, sticky="w", pady=2)
            self.choice_buttons.append(rb)

        # Submit
        btn_row = ttk.Frame(a_frame)
        btn_row.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        btn_row.columnconfigure(0, weight=1)

        self.submit_btn = ttk.Button(btn_row, text="Gửi đáp án (Enter)", style="Action.TButton", command=self.submit_answer)
        self.submit_btn.grid(row=0, column=0, sticky="ew")

        # Connection controls (right column)
        r_frame = ttk.LabelFrame(body, text="Phòng & Kết nối", padding=12)
        r_frame.grid(row=1, column=1, sticky="nsew")
        r_frame.columnconfigure(0, weight=1)

        self.connect_btn = ttk.Button(r_frame, text="Kết nối server", command=self.connect, style="Action.TButton")
        self.connect_btn.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.join_btn = ttk.Button(r_frame, text="Tham gia phòng", command=self.join_room, style="Action.TButton")
        self.join_btn.grid(row=1, column=0, sticky="ew", pady=(0, 6))

        self.leave_btn = ttk.Button(r_frame, text="Rời phòng", command=self.leave_room)
        self.leave_btn.grid(row=2, column=0, sticky="ew", pady=(0, 6))

        self.quit_btn = ttk.Button(r_frame, text="Thoát", command=self.stop, style="Danger.TButton")
        self.quit_btn.grid(row=3, column=0, sticky="ew", pady=(6, 0))

        # Leaderboard panel (full height under connection)
        lb_frame = ttk.LabelFrame(root, text="Bảng xếp hạng", padding=12)
        lb_frame.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 12))
        root.rowconfigure(2, weight=2)

        columns = ("rank", "player", "score")
        self.lb_tree = ttk.Treeview(lb_frame, columns=columns, show="headings", height=8)
        self.lb_tree.heading("rank", text="Hạng")
        self.lb_tree.heading("player", text="Người chơi")
        self.lb_tree.heading("score", text="Điểm")
        self.lb_tree.column("rank", width=60, anchor="center")
        self.lb_tree.column("player", width=220, anchor="w")
        self.lb_tree.column("score", width=100, anchor="e")
        self.lb_tree.grid(row=0, column=0, sticky="nsew")

        lb_scroll = ttk.Scrollbar(lb_frame, orient="vertical", command=self.lb_tree.yview)
        self.lb_tree.configure(yscrollcommand=lb_scroll.set)
        lb_scroll.grid(row=0, column=1, sticky="ns")

        lb_frame.columnconfigure(0, weight=1)
        lb_frame.rowconfigure(0, weight=1)

    # ============ Scheduling ============

    def _schedule_poll(self) -> None:
        if not self.running or self.root is None:
            return
        self._safe_update_gui()
        self.root.after(self.POLL_INTERVAL_MS, self._schedule_poll)

    def _schedule_progress_tick(self) -> None:
        if not self.running or self.root is None:
            return
        self._tick_progress()
        self.root.after(self.PROGRESS_INTERVAL_MS, self._schedule_progress_tick)

    def _refresh_now(self) -> None:
        self._safe_update_gui()

    # ============ Update & Rendering ============

    def _safe_update_gui(self) -> None:
        try:
            self.update_gui()
        except Exception as e:
            # Không để crash UI vì lỗi view_model
            self.on_error_occurred(f"Lỗi cập nhật giao diện: {e}")

    def update_gui(self) -> None:
        if not self.root:
            return

        # 1) Cập nhật trạng thái kết nối & state
        try:
            state = self.view_model.get_state()  # str hoặc enum
        except Exception:
            state = "unknown"

        if self.status_label:
            self.status_label.config(text=f"Status: {state}")

        if self.connection_label:
            try:
                connected = bool(getattr(self.view_model, "is_connected", lambda: False)())
            except Exception:
                # fallback: suy đoán từ state
                connected = state not in ("disconnected", "unknown", "idle")
            self.connection_label.config(text="Đã kết nối" if connected else "Chưa kết nối")

        # 2) Cập nhật câu hỏi & lựa chọn
        try:
            question = self.view_model.get_current_question() or {}
        except Exception:
            question = {}

        q_number = question.get("question_number", "?")
        q_text = question.get("question_text", "")
        options: List[str] = question.get("options", []) or []

        # time limit (nếu VM có)
        time_limit = question.get("time_limit")
        if isinstance(time_limit, int) and time_limit > 0:
            # đặt khi câu hỏi mới (dựa vào id/number)
            if self._is_new_question(question):
                self._question_time_limit = time_limit
                self._question_start_ts = time.time()

        # render câu hỏi
        if self.question_label:
            display = f"Câu hỏi {q_number}: {q_text}" if q_text else "Đang chờ câu hỏi..."
            self.question_label.config(text=display)

        # render lựa chọn (A-D)
        letters = ["A", "B", "C", "D"]
        for i, rb in enumerate(self.choice_buttons):
            if i < len(options):
                rb.config(text=f"{letters[i]}. {options[i]}")
                rb.state(["!disabled"])
            else:
                rb.config(text=f"{letters[i]}. —")
                rb.state(["disabled"])

        # 3) Khóa/mở submit theo state
        can_answer = self._can_answer_in_state(state) and bool(q_text)
        if self.submit_btn:
            if can_answer:
                self.submit_btn.state(["!disabled"])
            else:
                self.submit_btn.state(["disabled"])

        for rb in self.choice_buttons:
            if can_answer:
                rb.state(["!disabled"])
            else:
                rb.state(["disabled"])

        # 4) Cập nhật leaderboard
        try:
            leaderboard = self.view_model.get_leaderboard() or []
        except Exception:
            leaderboard = []

        if self.lb_tree is not None:
            # clear & fill
            for iid in self.lb_tree.get_children():
                self.lb_tree.delete(iid)

            for idx, player in enumerate(leaderboard[:50], 1):
                uname = str(player.get("username", "—"))
                score = int(player.get("score", 0))
                self.lb_tree.insert("", "end", values=(idx, uname, score))

    def _is_new_question(self, question: Dict[str, Any]) -> bool:
        """
        Xác định xem đây có phải câu hỏi mới (để reset progress) bằng cách so sánh id/number với state hiện tại.
        """
        # Kỹ thuật đơn giản: lưu number hiện tại vào root widget (không lan ra ngoài)
        if self.root is None:
            return False
        key = "_last_q_number"
        last = getattr(self.root, key, None)
        current = question.get("question_number")
        if current and current != last:
            setattr(self.root, key, current)
            return True
        return False

    def _can_answer_in_state(self, state: str) -> bool:
        """
        Quy ước: có thể trả lời khi game đang "in_progress" hoặc "question_open".
        Tùy bạn map với ClientState thực tế.
        """
        normalized = str(state).lower()
        return any(s in normalized for s in ("in_progress", "question_open", "playing"))

    def _tick_progress(self) -> None:
        """Cập nhật progressbar dựa trên time limit (nếu có)."""
        if not self.progress:
            return
        if not self._question_start_ts or not self._question_time_limit:
            self.progress["value"] = 0
            return

        elapsed = time.time() - self._question_start_ts
        total = max(1, self._question_time_limit)
        pct = max(0, min(100, int((elapsed / total) * 100)))
        # đảo chiều (còn lại)
        remaining_pct = max(0, 100 - pct)
        self.progress["value"] = remaining_pct

    # ============ Actions ============

    def _on_return_key(self, event=None):
        self.submit_answer()

    def submit_answer(self, event=None):
        """Gửi đáp án từ radio selection."""
        now = time.time()
        if now - self._last_submit_ts < self._submit_cooldown_s:
            return
        self._last_submit_ts = now

        final_answer = self.answer_var.get().strip().upper()
        if final_answer not in {"A", "B", "C", "D"}:
            messagebox.showwarning("Chưa chọn đáp án", "Vui lòng chọn A, B, C hoặc D.")
            return
        try:
            ok = self.view_model.submit_answer(final_answer)
        except Exception as e:
            self.on_error_occurred(f"Gửi đáp án thất bại: {e}")
            return

        if ok:
            messagebox.showinfo("Đã gửi", f"Đáp án của bạn: {final_answer}")
            # không tự clear radio để người chơi thấy mình đã chọn gì
        else:
            messagebox.showerror("Lỗi", "Không thể gửi đáp án. Vui lòng thử lại.")

    def connect(self):
        """Kết nối server."""
        try:
            ok = self.view_model.connect_to_server()
        except Exception as e:
            self.on_error_occurred(f"Kết nối thất bại: {e}")
            return

        if ok:
            messagebox.showinfo("Thành công", "Đã kết nối server.")
            self._refresh_now()
        else:
            messagebox.showerror("Lỗi", "Không thể kết nối.")

    def join_room(self):
        """Tham gia phòng (hỏi room_id nếu cần)."""
        room_id = None
        if hasattr(self.view_model, "get_room_id_required") and self.view_model.get_room_id_required():
            room_id = simpledialog.askstring("Join Room", "Nhập Room ID:", parent=self.root)

        try:
            ok = self.view_model.join_room(room_id) if room_id is not None else self.view_model.join_room()
        except Exception as e:
            self.on_error_occurred(f"Vào phòng thất bại: {e}")
            return

        if ok:
            messagebox.showinfo("Thành công", "Đã tham gia phòng.")
            self._refresh_now()
        else:
            messagebox.showerror("Lỗi", "Không thể tham gia phòng.")

    def leave_room(self):
        """Rời phòng."""
        try:
            ok = self.view_model.leave_room()
        except Exception as e:
            self.on_error_occurred(f"Rời phòng thất bại: {e}")
            return

        if ok:
            messagebox.showinfo("Thành công", "Đã rời phòng.")
            self._refresh_now()
        else:
            messagebox.showerror("Lỗi", "Không thể rời phòng.")

    # ============ UIBase Event Handlers ============

    def on_state_changed(self, new_state: str) -> None:
        # Cập nhật giao diện nhanh khi có sự kiện
        self._refresh_now()

    def on_question_received(self, question_data: dict) -> None:
        # Reset progress về câu hỏi mới
        self._question_start_ts = time.time()
        self._question_time_limit = question_data.get("time_limit")
        self.answer_var.set("")
        self._refresh_now()

    def on_score_updated(self, results: dict) -> None:
        self._refresh_now()

    def on_leaderboard_updated(self, leaderboard: list) -> None:
        self._refresh_now()

    def on_game_started(self, data: dict) -> None:
        messagebox.showinfo("Game Started", "Trò chơi bắt đầu!")
        self._refresh_now()

    def on_game_ended(self, final_results: dict) -> None:
        winner = final_results.get("winner") or final_results.get("winner_user_id") or "Không rõ"
        messagebox.showinfo("Game Ended", f"Trò chơi kết thúc!\nNgười thắng: {winner}")
        self._refresh_now()

    def on_error_occurred(self, error_message: str, *, code: Optional[str] = None) -> None:
        suffix = f"\n(Mã: {code})" if code else ""
        messagebox.showerror("Lỗi", f"{error_message}{suffix}")

    def on_info_received(self, info_message: str) -> None:
        messagebox.showinfo("Thông báo", info_message)

    # Giữ API UIBase
    def display_question(self, question_data: dict) -> None:
        self.on_question_received(question_data)

    def display_leaderboard(self, leaderboard: list) -> None:
        self.on_leaderboard_updated(leaderboard)

    def display_game_status(self, status: dict) -> None:
        self.on_state_changed(str(status.get("state", "")))

    def display_final_results(self, results: dict) -> None:
        self.on_game_ended(results)
