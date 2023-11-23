# client/rtsp_client.py
import socket

class RTSPClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.rtsp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.session_id = None

    def connect(self):
        try:
            self.rtsp_socket.connect((self.server_ip, self.server_port))
            print("Connected to RTSP server.")
        except Exception as e:
            print(f"Connection to RTSP server failed: {e}")

    def send_request(self, request_type, video_name):
        if request_type.upper() not in ["SETUP", "PLAY", "PAUSE", "TEARDOWN"]:
            print("Unknown RTSP request type.")
            return

        # Construct the RTSP request
        request = f"{request_type} {video_name} RTSP/1.0\nCSeq: 1\n"
        if self.session_id:
            request += f"Session: {self.session_id}\n"

        try:
            # Send the RTSP request
            self.rtsp_socket.send(request.encode())

            # Receive the server's response
            response = self.rtsp_socket.recv(1024)
            print("Server response:", response.decode())

            # Parse the session ID from the server's response
            if 'Session' in response.decode():
                self.session_id = response.decode().split('Session: ')[1].split('\n')[0]

        except socket.error as e:
            print(f"Socket error: {e}")
        except Exception as e:
            print(f"Error sending RTSP request: {e}")

    def teardown(self):
        if self.session_id:
            self.send_request("TEARDOWN", "")
            self.rtsp_socket.close()
            print(f"RTSP session {self.session_id} torn down.")
