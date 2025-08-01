# Fastest Finger First - Game Trả Lời Câu Hỏi Nhanh

## Tổng quan
Fastest Finger First là một game trả lời câu hỏi nhanh với kiến trúc Client-Server, sử dụng TCP socket để giao tiếp realtime giữa nhiều người chơi.

## Kiến trúc hệ thống
- **Server**: Quản lý phòng chờ, gửi câu hỏi, nhận đáp án, tính điểm, cập nhật bảng xếp hạng
- **Client**: Người chơi tham gia trả lời câu hỏi, xem điểm số và bảng xếp hạng realtime
- **Giao tiếp**: TCP socket, server đa luồng

## Cấu trúc thư mục
```
Fastest-Finger-First/
├── server/                 # Backend/Server & Database
│   ├── server.py          # Server chính
│   ├── game_manager.py    # Quản lý game logic
│   ├── database.py        # Cơ sở dữ liệu
│   └── config.py          # Cấu hình server
├── client/                # Client Logic & ViewModel
│   ├── client.py          # Client chính
│   ├── view_model.py      # ViewModel xử lý logic
│   ├── network.py         # Xử lý kết nối mạng
│   └── config.py          # Cấu hình client
├── ui/                    # Giao diện người dùng
│   ├── console_ui.py      # UI console
│   ├── gui_ui.py          # UI GUI (Tkinter)
│   └── ui_base.py         # Base class cho UI
├── data/                  # Câu hỏi và dữ liệu
│   ├── questions.json     # Bộ câu hỏi
│   ├── questions_generator.py  # Tạo câu hỏi tự động
│   └── sample_data.py     # Dữ liệu mẫu
├── tests/                 # Kiểm thử
│   ├── test_server.py     # Test server
│   ├── test_client.py     # Test client
│   └── integration_test.py # Test tích hợp
├── docs/                  # Tài liệu
│   ├── setup.md           # Hướng dẫn cài đặt
│   ├── user_guide.md      # Hướng dẫn sử dụng
│   └── api_docs.md        # Tài liệu API
├── requirements.txt       # Dependencies
├── run_server.py          # Script chạy server
├── run_client.py          # Script chạy client
└── README.md              # File này
```

## Cài đặt và chạy

### Yêu cầu hệ thống
- Python 3.8+
- Các thư viện trong requirements.txt

### Cài đặt
```bash
pip install -r requirements.txt
```

### Chạy Server
```bash
python run_server.py
```

### Chạy Client
```bash
python run_client.py
```

## Tính năng chính
- ✅ Kết nối đa client qua TCP socket
- ✅ Gửi câu hỏi đồng thời cho tất cả người chơi
- ✅ Tính điểm dựa trên tốc độ trả lời
- ✅ Bảng xếp hạng realtime
- ✅ Giao diện console và GUI
- ✅ Lưu trữ dữ liệu trận đấu
- ✅ Hệ thống câu hỏi đa dạng

## Team Development
- **Thành viên 1**: Backend/Server & Database
- **Thành viên 2**: Client Logic & ViewModel
- **Thành viên 3**: UI/View
- **Thành viên 4**: Questions & Testing

## License
MIT License 