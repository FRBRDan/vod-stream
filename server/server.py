import socket
import threading
from pathlib import Path
import vlc

VIDEO_DIR = Path("videos")  # Ensure this directory exists and contains video files

class ClientHandler(threading.Thread):
    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket

    def run(self):
        try:
            print("ClientHandler started.")
            movie_list = '\n'.join([video.name for video in VIDEO_DIR.iterdir() if video.is_file()])
            self.client_socket.sendall(movie_list.encode())

            chosen_movie = self.client_socket.recv(1024).decode()
            print(f"Client requested: {chosen_movie}")
            video_path = VIDEO_DIR / chosen_movie

            if not video_path.exists() or not video_path.is_file():
                print(f"Requested video {chosen_movie} does not exist.")
                return

            instance = vlc.Instance("--no-xlib", "-vvv")  # Increase verbosity
            media = instance.media_new_path(str(video_path))

            stream_output = (
                f"sout=#transcode{{vcodec=h264,scale=Auto,acodec=mpga,ab=128,channels=2,samplerate=44100}}:"
                f"rtp{{sdp=rtsp://:5555/{chosen_movie}}}"
            )
            media.add_option(stream_output)

            player = instance.media_player_new()
            player.set_media(media)
            print(f"Starting stream for {chosen_movie}")
            player.play()

            # Keep the stream alive until the client disconnects
            self.client_socket.recv(1024)
            print(f"Stopping stream for {chosen_movie}")
            player.stop()
            player.release()  # Ensure player is released

        except Exception as e:
            print(f"An error occurred with client: {e}")
        finally:
            self.client_socket.close()
            print(f"Closed connection with client.")

def main():
    HOST = 'localhost'  # Standard loopback interface address (localhost)
    PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()

        print(f"Server started on {HOST}:{PORT}")
        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Accepted connection from {addr}.")
                client_handler = ClientHandler(client_socket)
                client_handler.start()
        except KeyboardInterrupt:
            print("\nServer is shutting down.")

if __name__ == "__main__":
    main()
