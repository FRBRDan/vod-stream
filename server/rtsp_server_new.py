import gi
import threading
import os

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

class VideoStreamerRTSPServer:
    def __init__(self):
        Gst.init(None)

        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")  # Port number
        self.mounts = self.server.get_mount_points()

        self.setup_endpoints()

        self.server.attach(None)

    def setup_endpoints(self):
        videos_dir = "videos/"
        for video in os.listdir(videos_dir):
            if video.endswith((".mp4")):  # Add other formats as needed
                endpoint = "/" + os.path.splitext(video)[0]
                factory = GstRtspServer.RTSPMediaFactory()
                factory.set_launch(
                                f'( filesrc location="{os.path.join(videos_dir, video)}" ! '
                                'decodebin name=dec '
                                'dec. ! queue ! videoconvert ! x264enc ! rtph264pay name=pay0 pt=96 '
                                'dec. ! queue ! audioconvert ! audioresample ! avenc_aac ! rtpmp4apay name=pay1 pt=97 )'
                            )
                factory.set_shared(True)
                self.mounts.add_factory(endpoint, factory)
                print(f"Added endpoint {endpoint} for {video}")

def start_rtsp_server():
    rtsp_server = VideoStreamerRTSPServer()
    loop = GLib.MainLoop()
    loop.run()

if __name__ == "__main__":
    server_thread = threading.Thread(target=start_rtsp_server)
    server_thread.start()
