#!/usr/bin/env python3
"""
Demo script cho Fastest Finger First
Chạy server và client để test hệ thống
"""

import sys
import time
import threading
import subprocess
from pathlib import Path

def run_server():
    """Chạy server trong thread riêng"""
    print("Starting server...")
    subprocess.run([sys.executable, "run_server.py"])

def run_client(username):
    """Chạy client"""
    print(f"Starting client for {username}...")
    subprocess.run([sys.executable, "run_client.py", "--username", username])

def main():
    """Main function"""
    print("=" * 60)
    print("    FASTEST FINGER FIRST - DEMO")
    print("=" * 60)
    
    # Kiểm tra các file cần thiết
    required_files = [
        "run_server.py",
        "run_client.py", 
        "server/server.py",
        "client/client.py",
        "data/questions.json"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Missing required file: {file}")
            return
        else:
            print(f"✅ Found: {file}")
    
    print("\nStarting demo...")
    print("This will start a server and 2 clients for testing")
    print("Press Ctrl+C to stop the demo")
    print("=" * 60)
    
    try:
        # Khởi động server trong thread riêng
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Đợi server khởi động
        time.sleep(2)
        
        # Khởi động 2 client
        client1_thread = threading.Thread(target=run_client, args=("Player1",), daemon=True)
        client2_thread = threading.Thread(target=run_client, args=("Player2",), daemon=True)
        
        client1_thread.start()
        time.sleep(1)
        client2_thread.start()
        
        # Đợi các thread hoàn thành
        server_thread.join()
        
    except KeyboardInterrupt:
        print("\nDemo stopped by user")
    except Exception as e:
        print(f"Demo error: {e}")

if __name__ == "__main__":
    main() 