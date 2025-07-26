import socket
import threading
import json
import time

from viewmodel.game_viewmodel import GameViewModel
from view.client_ui import ClientUI

def main():
    print("\n===== FASTEST FINGER FIRST - CLIENT =====\n")

    host = input("Nhập địa chỉ server [localhost]: ") or "localhost"
    port_input = input("Nhập cổng server [5000]: ") or "5000"
    port = int(port_input)

    player_name = input("Nhập tên người chơi: ").strip()
    if not player_name:
        print("Tên người chơi không được để trống.")
        return

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        print(f"\nĐã kết nối tới server {host}:{port}\n")
    except Exception as e:
        print(f"Không thể kết nối server: {e}")
        return

    ui = ClientUI()
    viewmodel = GameViewModel(sock, player_name, ui)
    viewmodel.send_connect()

    def receive_loop():
        buffer = ""
        while True:
            try:
                data = sock.recv(4096)
                if not data:
                    print("\nServer ngắt kết nối.\n")
                    break
                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        message = json.loads(line)
                        viewmodel.handle_message(message)
            except Exception as e:
                print(f"\nLỗi khi nhận tin: {e}\n")
                break

    threading.Thread(target=receive_loop, daemon=True).start()

    try:
        while True:
            cmd = ui.get_user_command()
            viewmodel.handle_user_input(cmd)
    except KeyboardInterrupt:
        print("\nĐang thoát...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
