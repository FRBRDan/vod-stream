# server/rtsp_server.py
import socket

class RTSPPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.setup_server()

    def setup_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"RTSP server listening on {self.host}:{self.port}")

    def accept_client(self):
        while True:
            client_connection, client_address = self.server_socket.accept()
            print(f"Accepted connection from {client_address}")
            # Here you would start a new thread to handle the client session
