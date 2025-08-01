# 🚀 Quick Start - Vua Tốc Độ

## ⚡ Chạy nhanh

### Cách 1: Demo GUI (Khuyến nghị)
```bash
python demo.py
```

### Cách 2: Chạy thủ công
```bash
# Terminal 1 - Chạy Server
python run_server.py

# Terminal 2 - Chạy Client
python run_client.py

# Terminal 3 - Chạy thêm Client (để test đa người chơi)
python run_client.py
```

### Cách 3: Test kết nối
```bash
python test_client.py
```

## 🎮 Cách chơi

1. **Kết nối**: Nhập tên và mã phòng (mặc định: "default")
2. **Phòng chờ**: Chờ người chơi khác và bấm "SẴN SÀNG"
3. **Chơi game**: Trả lời câu hỏi nhanh nhất có thể
4. **Tính điểm**: 
   - Đáp án đúng: +10 điểm
   - Trả lời nhanh (<5s): +5 điểm bonus
   - Trả lời nhanh (<10s): +2 điểm bonus

## 📁 Cấu trúc file

```
Fastest-Finger-First/
├── demo.py              # 🎯 Chạy demo GUI
├── run_server.py        # 🚀 Chạy server
├── run_client.py        # 🎮 Chạy client
├── test_client.py       # 🧪 Test kết nối
├── config.json          # ⚙️ Cấu hình
├── data/
│   ├── questions.json   # ❓ Bộ câu hỏi
│   └── player_stats.json # 📊 Thống kê
├── server/              # 🔧 Backend
├── client/              # 🖥️ Frontend
└── README.md           # 📖 Hướng dẫn chi tiết
```

## ⚙️ Cấu hình

Chỉnh sửa `config.json`:

```json
{
  "server": {
    "host": "localhost",
    "port": 5000,
    "max_players": 4,
    "question_time": 30
  },
  "game": {
    "questions_per_round": 10,
    "points_per_correct": 10
  }
}
```

## 🐛 Troubleshooting

### Lỗi kết nối
- Kiểm tra server đã chạy chưa
- Kiểm tra port 5000 có bị block không

### Lỗi giao diện
- Kiểm tra Python 3.7+
- Kiểm tra tkinter đã cài chưa

### Lỗi import
- Chạy từ thư mục gốc của project
- Kiểm tra cấu trúc thư mục

## 🎯 Test đa người chơi

1. Chạy `python demo.py`
2. Bấm "Chạy Cả Hai"
3. Mở thêm terminal và chạy `python run_client.py`
4. Tham gia cùng phòng và chơi!

## 📞 Hỗ trợ

- Xem `README.md` để biết thêm chi tiết
- Kiểm tra logs trong thư mục `logs/`
- Chạy `python test_client.py` để debug kết nối

---

**Vua Tốc Độ** - Fastest Finger First Game 🏆 