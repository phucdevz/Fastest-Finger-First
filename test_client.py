#!/usr/bin/env python3
"""
Test client để kiểm tra kết nối server
"""

import socket
import json
import time
import threading

class TestClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        
    def connect(self, player_name="TestPlayer", room_id="test"):
        """Kết nối đến server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            print(f"✅ Kết nối thành công đến {self.host}:{self.port}")
            
            # Send join room message
            self._send_message({
                'type': 'JOIN_ROOM',
                'player_name': player_name,
                'room_id': room_id
            })
            
            # Start receive thread
            receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            receive_thread.start()
            
            return True
            
        except Exception as e:
            print(f"❌ Lỗi kết nối: {e}")
            return False
    
    def send_ready(self):
        """Gửi tín hiệu sẵn sàng"""
        if self.connected:
            self._send_message({
                'type': 'READY',
                'room_id': 'test'
            })
            print("📤 Đã gửi tín hiệu sẵn sàng")
    
    def send_answer(self, answer):
        """Gửi câu trả lời"""
        if self.connected:
            self._send_message({
                'type': 'ANSWER',
                'room_id': 'test',
                'answer': answer,
                'answer_time': time.time()
            })
            print(f"📤 Đã gửi đáp án: {answer}")
    
    def disconnect(self):
        """Ngắt kết nối"""
        if self.socket:
            self._send_message({
                'type': 'DISCONNECT',
                'player_name': 'TestPlayer',
                'room_id': 'test'
            })
            self.socket.close()
            self.connected = False
            print("🔌 Đã ngắt kết nối")
    
    def _send_message(self, message):
        """Gửi message đến server"""
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.send(data)
        except Exception as e:
            print(f"❌ Lỗi gửi message: {e}")
    
    def _receive_messages(self):
        """Nhận messages từ server"""
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                message = json.loads(data.decode('utf-8'))
                self._handle_message(message)
                
            except Exception as e:
                print(f"❌ Lỗi nhận message: {e}")
                break
        
        self.connected = False
        print("🔌 Mất kết nối đến server")
    
    def _handle_message(self, message):
        """Xử lý message từ server"""
        msg_type = message.get('type')
        
        if msg_type == 'JOIN_SUCCESS':
            print("✅ Tham gia phòng thành công!")
            print(f"📊 Players: {message.get('players', [])}")
            
        elif msg_type == 'JOIN_FAILED':
            print(f"❌ Tham gia phòng thất bại: {message.get('message', '')}")
            
        elif msg_type == 'GAME_START':
            print("🎮 Game bắt đầu!")
            
        elif msg_type == 'QUESTION':
            print(f"❓ Câu hỏi: {message.get('question', '')}")
            print(f"📝 Options: {message.get('options', [])}")
            
        elif msg_type == 'QUESTION_RESULT':
            print(f"✅ Đáp án đúng: {message.get('correct_answer', '')}")
            
        elif msg_type == 'SCORE_UPDATE':
            player = message.get('player_name', '')
            points = message.get('points_earned', 0)
            print(f"📊 {player}: +{points} điểm")
            
        elif msg_type == 'GAME_END':
            print("🏁 Game kết thúc!")
            print(f"🏆 Kết quả: {message.get('final_results', [])}")
            
        else:
            print(f"📨 Message: {msg_type}")

def main():
    print("🧪 Test Client Vua Tốc Độ")
    print("=" * 40)
    
    # Tạo test client
    client = TestClient()
    
    # Kết nối
    if not client.connect("TestPlayer", "test"):
        return
    
    try:
        print("\n📋 Menu:")
        print("1. Gửi sẵn sàng")
        print("2. Gửi đáp án")
        print("3. Ngắt kết nối")
        print("4. Thoát")
        
        while True:
            choice = input("\nChọn (1-4): ").strip()
            
            if choice == '1':
                client.send_ready()
            elif choice == '2':
                answer = input("Nhập đáp án (0-3): ").strip()
                try:
                    client.send_answer(int(answer))
                except ValueError:
                    print("❌ Đáp án không hợp lệ!")
            elif choice == '3':
                client.disconnect()
                break
            elif choice == '4':
                break
            else:
                print("❌ Lựa chọn không hợp lệ!")
                
    except KeyboardInterrupt:
        print("\n⏹️  Dừng test client...")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main() 