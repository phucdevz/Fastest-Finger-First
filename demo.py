#!/usr/bin/env python3
"""
Demo script để chạy toàn bộ hệ thống Vua Tốc Độ
"""

import subprocess
import sys
import os
import time
import threading
import tkinter as tk
from tkinter import messagebox

def run_server():
    """Chạy server trong background"""
    try:
        subprocess.run([sys.executable, "run_server.py"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
    except Exception as e:
        print(f"❌ Lỗi chạy server: {e}")

def run_client():
    """Chạy client"""
    try:
        subprocess.run([sys.executable, "run_client.py"])
    except Exception as e:
        print(f"❌ Lỗi chạy client: {e}")

def main():
    print("🎮 Vua Tốc Độ - Fastest Finger First")
    print("=" * 50)
    print("🚀 Khởi động demo...")
    
    # Kiểm tra Python version
    if sys.version_info < (3, 7):
        print("❌ Yêu cầu Python 3.7+")
        return
    
    # Kiểm tra tkinter
    try:
        import tkinter
    except ImportError:
        print("❌ Tkinter không có sẵn. Vui lòng cài đặt Python với Tkinter.")
        return
    
    # Tạo GUI cho demo
    root = tk.Tk()
    root.title("Vua Tốc Độ - Demo")
    root.geometry("400x300")
    root.configure(bg='#1a1a1a')
    
    # Title
    title_label = tk.Label(
        root,
        text="VUA TỐC ĐỘ",
        font=("Arial", 24, "bold"),
        fg="#FFD700",
        bg="#1a1a1a"
    )
    title_label.pack(pady=(20, 10))
    
    subtitle_label = tk.Label(
        root,
        text="Fastest Finger First",
        font=("Arial", 12),
        fg="#FFFFFF",
        bg="#1a1a1a"
    )
    subtitle_label.pack(pady=(0, 30))
    
    # Buttons frame
    buttons_frame = tk.Frame(root, bg="#1a1a1a")
    buttons_frame.pack()
    
    def start_server():
        """Bắt đầu server"""
        print("🚀 Khởi động server...")
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Chờ server khởi động
        messagebox.showinfo("Thông báo", "Server đã khởi động!\nBây giờ có thể chạy client.")
    
    def start_client():
        """Bắt đầu client"""
        print("🎮 Khởi động client...")
        client_thread = threading.Thread(target=run_client, daemon=True)
        client_thread.start()
    
    def start_both():
        """Bắt đầu cả server và client"""
        print("🚀 Khởi động toàn bộ hệ thống...")
        start_server()
        time.sleep(3)  # Chờ server khởi động
        start_client()
    
    def test_connection():
        """Test kết nối"""
        print("🧪 Test kết nối...")
        subprocess.run([sys.executable, "test_client.py"])
    
    # Buttons
    server_btn = tk.Button(
        buttons_frame,
        text="🚀 Chạy Server",
        font=("Arial", 12, "bold"),
        bg="#4CAF50",
        fg="#FFFFFF",
        width=20,
        height=2,
        command=start_server
    )
    server_btn.pack(pady=10)
    
    client_btn = tk.Button(
        buttons_frame,
        text="🎮 Chạy Client",
        font=("Arial", 12, "bold"),
        bg="#2196F3",
        fg="#FFFFFF",
        width=20,
        height=2,
        command=start_client
    )
    client_btn.pack(pady=10)
    
    both_btn = tk.Button(
        buttons_frame,
        text="🎯 Chạy Cả Hai",
        font=("Arial", 12, "bold"),
        bg="#FF9800",
        fg="#FFFFFF",
        width=20,
        height=2,
        command=start_both
    )
    both_btn.pack(pady=10)
    
    test_btn = tk.Button(
        buttons_frame,
        text="🧪 Test Kết Nối",
        font=("Arial", 12, "bold"),
        bg="#9C27B0",
        fg="#FFFFFF",
        width=20,
        height=2,
        command=test_connection
    )
    test_btn.pack(pady=10)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Hướng dẫn:\n1. Chạy Server trước\n2. Sau đó chạy Client\n3. Hoặc chạy 'Cả Hai' để tự động",
        font=("Arial", 10),
        fg="#CCCCCC",
        bg="#1a1a1a",
        justify=tk.LEFT
    )
    instructions.pack(pady=(20, 0))
    
    # Start GUI
    root.mainloop()

if __name__ == "__main__":
    main() 