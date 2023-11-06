# server/video_streamer.py
import socket
import os
import time
from random import randint
import logging

# Define constants for RTP packet size and header size
RTP_PACKET_MAX_SIZE = 20480
RTP_HEADER_SIZE = 12


class VideoStreamer:
    def __init__(self, client_info, video_path, client_rtp_port, client_rtcp_port):
        logging.info(f'Initializing VideoStreamer with {client_info} and {video_path}.')
        self.client_info = client_info  # Tuple (IP, port)
        self.video_path = video_path
        self.client_rtp_port = client_rtp_port
        self.client_rtcp_port = client_rtcp_port
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.streaming = False
        self.session_id = self.generate_session_id()
        self.sequence_num = 0
        self.timestamp = 0
        logging.info(f'Generated session ID {self.session_id}.')

    def generate_session_id(self):
        # Generate a random, unique session ID
        return randint(100000, 999999)

    def setup_stream(self):
        # Initialize variables before starting the stream
        logging.info(f'Initializing variables before the stream (setup_stream).')
        self.sequence_num = 0
        self.timestamp = 0

    def create_rtp_packet(self, payload):
        """Create an RTP packet with the specified payload."""
        version = 2
        padding = 0
        extension = 0
        csrc_count = 0
        marker = 0
        payload_type = 26  # MJPEG video
        sequence_num = self.sequence_num
        timestamp = self.timestamp
        ssrc = self.session_id

        rtp_header = (
            (version << 6 | padding << 5 | extension << 4 | csrc_count),
            (marker << 7 | payload_type),
            sequence_num,
            timestamp,
            ssrc,
        )

        rtp_header_bytes = bytearray()
        for value in rtp_header:
            rtp_header_bytes += value.to_bytes((value.bit_length() + 7) // 8, byteorder='big')

        rtp_header_bytes = rtp_header_bytes.ljust(RTP_HEADER_SIZE, b'\x00')
        return rtp_header_bytes + payload

    def stream_video(self):
        logging.info(f'About to stream video {self.video_path}..')
        if not os.path.isfile(self.video_path):
            print(f"Video file {self.video_path} not found.")
            return

        print(f"Streaming {self.video_path} to {self.client_info}")
        self.streaming = True

        with open(self.video_path, 'rb') as video_file:
            while self.streaming:
                data = video_file.read(RTP_PACKET_MAX_SIZE - RTP_HEADER_SIZE)
                if not data:
                    break

                self.sequence_num += 1
                self.timestamp += 3600  # Increment as needed for your framerate
                
                rtp_packet = self.create_rtp_packet(data)
                self.rtp_socket.sendto(rtp_packet, (self.client_info[0], self.client_rtp_port))
                time.sleep(1/30)  # Simulate 30 fps

        self.rtp_socket.close()

    def pause_streaming(self):
        self.streaming = False

    def stop_streaming(self):
        self.streaming = False
        self.rtp_socket.close()
