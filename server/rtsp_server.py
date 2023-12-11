import gi
import threading
import os
from request_handler import *

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

STREAMING_PORT_STR = "8554"

class VideoStreamerRTSPServer:
    def __init__(self):
        try:
            Gst.init(None)

            self.server = GstRtspServer.RTSPServer()
            self.server.set_service(STREAMING_PORT_STR)
            self.mounts = self.server.get_mount_points()

            self.setup_endpoints()

            self.server.attach(None)
        
        except Exception as e:
            print(f"Error initializing RTSP server: {e}")
            raise

    def setup_endpoints(self):
        try:
            videos_dir = "videos/"
            for video in os.listdir(videos_dir):
                if video.endswith((".mp4")):  # Add other formats as needed
                    endpoint = "/" + os.path.splitext(video)[0]
                    factory = GstRtspServer.RTSPMediaFactory()
                    factory.set_launch(
                            f'( filesrc location="{os.path.join(videos_dir, video)}" ! '
                            'decodebin name=dec '
                            'dec. ! queue ! videoconvert ! x264enc tune=zerolatency ! rtph264pay name=pay0 pt=96 '
                            'dec. ! queue ! audioconvert ! audioresample ! opusenc ! rtpopuspay name=pay1 pt=97 )'
                        )

                    factory.set_shared(False) # Create a separate instance for each client
                    self.mounts.add_factory(endpoint, factory)
                    print(f"Added endpoint {endpoint} for {video}")
        except Exception as e:
            print(f"Error setting up endpoints: {e}")

def start_rtsp_server():
    try:
        rtsp_server = VideoStreamerRTSPServer()
        loop = GLib.MainLoop()
        loop.run()
    except Exception as e:
        print(f"Error starting RTSP server: {e}")

if __name__ == "__main__":
    # Start HTTP server
    http_server_thread = threading.Thread(target=start_http_server)
    http_server_thread.start()

    # Start RTSP server
    server_thread = threading.Thread(target=start_rtsp_server)
    server_thread.start()
