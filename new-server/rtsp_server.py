# server/rtsp_server.py
import socket
import threading
import logging
from video_streamer import VideoStreamer

# Set up logging
logging.basicConfig(level=logging.INFO)

class RTSPPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.setup_server()

    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        logging.info(f"RTSP server listening on {self.host}:{self.port}")

    def run_server(self):
        try:
            while True:
                client_connection, client_address = self.server_socket.accept()
                logging.info(f"Accepted connection from {client_address}")
                client_handler = threading.Thread(
                    target=self.handle_client,
                    args=(client_connection, client_address)
                )
                client_handler.start()
        except Exception as e:
            logging.error(f"Server run encountered an error: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
                logging.info("Server socket closed.")

    def handle_client(self, connection, address):
        try:
            while True:
                request = connection.recv(1024).decode()
                if not request:
                    break  # Client has disconnected

                logging.info(f"Received request from {address}:\n{request}")
                self.process_request(request, connection, address)
        except Exception as e:
            logging.error(f"Error handling client {address}: {e}")
        finally:
            if address in self.clients:
                self.clients[address]['streamer'].stop_streaming()
                del self.clients[address]
            connection.close()

    def process_request(self, request, connection, address):
        lines = request.split('\n')
        method = lines[0].split(' ')[0]
        video_name = lines[0].split(' ')[1]
        video_path = self.get_video_path(video_name)

        if method == "SETUP" and video_path:
            self.clients[address] = {
                'streamer': VideoStreamer(address, video_path),
                'state': "INIT"
            }
            self.clients[address]['streamer'].setup_stream()
            response = "RTSP/1.0 200 OK\nCSeq: 2\nSession: {}\n".format(self.clients[address]['streamer'].session_id)
            connection.send(response.encode())
        elif method == "PLAY" and address in self.clients and self.clients[address]['state'] == "INIT":
            threading.Thread(target=self.clients[address]['streamer'].stream_video).start()
            self.clients[address]['state'] = "PLAYING"
            response = "RTSP/1.0 200 OK\nCSeq: 3\nSession: {}\n".format(self.clients[address]['streamer'].session_id)
            connection.send(response.encode())
        elif method == "PAUSE" and address in self.clients and self.clients[address]['state'] == "PLAYING":
            self.clients[address]['streamer'].pause_streaming()
            self.clients[address]['state'] = "PAUSED"
            response = "RTSP/1.0 200 OK\nCSeq: 4\nSession: {}\n".format(self.clients[address]['streamer'].session_id)
            connection.send(response.encode())
        elif method == "TEARDOWN" and address in self.clients:
            self.clients[address]['streamer'].stop_streaming()
            self.clients[address]['state'] = "STOPPED"
            response = "RTSP/1.0 200 OK\nCSeq: 5\nSession: {}\n".format(self.clients[address]['streamer'].session_id)
            connection.send(response.encode())

    def get_video_path(self, video_name):
        # Here you'd implement the logic to get the correct video path
        video_paths = {
            "Movie 1": "/path/to/your/video/sample.mp4",
            "Movie 2": "/path/to/your/video/test.mp4",
            "Movie 3": "/path/to/your/video/test2.mp4",
        }
        return video_paths.get(video_name, "")

# Main entry point of the RTSP server
if __name__ == "__main__":
    HOST, PORT = 'localhost', 8554
    rtsp_server = RTSPPServer(HOST, PORT)
    rtsp_server.run_server()
