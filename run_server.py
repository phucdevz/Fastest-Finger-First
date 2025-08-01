#!/usr/bin/env python3
"""
Script để chạy server Vua Tốc Độ
"""

import sys
import os

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from server.main import GameServer

def main():
    print("🚀 Khởi động Server Vua Tốc Độ...")
    print("=" * 50)
    
    try:
        server = GameServer()
        print("✅ Server đã sẵn sàng!")
        print("📡 Đang lắng nghe kết nối...")
        print("=" * 50)
        
        server.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  Dừng server...")
        server.stop()
        print("✅ Server đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 