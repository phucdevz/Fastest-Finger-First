#!/usr/bin/env python3
"""
Script để chạy client Vua Tốc Độ
"""

import sys
import os

# Add client directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'client'))

from client.main import GameClient

def main():
    print("🎮 Khởi động Client Vua Tốc Độ...")
    print("=" * 50)
    
    try:
        client = GameClient()
        print("✅ Client đã sẵn sàng!")
        print("🖥️  Mở giao diện...")
        print("=" * 50)
        
        client.start()
        
    except KeyboardInterrupt:
        print("\n⏹️  Dừng client...")
        print("✅ Client đã dừng!")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 