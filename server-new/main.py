# server/main.py
from rtsp_server import RTSPPServer
import threading

def main():
    rtsp_server = RTSPPServer('localhost', 8554)
    server_thread = threading.Thread(target=rtsp_server.accept_client)
    server_thread.start()

if __name__ == "__main__":
    main()
