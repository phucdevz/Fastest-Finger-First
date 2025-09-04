"""
UI base class cho trò chơi/ứng dụng hỏi-đáp.
- Chuẩn hóa kiểu dữ liệu bằng TypedDict
- Rõ ràng vòng đời start/stop
- Sẵn hook xử lý sự kiện/trạng thái, thông báo
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict


# ==== Kiểu dữ liệu có cấu trúc ====

class QuestionChoice(TypedDict, total=False):
    id: str
    text: str
    is_correct: bool  # chỉ dùng nội bộ (nếu có)

class QuestionData(TypedDict, total=False):
    id: str
    text: str
    choices: List[QuestionChoice]
    time_limit: Optional[int]  # giây
    metadata: Dict[str, Any]

class ScoreEntry(TypedDict, total=False):
    user_id: str
    user_name: str
    score_delta: int
    total_score: int

class ScoreResults(TypedDict, total=False):
    question_id: Optional[str]
    entries: List[ScoreEntry]
    metadata: Dict[str, Any]

class LeaderboardEntry(TypedDict, total=False):
    rank: int
    user_id: str
    user_name: str
    total_score: int

class GameLeaderboard(TypedDict, total=False):
    entries: List[LeaderboardEntry]
    updated_at: Optional[str]  # ISO datetime
    metadata: Dict[str, Any]

class GameStatus(TypedDict, total=False):
    state: str  # ví dụ: "idle" | "waiting" | "in_progress" | "paused" | "ended"
    round: Optional[int]
    total_rounds: Optional[int]
    remaining_time: Optional[int]
    metadata: Dict[str, Any]

class GameStartData(TypedDict, total=False):
    total_rounds: Optional[int]
    rules: Optional[str]
    metadata: Dict[str, Any]

class FinalResults(TypedDict, total=False):
    winner_user_id: Optional[str]
    leaderboard: GameLeaderboard
    metadata: Dict[str, Any]


# ==== Lớp nền tảng UI ====

class UIBase(ABC):
    """
    Lớp nền tảng cho tất cả UI interface.
    Các lớp kế thừa cần hiện thực các phương thức abstract bên dưới.
    """

    def __init__(self, view_model: Any) -> None:
        """
        Args:
            view_model: nguồn dữ liệu/logic hiển thị (MVVM hoặc Presenter)
        """
        self.view_model = view_model
        self.running: bool = False

    # --- Vòng đời UI ---

    @abstractmethod
    def start(self) -> None:
        """Khởi động UI (kết nối tín hiệu, render lần đầu, v.v.)."""
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        """Dừng UI (giải phóng tài nguyên, hủy timer, v.v.)."""
        raise NotImplementedError

    @abstractmethod
    def update(self, *, force: bool = False) -> None:
        """Cập nhật UI theo trạng thái hiện tại của view_model."""
        raise NotImplementedError

    # --- Sự kiện trạng thái hệ thống/trò chơi ---

    @abstractmethod
    def on_state_changed(self, new_state: str) -> None:
        """Xử lý khi trạng thái hệ thống/trò chơi thay đổi."""
        raise NotImplementedError

    @abstractmethod
    def on_question_received(self, question_data: QuestionData) -> None:
        """Xử lý khi nhận câu hỏi mới."""
        raise NotImplementedError

    @abstractmethod
    def on_score_updated(self, results: ScoreResults) -> None:
        """Xử lý khi điểm số được cập nhật."""
        raise NotImplementedError

    @abstractmethod
    def on_leaderboard_updated(self, leaderboard: GameLeaderboard) -> None:
        """Xử lý khi bảng xếp hạng được cập nhật."""
        raise NotImplementedError

    @abstractmethod
    def on_game_started(self, data: GameStartData) -> None:
        """Xử lý khi game bắt đầu."""
        raise NotImplementedError

    @abstractmethod
    def on_game_ended(self, final_results: FinalResults) -> None:
        """Xử lý khi game kết thúc."""
        raise NotImplementedError

    @abstractmethod
    def on_error_occurred(self, error_message: str, *, code: Optional[str] = None) -> None:
        """Xử lý lỗi hiển thị cho người dùng."""
        raise NotImplementedError

    @abstractmethod
    def on_info_received(self, info_message: str) -> None:
        """Xử lý thông tin (toast, snackbar, banner...)."""
        raise NotImplementedError

    # --- Hàm tiện ích hiển thị (không bắt buộc override) ---

    def display_question(self, question_data: QuestionData) -> None:
        """Hiển thị câu hỏi (mặc định: no-op)."""
        # Lớp con có thể override để render cụ thể
        return None

    def display_leaderboard(self, leaderboard: GameLeaderboard) -> None:
        """Hiển thị bảng xếp hạng (mặc định: no-op)."""
        return None

    def display_game_status(self, status: GameStatus) -> None:
        """Hiển thị trạng thái game (mặc định: no-op)."""
        return None

    def display_final_results(self, results: FinalResults) -> None:
        """Hiển thị kết quả cuối cùng (mặc định: no-op)."""
        return None

    # --- Nhập liệu & thông báo ---

    def get_user_input(self, prompt: str = "") -> str:
        """
        Lấy input từ người dùng.
        Lớp con có thể override (CLI/GUI/Web). Mặc định: trả về chuỗi rỗng.
        """
        return ""

    def show_message(self, message: str, *, message_type: str = "info") -> None:
        """
        Hiển thị thông báo cho người dùng.
        message_type: "info" | "success" | "warning" | "error"
        """
        return None

    # --- Tiện ích phụ trợ ---

    def set_running(self, value: bool) -> None:
        """Cập nhật cờ chạy; dùng khi start/stop để đồng bộ trạng thái."""
        self.running = value

    def handle_event(self, event: str, payload: Dict[str, Any] | None = None) -> None:
        """
        Router sự kiện đơn giản (tuỳ chọn dùng).
        Ví dụ: event="question_received", payload=QuestionData
        """
        if event == "state_changed" and payload and "state" in payload:
            self.on_state_changed(str(payload["state"]))
        elif event == "question_received" and payload:
            self.on_question_received(payload)  # type: ignore[arg-type]
        elif event == "score_updated" and payload:
            self.on_score_updated(payload)  # type: ignore[arg-type]
        elif event == "leaderboard_updated" and payload:
            self.on_leaderboard_updated(payload)  # type: ignore[arg-type]
        elif event == "game_started" and payload:
            self.on_game_started(payload)  # type: ignore[arg-type]
        elif event == "game_ended" and payload:
            self.on_game_ended(payload)  # type: ignore[arg-type]
        elif event == "error" and payload:
            self.on_error_occurred(str(payload.get("message", "")), code=payload.get("code"))  # type: ignore[arg-type]
        elif event == "info" and payload:
            self.on_info_received(str(payload.get("message", "")))

    # --- Context manager cho vòng đời ---

    def __enter__(self) -> "UIBase":
        self.start()
        self.set_running(True)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.set_running(False)
        self.stop()
