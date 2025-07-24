# Fastest Finger First - Vua Tốc Độ

Hướng dẫn setup, chạy, mô tả dự án

Phụ trách: Nguyễn Phạm Thiên Phước
Vai trò: Testing & Documentation Lead

## 📋 Tổng quan dự án

**Fastest Finger First** là một game trả lời câu hỏi trực tuyến theo thời gian thực, sử dụng kiến trúc Client-Server với giao thức Socket. Người chơi sẽ thi đấu để trả lời câu hỏi nhanh nhất và chính xác nhất.

### 🎯 Tính năng chính

- **Multiplayer Real-time**: Hỗ trợ nhiều người chơi cùng lúc
- **Câu hỏi đa dạng**: Hỗ trợ nhiều loại câu hỏi và chủ đề
- **Hệ thống điểm**: Tính điểm dựa trên tốc độ và độ chính xác
- **Bảng xếp hạng**: Theo dõi và hiển thị xếp hạng real-time
- **Lưu trữ dữ liệu**: Lưu lịch sử trận đấu và thống kê người chơi
- **Giao diện admin**: Quản lý server và theo dõi trận đấu

### 🏗️ Kiến trúc hệ thống

- **Server**: Python Socket Server với kiến trúc MVVM
- **Client**: Python Client với giao diện console/GUI
- **Database**: JSON file cho câu hỏi và lịch sử
- **Communication**: Socket TCP/IP
- **Architecture**: MVVM Pattern

---

## 🚀 Cài đặt và Chạy

### Yêu cầu hệ thống

- Python 3.7 hoặc cao hơn
- Hệ điều hành: Windows, macOS, Linux
- RAM: Tối thiểu 512MB
- Ổ cứng: 100MB trống

### Cài đặt

1. **Clone repository**
   ```bash
   git clone https://github.com/your-username/Fastest-Finger-First.git
   cd Fastest-Finger-First
   ```

2. **Cài đặt dependencies (tùy chọn)**
   ```bash
   pip install -r requirements.txt
   ```

3. **Chạy server**
   ```bash
   # Chạy với cấu hình mặc định
   python server/main.py
   
   # Chạy với cấu hình tùy chỉnh
   python server/main.py --host 0.0.0.0 --port 5000 --log-level INFO
   ```

### Cấu hình

Server sẽ tự động tạo file `config.json` với cấu hình mặc định:

```json
{
  "server": {
    "host": "localhost",
    "port": 5000,
    "max_connections": 50,
    "timeout": 60
  },
  "game": {
    "min_players": 2,
    "max_players": 10,
    "questions_per_game": 10,
    "question_time_limit": 30,
    "countdown_duration": 5,
    "answer_review_duration": 3
  },
  "logging": {
    "level": "INFO",
    "file": "server.log",
    "max_size": 10485760,
    "backup_count": 5
  },
  "data": {
    "questions_file": "data/questions.json",
    "player_stats_file": "data/player_stats.json",
    "game_history_file": "data/game_history.json"
  }
}
```

---

## 📁 Cấu trúc dự án

```
fastest-finger-first/
│
├── server/                    # Backend Server
│   ├── main.py               # Entry point khởi động server
│   ├── model/
│   │   ├── question.py       # Quản lý câu hỏi và bộ đề
│   │   ├── player.py         # Thông tin người chơi
│   │   └── scoreboard.py     # Bảng điểm và lịch sử
│   ├── viewmodel/
│   │   ├── game_manager.py   # Điều phối game flow
│   │   └── network_manager.py# Quản lý socket và kết nối
│   ├── view/
│   │   └── server_ui.py      # Giao diện admin (tùy chọn)
│   └── utils/
│       └── helpers.py        # Hàm tiện ích
│
├── client/                    # Frontend Client
│   ├── main.py               # Entry point client
│   ├── model/
│   │   ├── player.py         # Thông tin user local
│   │   └── question.py       # Câu hỏi nhận được
│   ├── viewmodel/
│   │   └── game_viewmodel.py # Logic xử lý client
│   ├── view/
│   │   └── client_ui.py      # Giao diện người chơi
│   └── utils/
│       └── helpers.py        # Hàm tiện ích client
│
├── data/                      # Dữ liệu
│   ├── questions.json        # Bộ câu hỏi
│   ├── player_stats.json     # Thống kê người chơi
│   └── game_history.json     # Lịch sử trận đấu
│
├── docs/                      # Tài liệu
│   ├── project_review.md     # Phân công dự án
│   ├── report.md             # Báo cáo dự án
│   └── presentation.pptx     # Slide thuyết trình
│
├── requirements.txt           # Dependencies
├── README.md                 # Hướng dẫn này
└── config.json               # Cấu hình server
```

---

## 👥 Phân công thành viên

### 🎯 **Nguyễn Trường Phục** - Backend/Server & Database
- `server/main.py` - Entry point server
- `server/model/question.py` - Quản lý câu hỏi
- `server/model/player.py` - Thông tin người chơi
- `server/model/scoreboard.py` - Bảng điểm
- `server/utils/helpers.py` - Hàm tiện ích

### 🎯 **Nguyễn Đức Lượng** - Client Logic & ViewModel
- `client/main.py` - Entry point client
- `client/viewmodel/game_viewmodel.py` - Logic client
- `client/model/player.py` - Thông tin user
- `client/model/question.py` - Câu hỏi local
- `client/utils/helpers.py` - Hàm tiện ích client

