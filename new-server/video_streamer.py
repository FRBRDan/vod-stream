# server/video_streamer.py
import socket
import os
import time
from random import randint
import logging
import subprocess


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
        payload_type = 96  # H264 encoded
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
        logging.info(f'About to stream video {self.video_path} to {self.client_info}')
        if not os.path.isfile(self.video_path):
            logging.error(f"Video file {self.video_path} not found.")
            return

        # Dynamically set the RTP streaming address
        rtp_address = f'rtp://{self.client_info[0]}:{self.client_rtp_port}'

        command = [
            'ffmpeg', '-re', '-i', self.video_path,
            '-vcodec', 'libx264', '-an',
            '-f', 'rtp', rtp_address
        ]

        try:
            ffmpeg_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.streaming = True

            while self.streaming:
                output = ffmpeg_process.stdout.readline()
                if output:
                    logging.info(output.strip())

                error = ffmpeg_process.stderr.readline()
                if error:
                    logging.error(error.strip())

                if ffmpeg_process.poll() is not None:
                    logging.error("FFmpeg process ended unexpectedly.")
                    break

        except Exception as e:
            logging.error(f"Error streaming video: {e}")

        finally:
            self.streaming = False
            if ffmpeg_process:
                ffmpeg_process.terminate()
                ffmpeg_process.wait()
                logging.info("FFmpeg process terminated.")

    def pause_streaming(self):
        self.streaming = False

    def stop_streaming(self):
        self.streaming = False
        self.rtp_socket.close()
