import tkinter as tk
import vlc


class VideoPlayerGUI:
    def __init__(self, client, video_list):
        self.client = client
        self.root = tk.Tk()
        self.root.title("VOD Client")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle window closing

        self.listbox = tk.Listbox(self.root)
        for video in video_list:
            self.listbox.insert(tk.END, video)
        self.listbox.pack(pady=20)

        self.status_label = tk.Label(self.root, text="Select a video to play")
        self.status_label.pack()

        self.play_button = tk.Button(self.root, text="Play", command=self.play_video)
        self.play_button.pack()

        # VLC player
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.media_player.set_fullscreen(False)

        # Create a Frame for VLC player
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack(padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.player_frame, bg="black", width=640, height=360)
        self.canvas.pack(padx=10, pady=10)
        
        self.media_player.set_hwnd(self.canvas.winfo_id())  # Attach VLC player to canvas

        # Event manager for media player
        self.event_manager = self.media_player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_end_of_media)

        self.root.mainloop()

    def play_video(self):
        self.status_label.config(text="Loading...")
        selected_video = self.listbox.get(tk.ACTIVE)
        rtsp_url = f"rtsp://localhost:5555/{selected_video}"    # Form the RTSP URL
        self.client.request_video(selected_video)               # Request the video
        media = self.vlc_instance.media_new(rtsp_url)           # Create media object
        self.media_player.set_media(media)                      # Set the media to VLC player
        self.media_player.play()                                # Play the video
        self.status_label.config(text="Now Playing: " + selected_video)

    def on_end_of_media(self, event):
        self.status_label.config(text="Video ended. Select another video to play.")

    def on_close(self):
        # Stop the player and release resources
        self.media_player.stop()
        self.vlc_instance.release()
        self.root.destroy()