### 🎯 **Lê Đức Anh** - UI/View Developer
- `client/view/client_ui.py` - Giao diện người chơi
- `server/view/server_ui.py` - Giao diện admin
- `data/questions.json` - Bộ câu hỏi test

### 🎯 **Nguyễn Phạm Thiên Phước** - Testing & Documentation
- `data/questions.json` - Bộ câu hỏi hoàn chỉnh
- `docs/report.md` - Báo cáo dự án
- `docs/presentation.pptx` - Slide thuyết trình
- `README.md` - Hướng dẫn dự án

---

## 🎮 Cách chơi

### Kết nối
1. Chạy server: `python server/main.py`
2. Chạy client: `python client/main.py`
3. Nhập tên người chơi và kết nối

### Luật chơi
1. **Chờ phòng**: Đợi đủ số người chơi tối thiểu
2. **Đếm ngược**: 5 giây chuẩn bị
3. **Trả lời câu hỏi**: 
   - Mỗi câu hỏi có thời gian giới hạn
   - Trả lời nhanh nhất và đúng được nhiều điểm
   - Điểm = (Thời gian còn lại / Tổng thời gian) × Điểm câu hỏi
4. **Xem kết quả**: Hiển thị đáp án và xếp hạng
5. **Kết thúc**: Hiển thị người thắng cuộc

### Điểm số
- **Đúng**: Điểm dựa trên tốc độ trả lời
- **Sai**: 0 điểm
- **Không trả lời**: 0 điểm

---

## 🔧 API Reference

### Server Messages

#### Connection
```json
{
  "type": "connect",
  "data": {
    "player_name": "PlayerName"
  }
}
```

#### Join Game
```json
{
  "type": "join_game",
  "data": {}
}
```

#### Answer Question
```json
{
  "type": "answer",
  "data": {
    "answer": "A",
    "answer_time": 5.2
  }
}
```

### Client Messages

#### Question
```json
{
  "type": "question",
  "question_id": "1",
  "question": "What is the capital of Vietnam?",
  "options": ["Hanoi", "HCMC", "Da Nang", "Hue"],
  "time_limit": 30,
  "question_number": 1,
  "total_questions": 10
}
```

#### Answer Review
```json
{
  "type": "answer_review",
  "correct_answer": "Hanoi",
  "explanation": "Hanoi is the capital of Vietnam",
  "correct_answers": [
    {
      "player_id": "1",
      "player_name": "Player1",
      "answer_time": 2.5
    }
  ],
  "current_rankings": [...]
}
```

---

## 🛠️ Development

### Chạy tests
```bash
# Cài đặt pytest
pip install pytest

# Chạy tests
pytest tests/
```

### Code formatting
```bash
# Cài đặt black
pip install black

# Format code
black server/ client/
```

### Type checking
```bash
# Cài đặt mypy
pip install mypy

# Check types
mypy server/ client/
```

---

## 📊 Monitoring

### Logs
- Server logs: `server.log`
- Log level: DEBUG, INFO, WARNING, ERROR
- Log rotation: 10MB per file, 5 backup files

### Metrics
- Active connections
- Games played
- Questions answered
- Player statistics

### Health check
```bash
# Kiểm tra trạng thái server
curl http://localhost:5000/health
```

---

## 🔒 Security

### Input Validation
- Sanitize player names
- Validate answer options
- Prevent path traversal

### Rate Limiting
- Connection limits
- Message frequency limits
- Timeout handling

### Data Protection
- Secure file operations
- Backup creation
- Error handling

---

## 🚀 Deployment

### Production Setup
1. **Environment**
   ```bash
   export PYTHONPATH=/path/to/Fastest-Finger-First
   export LOG_LEVEL=INFO
   ```

2. **Service (systemd)**
   ```ini
   [Unit]
   Description=Fastest Finger First Server
   After=network.target
   
   [Service]
   Type=simple
   User=gameuser
   WorkingDirectory=/path/to/Fastest-Finger-First
   ExecStart=/usr/bin/python3 server/main.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

3. **Firewall**
   ```bash
   # Allow game port
   sudo ufw allow 5000
   ```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "server/main.py"]
```

---

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use**
   ```bash
   # Change port
   python server/main.py --port 5001
   ```

2. **Permission denied**
   ```bash
   # Check file permissions
   chmod +x server/main.py
   ```

3. **Import errors**
   ```bash
   # Set PYTHONPATH
   export PYTHONPATH=/path/to/project
   ```

### Debug Mode
```bash
# Enable debug logging
python server/main.py --log-level DEBUG
```

---

## 📈 Roadmap

### Version 1.0 (Current)
- ✅ Basic multiplayer functionality
- ✅ Question management
- ✅ Score tracking
- ✅ Real-time communication

### Version 1.1 (Planned)
- 🔄 Web interface
- 🔄 Database integration
- 🔄 Authentication system
- 🔄 Tournament mode

### Version 2.0 (Future)
- 📋 Mobile app
- 📋 Voice chat
- 📋 AI opponents
- 📋 Global leaderboards

---

## 📞 Support

### Team Contact
- **Nguyễn Trường Phục**: Backend development
- **Nguyễn Đức Lượng**: Client development  
- **Lê Đức Anh**: UI/UX design
- **Nguyễn Phạm Thiên Phước**: Testing & Documentation

### Issues
- GitHub Issues: [Create Issue](https://github.com/phucdevz/Fastest-Finger-First/issues)
- Email: agencyluuvong@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Ngày tạo: 20/07/2025*  s
*Phiên bản: 1.0*  
*Nhóm phát triển: Zero Latency Team* 