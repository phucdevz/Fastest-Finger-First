# Lưu thông tin user, trạng thái cá nhân
# Phụ trách: Nguyễn Đức Lượng

class Player:
    def __init__(self, name: str):
        self.name = name
        self.id = None
        self.status = "connected"
        self.score = 0

    def reset(self):
        self.score = 0
        self.status = "ready"
