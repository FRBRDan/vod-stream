import tkinter as tk


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

        self.root.mainloop()

    def play_video(self):
        selected_video = self.listbox.get(tk.ACTIVE)
        self.client.request_video(selected_video)


