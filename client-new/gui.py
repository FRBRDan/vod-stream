import sys
import vlc
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QListWidget

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.initUI()

    def initUI(self):
        # Set main window properties
        self.setWindowTitle('VOD Client')
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        # Create central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create and add the video list widget
        self.video_list_widget = QListWidget(self.central_widget)
        self.layout.addWidget(self.video_list_widget)

        # Add some example items to the list
        self.video_list_widget.addItems(["Movie 1", "Movie 2", "Movie 3"])

        # Create and add the play and stop buttons
        self.play_button = QPushButton('Play', self.central_widget)
        self.stop_button = QPushButton('Stop', self.central_widget)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.stop_button)

        # Connect buttons to their functions
        self.play_button.clicked.connect(self.play_video)
        self.stop_button.clicked.connect(self.stop_video)

        # Create video output widget
        self.video_frame = QWidget(self.central_widget)
        self.video_frame.setMinimumSize(640, 480)
        self.layout.addWidget(self.video_frame)

        # Set the video output widget in the player
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            # macOS specific setup
            try:
                self.media_player.set_nsobject(int(self.video_frame.winId()))
            except Exception as e:
                print(f"Failed to set nsobject: {e}")

        # Show the GUI
        self.show()

    def play_video(self):
        video_url = self.get_video_url(self.video_list_widget.currentItem().text())
        if video_url:
            Media = self.vlc_instance.media_new(video_url)
            self.media_player.set_media(Media)
            self.media_player.play()

    def stop_video(self):
        self.media_player.stop()

    def get_video_url(self, video_name):
        # Mapping of video names to file paths
        video_urls = {
            "Movie 1": "/path/to/your/video/sample.mp4",
            "Movie 2": "/path/to/your/video/test.mp4",
            "Movie 3": "/path/to/your/video/test2.mp4",
        }
        return video_urls.get(video_name)

def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
