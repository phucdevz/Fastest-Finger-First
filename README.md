# Vua Tốc Độ - Fastest Finger First

Một mini game đa người chơi sử dụng mô hình MVVM và Socket Multi Client-Server.

## 🎮 Tính năng

- **Đa người chơi**: Hỗ trợ tối đa 4 người chơi cùng lúc
- **Giao diện đẹp**: UI hiện đại với theme tối
- **Real-time**: Cập nhật điểm số và bảng xếp hạng theo thời gian thực
- **Hệ thống điểm**: Tính điểm dựa trên độ chính xác và tốc độ trả lời
- **Phòng chờ**: Hệ thống phòng chờ với tín hiệu sẵn sàng

## 🏗️ Kiến trúc

### Mô hình MVVM
- **Model**: Quản lý dữ liệu game (Player, GameRoom, Question)
- **View**: Giao diện người dùng (GUI với Tkinter)
- **ViewModel**: Xử lý logic và giao tiếp giữa Model và View

### Socket Multi Client-Server
- **Server**: Xử lý đa luồng, quản lý phòng, tính điểm
- **Client**: Kết nối qua socket, giao diện người dùng
- **Giao thức**: JSON message qua TCP socket

## 📁 Cấu trúc Project

```
Fastest-Finger-First/
├── config.json              # Cấu hình chính
├── data/
│   ├── player_stats.json    # Thống kê người chơi
│   └── questions.json       # Bộ câu hỏi
├── server/
│   ├── main.py             # Server chính
│   ├── model/
│   │   ├── player.py       # Model Player
│   │   └── game_room.py    # Model GameRoom
│   └── utils/
│       ├── config_loader.py # Load cấu hình
│       ├── question_manager.py # Quản lý câu hỏi
│       └── logger.py       # Ghi log
├── client/
│   ├── main.py             # Client chính
│   ├── viewmodel/
│   │   └── game_viewmodel.py # ViewModel
│   ├── view/
│   │   └── main_window.py  # Giao diện chính
│   └── utils/
│       └── config_loader.py # Load cấu hình
├── requirements.txt         # Dependencies
└── README.md              # Hướng dẫn
```

## 🚀 Cài đặt và Chạy

### 1. Cài đặt dependencies
```bash
# Python 3.7+ required
python --version

# Install dependencies (optional - most are built-in)
pip install -r requirements.txt
```

### 2. Chạy Server
```bash
cd server
python main.py
```

### 3. Chạy Client
```bash
cd client
python main.py
```

### 4. Chạy nhiều Client
Mở nhiều terminal và chạy client để test đa người chơi.

## 🎯 Cách chơi

1. **Kết nối**: Nhập tên và mã phòng
2. **Phòng chờ**: Chờ người chơi khác và bấm "SẴN SÀNG"
3. **Chơi game**: Trả lời câu hỏi nhanh nhất có thể
4. **Tính điểm**: 
   - Đáp án đúng: +10 điểm
   - Trả lời nhanh (<5s): +5 điểm bonus
   - Trả lời nhanh (<10s): +2 điểm bonus

## ⚙️ Cấu hình

Chỉnh sửa `config.json` để thay đổi:

```json
{
  "server": {
    "host": "localhost",
    "port": 5000,
    "max_players": 4,
    "question_time": 30,
    "wait_time": 10
  },
  "game": {
    "questions_per_round": 10,
    "points_per_correct": 10,
    "bonus_points_fast": 5
  }
}
```

## 🧪 Testing

### Test đơn giản
1. Chạy server
2. Chạy 2-3 client
3. Tham gia cùng phòng
4. Bấm sẵn sàng và chơi

### Test kết nối
```bash
# Test server
telnet localhost 5000

# Test client
python client/main.py
```

## 📊 Tính năng nâng cao

### Thêm câu hỏi
Chỉnh sửa `data/questions.json`:

```json
{
  "id": 11,
  "question": "Câu hỏi mới?",
  "options": ["A", "B", "C", "D"],
  "correct_answer": 0,
  "category": "Toán học",
  "difficulty": "easy"
}
```

### Thay đổi theme
Trong `config.json`:
```json
{
  "ui": {
    "theme": "light",
    "window_width": 1200,
    "window_height": 800
  }
}
```

## 🐛 Troubleshooting

### Lỗi kết nối
- Kiểm tra server đã chạy chưa
- Kiểm tra port 5000 có bị block không
- Kiểm tra firewall

### Lỗi giao diện
- Kiểm tra Python version (3.7+)
- Kiểm tra tkinter đã cài chưa

### Lỗi câu hỏi
- Kiểm tra file `data/questions.json`
- Kiểm tra format JSON

## 📝 Logs

Logs được lưu trong thư mục `logs/`:
- `server_YYYYMMDD.log`: Log server
- Console output: Log real-time

## 🤝 Đóng góp

1. Fork project
2. Tạo feature branch
3. Commit changes
4. Push to branch
5. Tạo Pull Request

## 📄 License

MIT License - xem file LICENSE để biết thêm chi tiết.

## 👥 Team

- **Backend/Server**: Quản lý server, socket, game logic
- **Client Logic**: ViewModel, xử lý client logic
- **UI/UX**: Giao diện người dùng, animations
- **Testing**: Unit tests, integration tests

---

**Vua Tốc Độ** - Fastest Finger First Game 🏆 