# server/video_streamer.py
import socket
import os
import io
import time  # Import the time module


class VideoStreamer:
    def __init__(self, client_info, video_path):
        self.client_info = client_info  # Tuple (IP, port)
        self.video_path = video_path
        self.rtp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def stream_video(self):
        """ Stream the video file to the client using RTP packets. """
        if not os.path.isfile(self.video_path):
            print(f"Video file {self.video_path} not found.")
            return

        print(f"Streaming {self.video_path} to {self.client_info}")

        with open(self.video_path, 'rb') as video_file:
            while True:
                # Read a chunk of the video file
                data = video_file.read(20480)  # You might want to choose a different chunk size
                if not data:
                    break  # End of file

                # Here you would normally need to wrap the data in an RTP packet.
                # This is just sending raw video data, which is not a proper RTP stream.

                self.rtp_socket.sendto(data, self.client_info)

                # Simulate the frame rate
                time.sleep(1/30)  # For 30 fps, wait 1/30 of a second

        self.rtp_socket.close()
