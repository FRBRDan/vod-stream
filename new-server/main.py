# server/main.py
from rtsp_server import RTSPPServer
import threading

def main():
    rtsp_server = RTSPPServer('localhost', 8554)
    rtsp_server.run_server()

if __name__ == "__main__":
    main()