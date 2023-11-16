import socket
from gui import VideoPlayerGUI

HOST = 'localhost'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

class VODClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((HOST, PORT))
            video_list = self.socket.recv(1024).decode().split('\n')
            self.gui = VideoPlayerGUI(self, video_list)
        except ConnectionError as e:
            print(f"Could not connect to server: {e}")
            exit(1)  # Exit if no connection could be made

    def request_video(self, video_name):
        try:
            self.socket.sendall(video_name.encode())
        except BrokenPipeError as e:
            print(f"Error sending video request: {e}")
            # Handle the error (e.g., try to reconnect, notify the user, etc.)


if __name__ == "__main__":
    client = VODClient()
