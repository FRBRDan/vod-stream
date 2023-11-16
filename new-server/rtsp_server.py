# server/rtsp_server.py
from email.utils import formatdate
from random import randint
import random
import socket
import threading
import logging
from video_streamer import VideoStreamer
from urllib.parse import urlparse

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

                logging.info(f"[--->]Received request from {address}:\n{request}")
                self.process_request(request, connection, address)
        except Exception as e:
            logging.error(f"Error handling client {address}: {e}")
        finally:
            if address not in self.clients:
                connection.close()

    def process_request(self, request, connection, address):
        lines = request.split('\r\n')
        method = lines[0].split(' ')[0]
        cseq = self.extract_cseq(request)
    
        # Extract the URL and portentially a trackID
        url = lines[0].split(' ')[1]
        url_parts = url.split('/')
        print('Url Parts: ', url_parts)
        video_name = url_parts[1] if len(url_parts) > 1 else None  # Assuming the format [host]:[port]/[video_name]/trackID=[id]
        track_id = self.extract_track_id('/'.join(url_parts[1:])) if video_name else None

        video_path = self.get_video_path(video_name) if video_name else None

        print(f"Video name is {video_name}, Video Path is {video_path}, Track ID is {track_id}, and path is {video_path}. Received CSeq: {cseq}")

        if method == "OPTIONS":
            response = f"RTSP/1.0 200 OK\r\nServer: VLC/3.0.9.2\r\nContent-Length: 0\r\nCSeq: {cseq}\r\nPublic: DESCRIBE,SETUP,TEARDOWN,PLAY,PAUSE,GET_PARAMETER\r\n\r\n"
            connection.send(response.encode())

        elif method == "DESCRIBE":
            logging.info("Processing DESCRIBE request.")
            video_name = url_parts[-1] # Fix
            sdp = self.create_sdp_description(address, video_name)
            current_date = formatdate(timeval=None, localtime=False, usegmt=True)
            response = f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\nDate: {current_date}\r\n"
            response += f"Content-Base: {self.host}:{self.port}/{video_name}/\r\n"
            response += f"Content-Type: application/sdp\r\n"
            response += f"Content-Length: {len(sdp)}\r\n\r\n{sdp}"
            connection.send(response.encode())


        elif method == "SETUP" and video_path:
            logging.info("Processing SETUP request.")

            # Extract the client's RTP and RTCP port numbers
            client_rtp_port, client_rtcp_port = self.extract_client_ports(request)
            
            if client_rtp_port and client_rtp_port:
                self.clients[address] = {
                    'streamer': VideoStreamer(address, video_path, client_rtp_port, client_rtcp_port),
                    'state': "INIT"
                }
                self.clients[address]['streamer'].setup_stream()

                # Inside process_request method under SETUP:
                server_rtp_port = randint(50000, 55000)
                server_rtcp_port = server_rtp_port + 1
                self.clients[address]['rtp_port'] = server_rtp_port
                self.clients[address]['rtcp_port'] = server_rtcp_port
                current_date = formatdate(timeval=None, localtime=False, usegmt=True)
                ssrc_value = format(random.getrandbits(32), '08x')
                response = f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\nDate: {current_date}\r\nSession: {self.clients[address]['streamer'].session_id}\r\n"
                response += f"Transport: RTP/AVP;unicast;client_port={client_rtp_port}-{client_rtcp_port};server_port={server_rtp_port}-{server_rtcp_port};ssrc={ssrc_value};mode=\"play\"\r\n\r\n"
                print(f'[<---] Sending the response: to connection {connection}\n {response}')
                connection.send(response.encode())

        elif method == "PLAY" and address in self.clients and self.clients[address]['state'] == "INIT":
            threading.Thread(target=self.clients[address]['streamer'].stream_video).start()
            self.clients[address]['state'] = "PLAYING"
            response = f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\nSession: {self.clients[address]['streamer'].session_id}\r\n\r\n"
            connection.send(response.encode())

        elif method == "PAUSE" and address in self.clients and self.clients[address]['state'] == "PLAYING":
            self.clients[address]['streamer'].pause_streaming()
            self.clients[address]['state'] = "PAUSED"
            response = f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\nSession: {self.clients[address]['streamer'].session_id}\r\n\r\n"
            connection.send(response.encode())

        elif method == "TEARDOWN" and address in self.clients:
            self.clients[address]['streamer'].stop_streaming()
            self.clients[address]['state'] = "STOPPED"
            response = f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\nSession: {self.clients[address]['streamer'].session_id}\r\n\r\n"
            connection.send(response.encode())

            connection.close()
            del self.clients[address]
    
    def extract_cseq(self, request_string):
        for line in request_string.split("\n"):
            if line.startswith("CSeq:"):
                return int(line.split(":")[1].strip())
        return None
    
    def extract_client_ports(self, request_string):
        for line in request_string.split("\n"):
            if line.startswith("Transport:"):
                parts = line.split(";")
                for part in parts:
                    if "client_port" in part:
                        return tuple(map(int, part.split("=")[1].split("-")))
        return None, None

    def get_video_path(self, video_name):
        # Here you'd implement the logic to get the correct video path
        video_paths = {
            "movie1": "videos/sample.mp4",
            "movie2": "videos/test.mp4",
            "movie3": "videos/test2.mp4",
        }
        return video_paths.get(video_name, "")

    def create_sdp_description(self, address, video_name):
        sdp = "v=0\r\n"
        sdp += "o=- 0 0 IN IP4 " + self.host + "\r\n"
        sdp += "s=RTSP Server\r\n"
        sdp += "c=IN IP4 " + address[0] + "\r\n"
        sdp += "t=0 0\r\n"
        sdp += "m=video 0 RTP/AVP 96\r\n"
        sdp += "a=rtpmap:96 H264/90000\r\n"
        sdp += "a=control:trackID=0\r\n"
        # Add more media descriptions as needed
        return sdp
    
    def extract_track_id(self, url_path):
        parts = url_path.split('/')
        for part in parts:
            if 'trackID=' in part:
                return part.split('=')[1]
        return None



# Main entry point of the RTSP server
if __name__ == "__main__":
    HOST, PORT = 'localhost', 8554
    rtsp_server = RTSPPServer(HOST, PORT)
    rtsp_server.run_server()
