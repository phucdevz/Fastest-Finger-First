# Fastest Finger First - Project Review & Team Assignment

## 📋 Tổng quan dự án

**Fastest Finger First** là một game trả lời câu hỏi trực tuyến theo thời gian thực, sử dụng kiến trúc Client-Server với giao thức Socket. Người chơi sẽ thi đấu để trả lời câu hỏi nhanh nhất và chính xác nhất.

### 🏗️ Kiến trúc hệ thống
- **Server**: Python Socket Server với kiến trúc MVVM
- **Client**: Python Client với giao diện console/GUI
- **Database**: JSON file cho câu hỏi và lịch sử
- **Communication**: Socket TCP/IP

---

## 👥 Phân công thành viên nhóm

### 🎯 **Thành viên 1: Nguyễn Trường Phục**
**Vai trò:** Backend/Server & Database Developer

#### 📁 Files phụ trách:
- `server/main.py` - Entry point khởi động server
- `server/model/question.py` - Quản lý bộ câu hỏi, định nghĩa class Question
- `server/model/player.py` - Thông tin người chơi trên server
- `server/model/scoreboard.py` - Bảng điểm, lưu trạng thái trận đấu
- `server/utils/helpers.py` - Hàm tiện ích, đọc file câu hỏi, format message

#### 🔧 Nhiệm vụ chính:
- Code xử lý socket server
- Quản lý game flow và logic
- Xử lý data retrieval và storage
- Viết các helper functions cho server
- Đảm bảo tính ổn định và hiệu suất của server

---

### 🎯 **Thành viên 2: Nguyễn Đức Lượng**
**Vai trò:** Client Logic & ViewModel Developer

#### 📁 Files phụ trách:
- `client/main.py` - Entry point khởi động client
- `client/viewmodel/game_viewmodel.py` - Quản lý logic xử lý, nhận câu hỏi, gửi đáp án
- `client/model/player.py` - Lưu thông tin user, trạng thái cá nhân
- `client/model/question.py` - Câu hỏi đã nhận, lưu đáp án local
- `client/utils/helpers.py` - Hàm tiện ích (validate input, format text)

#### 🔧 Nhiệm vụ chính:
- Logic nhận câu hỏi từ server
- Xử lý gửi đáp án về server
- Quản lý trạng thái client
- Đồng bộ hóa UI với server
- Viết các helper functions cho client

---

### 🎯 **Thành viên 3: Lê Đức Anh**
**Vai trò:** UI/View Developer

#### 📁 Files phụ trách:
- `client/view/client_ui.py` - Giao diện người chơi (console/GUI)
- `server/view/server_ui.py` - Giao diện admin monitoring
- `data/questions.json` - Bộ câu hỏi test

#### 🔧 Nhiệm vụ chính:
- Thiết kế giao diện người chơi
- Tạo giao diện admin để monitor server
- Nhập/xuất dữ liệu người dùng
- Tạo bộ câu hỏi test ban đầu
- Đảm bảo UX/UI thân thiện

---

### 🎯 **Thành viên 4: Nguyễn Phạm Thiên Phước**
**Vai trò:** Testing & Documentation Lead

#### 📁 Files phụ trách:
- `data/questions.json` - Bộ câu hỏi hoàn chỉnh
- `data/history.log` - Log lịch sử trận đấu (nếu có)
- `docs/report.md` - Báo cáo dự án
- `docs/presentation.pptx` - Slide thuyết trình
- `README.md` - Hướng dẫn dự án

#### 🔧 Nhiệm vụ chính:
- Soạn thảo bộ câu hỏi đầy đủ
- Testing chức năng toàn bộ hệ thống
- Viết báo cáo dự án chi tiết
- Chuẩn bị slide thuyết trình
- Viết hướng dẫn sử dụng

---

## 📊 Tiến độ dự án

### ✅ **Giai đoạn 1: Setup & Foundation**
- [x] Tạo cấu trúc thư mục
- [x] Tạo các file cơ bản
- [x] Phân công nhiệm vụ

### 🔄 **Giai đoạn 2: Core Development**
- [ ] Backend Server Development (Nguyễn Trường Phục)
- [ ] Client Logic Development (Nguyễn Đức Lượng)
- [ ] UI Development (Lê Đức Anh)
- [ ] Question Bank Creation (Nguyễn Phạm Thiên Phước)

### ⏳ **Giai đoạn 3: Integration & Testing**
- [ ] Integration testing
- [ ] Performance testing
- [ ] Bug fixing
- [ ] Documentation completion

### 🎯 **Giai đoạn 4: Finalization**
- [ ] Final testing
- [ ] Report completion
- [ ] Presentation preparation
- [ ] Project delivery

---

## 🎯 Mục tiêu dự án

### **Chức năng chính:**
1. **Multiplayer Quiz Game**: Hỗ trợ nhiều người chơi cùng lúc
2. **Real-time Competition**: Thi đấu theo thời gian thực
3. **Score Tracking**: Theo dõi điểm số và xếp hạng
4. **Question Management**: Quản lý bộ câu hỏi linh hoạt
5. **Admin Interface**: Giao diện quản trị cho server

### **Công nghệ sử dụng:**
- **Backend**: Python Socket, JSON
- **Frontend**: Python (Tkinter/PyQt hoặc Console)
- **Communication**: TCP/IP Socket
- **Data Storage**: JSON files
- **Architecture**: MVVM Pattern

---

## 📈 Đánh giá rủi ro

### **Rủi ro kỹ thuật:**
- **Network latency**: Có thể ảnh hưởng đến trải nghiệm real-time
- **Concurrent connections**: Cần xử lý nhiều kết nối đồng thời
- **Data synchronization**: Đồng bộ dữ liệu giữa client-server

### **Rủi ro dự án:**
- **Time management**: Cần phân bổ thời gian hợp lý
- **Team coordination**: Đảm bảo giao tiếp hiệu quả giữa các thành viên
- **Quality assurance**: Testing đầy đủ trước khi demo

---

## 🎉 Kết luận

Dự án **Fastest Finger First** với sự phân công rõ ràng cho 4 thành viên sẽ đảm bảo:
- **Nguyễn Trường Phục**: Xây dựng nền tảng server vững chắc
- **Nguyễn Đức Lượng**: Phát triển logic client mượt mà
- **Lê Đức Anh**: Tạo giao diện thân thiện người dùng
- **Nguyễn Phạm Thiên Phước**: Đảm bảo chất lượng và tài liệu

Với kiến trúc MVVM và phân chia trách nhiệm rõ ràng, dự án sẽ được hoàn thành hiệu quả và đạt chất lượng cao.

---

*Ngày tạo: 20/07/2025*  
*Phiên bản: 1.0* 