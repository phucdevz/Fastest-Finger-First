# Câu hỏi đã nhận, lưu đáp án local
# Phụ trách: Nguyễn Đức Lượng

class Question:
    def __init__(self, qid, question, options, time_limit, number, total):
        self.id = qid
        self.question = question
        self.options = options
        self.time_limit = time_limit
        self.number = number
        self.total = total

    @classmethod
    def from_message(cls, msg: dict):
        return cls(
            qid=msg.get("question_id"),
            question=msg.get("question"),
            options=msg.get("options"),
            time_limit=msg.get("time_limit"),
            number=msg.get("question_number"),
            total=msg.get("total_questions")
        )
