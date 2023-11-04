import socket
import threading
from pathlib import Path
import vlc

VIDEO_DIR = Path("videos")


class ClientHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        # Handle client requests (RTSP, RTP, RTCP)

        # For simplicity, just send a list of movies as a response
        movie_list = '\n'.join([video.name for video in VIDEO_DIR.iterdir()])
        self.client_socket.sendall(movie_list.encode())

        # After sending movie list, wait for client's choice
        chosen_movie = self.client_socket.recv(1024).decode()
        video_path = VIDEO_DIR / chosen_movie

        # Start VLC instance to stream video via RTSP
        instance = vlc.Instance("--no-xlib")
        media = instance.media_new_path(video_path)

        # RTSP stream setup
        stream_output = f"sout=#rtp{{sdp=rtsp://:5555/{chosen_movie}}}"
        media.add_option(stream_output)

        player = instance.media_player_new()
        player.set_media(media)
        player.play()

        # Keep the connection open to handle potential RTSP commands
        # This is a basic example; a full implementation would handle commands like PAUSE, PLAY, etc.
        self.client_socket.recv(1024)
        player.stop()
        self.client_socket.close()
        print(f"Streamed {chosen_movie} and closed connection")


def main():
    HOST = 'localhost'
    PORT = 65432

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"Server started on {HOST}:{PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}.")
            client_handler = ClientHandler(client_socket)
            client_handler.start()


if __name__ == "__main__":
    main()
