import tkinter as tk
import vlc


class VideoPlayerGUI:
    def __init__(self, client, video_list):
        self.client = client
        self.root = tk.Tk()
        self.root.title("VOD Client")

        self.listbox = tk.Listbox(self.root)
        for video in video_list:
            self.listbox.insert(tk.END, video)
        self.listbox.pack(pady=20)

        self.play_button = tk.Button(self.root, text="Play", command=self.play_video)
        self.play_button.pack()

        # VLC player
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()

        # Create a Frame for VLC player
        self.player_frame = tk.Frame(self.root)
        self.player_frame.pack(padx=10, pady=10)
        
        self.canvas = tk.Canvas(self.player_frame, bg="black", width=640, height=360)
        self.canvas.pack(padx=10, pady=10)
        
        self.media_player.set_hwnd(self.canvas.winfo_id())  # Attach VLC player to canvas

        self.root.mainloop()

    def play_video(self):
        print("Inside play_video")
        selected_video = self.listbox.get(tk.ACTIVE)
        rtsp_url = f"rtsp://localhost:5555/{selected_video}"    # Form the RTSP URL
        self.client.request_video(selected_video)               # Request the video
        media = self.vlc_instance.media_new(rtsp_url)           # Create media object
        self.media_player.set_media(media)                      # Set the media to VLC player
        self.media_player.play()                                # Play the video


