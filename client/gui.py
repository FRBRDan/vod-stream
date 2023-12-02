import sys
import vlc
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QListWidget, QLabel, QSlider, QStatusBar, QHBoxLayout, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QTimer
import requests


class GUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        # Set the initial volume of the media player to 100%
        self.media_player.audio_set_volume(100)
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
        # self.video_list_widget.addItems(["Movie 1", "Movie 2"])

        self.fetch_movie_list()

        # Connect the itemSelectionChanged signal to the new method
        self.video_list_widget.itemSelectionChanged.connect(self.on_video_selection_changed)


        # Create control buttons layout
        self.buttons_layout = QHBoxLayout()
        self.layout.addLayout(self.buttons_layout)

        # Create and add the play and stop buttons with icons
        self.play_button = QPushButton('Play')  # If icon file is not available
        self.stop_button = QPushButton('Stop')  # If icon file is not available
        # self.pause_button = QPushButton('Pause')  # If icon file is not available
        self.buttons_layout.addWidget(self.play_button)
        self.buttons_layout.addWidget(self.stop_button)

        # Create and add the pause button with an icon
        self.pause_button = QPushButton(QIcon('pause_icon.png'), 'Pause')
        # self.buttons_layout.addWidget(self.pause_button)
        # self.pause_button.clicked.connect(self.pause_video)

        # Playback Time Label
        self.playback_label = QLabel('00:00 / 00:00')
        self.playback_label.setFont(QFont('Arial', 10))
        self.layout.addWidget(self.playback_label)
        
        # Create and add a slider for video seeking
        self.seek_slider = QSlider(Qt.Horizontal)
        self.layout.addWidget(self.seek_slider)

        # Modify seek_slider
        self.seek_slider.setRange(0, 1000)  # Example range
        self.seek_slider.sliderMoved.connect(self.set_position)

        # Volume Label
        self.volume_label = QLabel('Volume 100%')
        self.volume_label.setFont(QFont('Arial', 10))
        self.layout.addWidget(self.volume_label)

        # Create and add a slider for volume control
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)  # VLC volume range is from 0 to 100
        # Set the initial value of the volume slider to 100
        self.volume_slider.setValue(100)
        initial_volume = self.media_player.audio_get_volume()
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.layout.addWidget(self.volume_slider)

        # Timer to update seek_slider position
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Update every 100 ms
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

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

    def on_video_selection_changed(self):
        # Reset the play button text to 'Play'
        self.play_button.setText('Play')

        # Stop the current video and reset the media player
        self.media_player.stop()


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
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText('Play')
        else:
            # Check if the media player has media loaded and is in a paused state
            if self.media_player.get_media() and self.media_player.get_state() == vlc.State.Paused:
                self.media_player.play()
                self.play_button.setText('Pause')
            else:
                try:
                    # Fetch the URL of the selected video
                    video_name = self.video_list_widget.currentItem().text()
                    video_url = self.get_video_url(video_name)
                    if video_url:
                        # Create a new Media instance with the URL only if it's different from the current one
                        current_media = self.media_player.get_media()
                        if not current_media or current_media.get_mrl() != video_url:
                            Media = self.vlc_instance.media_new(video_url)
                            self.media_player.set_media(Media)
                        # Play the video
                        self.media_player.play()
                        self.play_button.setText('Pause')
                except Exception as e:
                    print(f"Error in play_video: {e}")



    def stop_video(self):
        try:
            self.media_player.stop()
        except Exception as e:
            print(f"Error in stop_video: {e}")

    def closeEvent(self, event):
        # Override the close event to handle proper teardown
        self.rtsp_client.teardown()
        super().closeEvent(event)

    def get_video_url(self, video_name):
        return f"rtsp://localhost:8554/{video_name}"

    def set_volume(self, value):
        self.media_player.audio_set_volume(value)
        self.volume_label.setText(f'Volume {value}%')

    # Set media position
    def set_position(self, value):
        # Setting the position to where the user moved the slider
        self.media_player.set_position(value / 1000.0)
  
    # Update UI components
    def update_ui(self):
        # Update the seek slider to the current media player time
        media_pos = int(self.media_player.get_position() * 1000)
        self.seek_slider.setValue(media_pos)

        # Update playback time label
        if self.media_player.is_playing():
            current_time = self.media_player.get_time() // 1000  # Current time in seconds
            total_time = self.media_player.get_length() // 1000  # Total time in seconds
        else:
            current_time = 0
            total_time = 0
        current_time_str = f'{current_time // 60:02d}:{current_time % 60:02d}'
        total_time_str = f'{total_time // 60:02d}:{total_time % 60:02d}'
        self.playback_label.setText(f'{current_time_str} / {total_time_str}')

    def fetch_movie_list(self):
        # Implement the logic to fetch the movie list from the server
        try:
            response = requests.get('http://localhost:8000/movies')
            if response.status_code == 200:
                movies = response.json()
                formatted_movies = [os.path.splitext(movie)[0] for movie in movies]
                print(formatted_movies)
                self.video_list_widget.clear()
                self.video_list_widget.addItems(formatted_movies)
        except Exception as e:
            print(f"Error fetching movie list: {e}")

def main():
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
