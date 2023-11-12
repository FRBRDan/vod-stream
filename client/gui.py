import sys
import vlc
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QListWidget, QLabel, QSlider, QStatusBar, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont

class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.initUI()

    def initUI(self):
        # Set main window properties
        self.setWindowTitle('VOD Client')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet("""
            QMainWindow { background-color: #2c3e50; }
            QPushButton { border: 2px solid #34495e; border-radius: 5px; padding: 5px; background-color: #34495e; color: #ecf0f1; }
            QPushButton:hover { background-color: #4e6a85; }
            QPushButton:pressed { background-color: #2c3e50; }
            QListWidget { border: none; color: #ecf0f1; background-color: #34495e; }
            QLabel { color: #ecf0f1; font-weight: bold; }
            QSlider::groove:horizontal { border: 1px solid #bbb; background: white; height: 10px; border-radius: 4px; }
            QSlider::sub-page:horizontal { background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5F97FF, stop:1 #5F97FF); border: 1px solid #777; height: 10px; border-radius: 4px; }
            QSlider::handle:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eee, stop:1 #ccc); border: 1px solid #777; width: 13px; margin-top: -2px; margin-bottom: -2px; border-radius: 4px; }
            QStatusBar { color: #ecf0f1; }
        """)

        # Create central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create and add a label for the video list
        self.video_list_label = QLabel('Available Videos')
        self.video_list_label.setFont(QFont('Arial', 14))
        self.layout.addWidget(self.video_list_label)

        # Create and add the video list widget
        self.video_list_widget = QListWidget(self.central_widget)
        self.video_list_widget.setFont(QFont('Arial', 12))
        self.layout.addWidget(self.video_list_widget)

        # Add some example items to the list
        self.video_list_widget.addItems(["Movie 1", "Movie 2", "Movie 3"])

        # Create control buttons layout
        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        # Create and add the play and stop buttons with icons
        self.play_button = QPushButton(QIcon('play_icon.png'), 'Play')
        self.stop_button = QPushButton(QIcon('stop_icon.png'), 'Stop')
        self.buttons_layout.addWidget(self.play_button)
        self.buttons_layout.addWidget(self.stop_button)

        # Create and add the pause button with an icon
        self.pause_button = QPushButton(QIcon('pause_icon.png'), 'Pause')
        self.buttons_layout.addWidget(self.pause_button)
        self.pause_button.clicked.connect(self.pause_video)
        
        # Create and add a slider for video seeking
        self.seek_slider = QSlider(Qt.Horizontal)
        self.layout.addWidget(self.seek_slider)

        # Create and add a status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Connect buttons to their functions
        self.play_button.clicked.connect(self.play_video)
        self.stop_button.clicked.connect(self.stop_video)

        # Create video output widget
        self.video_frame = QFrame()
        self.video_frame.setMinimumSize(800, 450)
        self.video_frame.setStyleSheet("QFrame { background-color: black; }")
        self.layout.addWidget(self.video_frame)

        # Set the video output widget in the player
        self.set_video_output()

        # Show the GUI
        self.show()

    # Add the new pause_video method
    def pause_video(self):
        self.media_player.pause()  # This method toggles pause/unpause on the media player.


    def set_video_output(self):
        if sys.platform.startswith('linux'):  # for Linux using the X Server
            self.media_player.set_xwindow(self.video_frame.winId())
        elif sys.platform == "win32":  # for Windows
            self.media_player.set_hwnd(self.video_frame.winId())
        elif sys.platform == "darwin":  # for MacOS
            try:
                self.media_player.set_nsobject(int(self.video_frame.winId()))
            except Exception as e:
                self.status_bar.showMessage(f"Failed to set video output: {e}")

    def play_video(self):
        video_url = self.get_video_url(self.video_list_widget.currentItem().text())
        if video_url:
            Media = self.vlc_instance.media_new(video_url)
            self.media_player.set_media(Media)
            self.media_player.play()

    def stop_video(self):
        self.media_player.stop()

    def get_video_url(self, video_name):
        video_urls = {
            "movie1": "/path/to/movie1.mp4",
            "movie2": "/path/to/movie2.mp4",
            "movie3": "/path/to/movie3.mp4",
        }
        return video_urls.get(video_name)

def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
