# Hướng dẫn sử dụng Fastest Finger First

## Tổng quan

Fastest Finger First là một game trả lời câu hỏi nhanh với kiến trúc Client-Server. Người chơi sẽ cạnh tranh để trả lời câu hỏi nhanh nhất và chính xác nhất.

## Cách chơi

### Luật chơi cơ bản
1. **Kết nối**: Người chơi kết nối đến server
2. **Tham gia phòng**: Vào phòng chờ với các người chơi khác
3. **Trả lời câu hỏi**: Khi câu hỏi xuất hiện, trả lời nhanh nhất có thể
4. **Tính điểm**: 
   - Đáp án đúng: 10 điểm
   - Trả lời nhanh nhất: +5 điểm thưởng
   - Đáp án sai: 0 điểm (không bị trừ điểm)

### Thời gian
- **Thời gian trả lời**: 30 giây mỗi câu hỏi
- **Thời gian chờ**: 3 giây giữa các câu hỏi
- **Số câu hỏi**: Tối đa 10 câu mỗi trận

## Hướng dẫn sử dụng

### Cho người chơi (Client)

#### 1. Khởi động Client
```bash
python run_client.py
```

#### 2. Nhập thông tin
- **Username**: Tên người chơi (bắt buộc)
- **Server**: Địa chỉ server (mặc định: localhost)
- **Port**: Port server (mặc định: 5555)

#### 3. Kết nối và chơi
1. **Kết nối**: Gõ `connect` để kết nối server
2. **Tham gia phòng**: Gõ `join` để vào phòng chơi
3. **Chờ người chơi**: Đợi đủ 2+ người chơi
4. **Trả lời câu hỏi**: 
   - Đọc câu hỏi và các lựa chọn
   - Gõ đáp án: `A`, `B`, `C`, `D` hoặc `1`, `2`, `3`, `4`
5. **Xem kết quả**: Theo dõi điểm số và bảng xếp hạng

#### 4. Lệnh trong game
- `connect` - Kết nối server
- `join` - Tham gia phòng
- `leave` - Rời phòng
- `quit` - Thoát game

### Cho quản trị viên (Server)

#### 1. Khởi động Server
```bash
python run_server.py
```

#### 2. Quản lý server
- Server sẽ tự động chạy và chờ kết nối
- Theo dõi log để kiểm tra hoạt động
- Có thể dừng bằng `Ctrl+C`

#### 3. Cấu hình server
Chỉnh sửa file `server/config.py`:
```python
# Thay đổi port nếu cần
PORT = 5555

# Điều chỉnh thời gian
QUESTION_TIME_LIMIT = 30
WAIT_TIME_BETWEEN_QUESTIONS = 3

# Số người chơi tối thiểu
MIN_PLAYERS_TO_START = 2
```

## Giao diện

### Console UI
```
============================================================
Player: Player1 | State: playing
============================================================

==================================================
QUESTION 1
==================================================
Thủ đô của Việt Nam là gì?

1. Hà Nội
2. TP. Hồ Chí Minh
3. Đà Nẵng
4. Huế

Type your answer (A, B, C, D or 1, 2, 3, 4):

==============================
LEADERBOARD
==============================
 1. Player1        15 pts
 2. Player2        10 pts

============================================================
Commands: connect, join, leave, quit
============================================================
>>> 
```

### Màu sắc và ký hiệu
- 🟢 **Xanh lá**: Kết nối thành công, đáp án đúng
- 🟡 **Vàng**: Cảnh báo, thông báo
- 🔴 **Đỏ**: Lỗi, ngắt kết nối
- 🔵 **Xanh dương**: Thông tin
- 🏆 **Cup**: Người thắng
- ⏱️ **Đồng hồ**: Thời gian

## Tính năng nâng cao

### Bảng xếp hạng
- Hiển thị top 10 người chơi
- Cập nhật realtime
- Hiển thị điểm số và thống kê

### Lịch sử trận đấu
- Lưu trữ tất cả trận đấu
- Thống kê người chơi
- Xuất báo cáo

### Tùy chỉnh câu hỏi
- Thêm câu hỏi mới vào `data/questions.json`
- Tạo câu hỏi tự động bằng `data/questions_generator.py`
- Phân loại theo chủ đề và độ khó

## Mẹo chơi

### Tối ưu tốc độ
1. **Đọc nhanh**: Tập trung vào từ khóa chính
2. **Phân tích nhanh**: Loại trừ đáp án sai rõ ràng
3. **Phản xạ nhanh**: Luyện tập thường xuyên

### Chiến lược
1. **Cân bằng**: Không vội vàng trả lời sai
2. **Theo dõi**: Quan sát điểm số đối thủ
3. **Tập trung**: Tránh phân tâm khi chơi

### Kỹ thuật
1. **Sử dụng phím tắt**: A, B, C, D thay vì 1, 2, 3, 4
2. **Đọc trước**: Đọc câu hỏi khi đang chờ
3. **Dự đoán**: Đoán câu hỏi tiếp theo

## Xử lý sự cố

### Lỗi kết nối
```
[ERROR] Connection failed: Connection refused
```
**Giải pháp**:
1. Kiểm tra server đã chạy chưa
2. Kiểm tra địa chỉ IP và port
3. Kiểm tra firewall

### Lỗi username
```
[ERROR] Username already exists
```
**Giải pháp**: Chọn username khác

### Lỗi đáp án
```
[WARNING] Invalid answer. Use A, B, C, D or 1, 2, 3, 4
```
**Giải pháp**: Sử dụng đúng định dạng đáp án

### Mất kết nối
```
[WARNING] Lost connection to server
```
**Giải pháp**:
1. Đợi tự động kết nối lại
2. Hoặc gõ `connect` để kết nối lại thủ công

## Thống kê và báo cáo

### Thống kê cá nhân
- Tổng số trận đã chơi
- Điểm số cao nhất
- Tỷ lệ đáp án đúng
- Thời gian phản hồi trung bình

### Báo cáo trận đấu
- Người thắng và điểm số
- Thời gian trận đấu
- Số câu hỏi đã trả lời
- Chi tiết từng câu hỏi

## Hỗ trợ

### Liên hệ hỗ trợ
- **Email**: support@fastestfingerfirst.com
- **GitHub**: https://github.com/your-username/Fastest-Finger-First/issues
- **Discord**: https://discord.gg/fastestfingerfirst

### Tài liệu thêm
- [Hướng dẫn cài đặt](setup.md)
- [API Documentation](api_docs.md)
- [FAQ](faq.md)

### Báo lỗi
Khi báo lỗi, vui lòng cung cấp:
1. Phiên bản Python
2. Hệ điều hành
3. Mô tả lỗi chi tiết
4. Log file (nếu có)
5. Các bước tái hiện lỗi 