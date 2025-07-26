# Giao diện (console), nhập tên, trả lời, hiển thị điểm, xếp hạng
# Phụ trách: Lê Đức Anh

class ClientUI:
    def get_user_command(self):
        return input("Lệnh [join/ready/answer/status]: ").strip()

    def get_answer_input(self, options):
        print("Nhập đáp án của bạn:")
        for idx, opt in enumerate(options):
            print(f"{idx + 1}. {opt}")
        choice = input("Chọn (1-4): ")
        try:
            return options[int(choice) - 1]
        except:
            print("⚠️ Lựa chọn không hợp lệ.")
            return ""

    def display_question(self, question):
        print("\n📢 Câu hỏi:")
        print(f"({question.number}/{question.total}) {question.question}")
        for idx, opt in enumerate(question.options):
            print(f"{idx + 1}. {opt}")
        print(f"(⏱️ {question.time_limit}s)\n")

    def display_answer_review(self, msg):
        print("\n📊 Đáp án:")
        print(f"✅ Đáp án đúng: {msg['correct_answer']}")
        print(f"📖 Giải thích: {msg.get('explanation', 'Không có')}")
        print("\n🏆 Xếp hạng hiện tại:")
        for rank in msg.get("current_rankings", []):
            print(f"  - {rank['rank']}. {rank['player_name']} ({rank['score']} điểm)")

    def display_game_end(self, msg):
        print("\n🏁 Trò chơi kết thúc!")
        winner = msg.get("winner", {})
        print(f"🎉 Người thắng: {winner.get('name')} ({winner.get('score')} điểm)")
        print("\n📋 Bảng xếp hạng cuối cùng:")
        for rank in msg.get("final_rankings", []):
            print(f"  - {rank['rank']}. {rank['player_name']} ({rank['score']} điểm)")

    def display_status(self, status):
        print("\nℹ️ Trạng thái hiện tại:")
        for k, v in status.items():
            print(f"{k}: {v}")
