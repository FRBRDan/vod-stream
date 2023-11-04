import socket
from gui import VideoPlayerGUI
import vlc

HOST = 'localhost'
PORT = 65432


class VODClient:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((HOST, PORT))
        video_list = self.socket.recv(1024).decode().split('\n')
        self.gui = VideoPlayerGUI(self, video_list)

    def request_video(self, video_name):
        # Send request for a specific video
        # Handle RTP stream and RTCP feedback
        print(f"Inside request_video, requesting {video_name}")
        self.socket.sendall(video_name.encode())

        # In a full-featured implementation, you'd handle RTSP controls here.


if __name__ == "__main__":
    client = VODClient()
