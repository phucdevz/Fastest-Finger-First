# Hướng dẫn cài đặt Fastest Finger First

## Yêu cầu hệ thống

### Phần mềm cần thiết
- **Python 3.8+** (khuyến nghị Python 3.9 hoặc 3.10)
- **Git** (để clone repository)

### Hệ điều hành hỗ trợ
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

## Cài đặt

### Bước 1: Clone repository
```bash
git clone https://github.com/your-username/Fastest-Finger-First.git
cd Fastest-Finger-First
```

### Bước 2: Tạo môi trường ảo (khuyến nghị)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Bước 3: Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Bước 4: Kiểm tra cài đặt
```bash
# Test import các module
python -c "import server; import client; import data; print('Installation successful!')"
```

## Cấu hình

### Cấu hình Server
File: `server/config.py`
```python
# Cấu hình mạng
HOST = 'localhost'  # Địa chỉ IP server
PORT = 5555         # Port server

# Cấu hình game
QUESTION_TIME_LIMIT = 30  # Thời gian trả lời (giây)
MIN_PLAYERS_TO_START = 2  # Số người chơi tối thiểu
MAX_QUESTIONS_PER_GAME = 10  # Số câu hỏi tối đa
```

### Cấu hình Client
File: `client/config.py`
```python
# Cấu hình kết nối
SERVER_HOST = 'localhost'  # Địa chỉ server
SERVER_PORT = 5555         # Port server

# Cấu hình giao diện
UI_TYPE = 'console'  # 'console' hoặc 'gui'
```

## Chạy ứng dụng

### Chạy Server
```bash
# Cách 1: Sử dụng script
python run_server.py

# Cách 2: Chạy trực tiếp
python -m server.server
```

### Chạy Client
```bash
# Cách 1: Sử dụng script
python run_client.py

# Cách 2: Với tham số
python run_client.py --username "YourName" --host "localhost" --port 5555

# Cách 3: Chạy trực tiếp
python -m client.client
```

## Kiểm tra hoạt động

### Test đơn vị
```bash
# Test server
python -m unittest tests.test_server

# Test client
python -m unittest tests.test_client

# Test tích hợp
python -m unittest tests.integration_test
```

### Test thủ công
1. Chạy server: `python run_server.py`
2. Mở terminal mới, chạy client: `python run_client.py`
3. Nhập username và thử kết nối
4. Mở thêm client khác để test multiplayer

## Xử lý lỗi thường gặp

### Lỗi Import
```
ModuleNotFoundError: No module named 'server'
```
**Giải pháp**: Đảm bảo đang ở thư mục gốc của project

### Lỗi Port đã được sử dụng
```
Address already in use
```
**Giải pháp**: 
- Thay đổi port trong config
- Hoặc kill process đang sử dụng port: `netstat -ano | findstr 5555`

### Lỗi kết nối
```
Connection refused
```
**Giải pháp**:
- Kiểm tra server đã chạy chưa
- Kiểm tra firewall
- Kiểm tra địa chỉ IP và port

### Lỗi Database
```
sqlite3.OperationalError: database is locked
```
**Giải pháp**: Đảm bảo không có process nào khác đang sử dụng database

## Cấu trúc thư mục sau cài đặt
```
Fastest-Finger-First/
├── server/                 # Backend/Server
├── client/                 # Client Logic & ViewModel
├── ui/                     # Giao diện người dùng
├── data/                   # Câu hỏi và dữ liệu
├── tests/                  # Kiểm thử
├── docs/                   # Tài liệu
├── venv/                   # Môi trường ảo (nếu có)
├── game_data.db           # Database (tự tạo)
├── server.log             # Log server (tự tạo)
├── requirements.txt       # Dependencies
├── run_server.py          # Script chạy server
├── run_client.py          # Script chạy client
└── README.md              # File này
```

## Gỡ cài đặt
```bash
# Xóa môi trường ảo
deactivate  # Nếu đang sử dụng venv
rm -rf venv/  # Linux/macOS
rmdir /s venv  # Windows

# Xóa database và log
rm game_data.db server.log  # Linux/macOS
del game_data.db server.log  # Windows
```

## Hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra log file `server.log`
2. Chạy test để xác định lỗi
3. Tạo issue trên GitHub với thông tin chi tiết
4. Liên hệ team development 