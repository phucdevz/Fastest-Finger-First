#!/usr/bin/env python3
"""
Script chạy client Fastest Finger First
"""

import sys
import os
import argparse
from pathlib import Path

# Thêm thư mục gốc vào path
sys.path.insert(0, str(Path(__file__).parent))

from client.client import GameClient

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Fastest Finger First Client')
    parser.add_argument('--username', '-u', type=str, help='Username for the game')
    parser.add_argument('--ui', type=str, choices=['console', 'gui'], 
                       default='console', help='UI type to use')
    parser.add_argument('--host', type=str, default='localhost', 
                       help='Server host')
    parser.add_argument('--port', type=int, default=5555, 
                       help='Server port')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("    FASTEST FINGER FIRST - CLIENT")
    print("=" * 60)
    
    # Cập nhật cấu hình
    import client.config as client_config
    client_config.SERVER_HOST = args.host
    client_config.SERVER_PORT = args.port
    
    # Lấy username nếu không được cung cấp
    username = args.username
    if not username:
        # Check if we're running in an interactive environment
        try:
            # Try to get input, but if it fails (non-interactive), use default
            username = input("Enter your username: ").strip()
            if not username:
                username = "Player"
        except (EOFError, OSError):
            # Non-interactive environment (like subprocess), use default
            username = "Player"
            print(f"Using default username: {username}")
    
    print(f"Connecting to server {args.host}:{args.port}")
    print(f"Username: {username}")
    print(f"UI Type: {args.ui}")
    print("=" * 60)
    
    # Tạo và chạy client
    client = GameClient(ui_type=args.ui)
    
    try:
        client.start(username=username)
    except KeyboardInterrupt:
        print("\nShutting down client...")
        client.stop()
    except Exception as e:
        print(f"Error: {e}")
        client.stop()

if __name__ == "__main__":
    main() 