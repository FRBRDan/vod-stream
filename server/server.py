import socket
import threading
from pathlib import Path

VIDEO_DIR = Path("videos")


class ClientHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        # Handle client requests (RTSP, RTP, RTCP)

        # For simplicity, just send a list of movies as a response
        movie_list = '\n'.join([video.name for video in VIDEO_DIR.iterdir()])
        print(movie_list, type(movie_list))
        self.client_socket.sendall(movie_list.encode())

        # Here you would handle the RTSP handshake, setup RTP stream, handle RTCP feedback, etc.

        self.client_socket.close()
        print("Closed socket")


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
