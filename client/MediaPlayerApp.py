import sys
import vlc
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QListWidget, QLabel, QSlider, QStatusBar, QHBoxLayout, QFrame
)
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

import requests
from constants import *

class MediaPlayerApp(QMainWindow):
    def __init__(self):
        """
        Initialize the main window and VLC media player instance.
        Set default volume and initialize the user interface.
        """
        super().__init__()
        self.vlc_instance = vlc.Instance()
        self.media_player = self.vlc_instance.media_player_new()
        self.media_player.audio_set_volume(DEFAULT_VOLUME)
        self.initUI()

    def initUI(self):
        """
        Initialize the user interface, set window properties, and create layout.
        """
        # Set main window properties
        self.setWindowTitle('VOD Client')
        self.setGeometry(100, 100, 1000, 600)
        self.setStyleSheet(GUI_STYLES)

        # Create central widget and layout
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create and add a label for the video list
        self.video_list_label = QLabel('Available Videos')
        self.video_list_label.setFont(QFont(DEFAULT_FONT_TYPE, TITLE_FONT_SIZE))
        self.layout.addWidget(self.video_list_label)

        # Create and add the video list widget
        self.video_list_widget = QListWidget(self.central_widget)
        self.video_list_widget.setFont(QFont(DEFAULT_FONT_TYPE, LIST_FONT_SIZE))
        self.layout.addWidget(self.video_list_widget)

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

        # Playback Time Label
        self.playback_label = QLabel('00:00 / 00:00')
        self.playback_label.setFont(QFont(DEFAULT_FONT_TYPE, DATA_FONT_SIZE))
        self.layout.addWidget(self.playback_label)
        
        # Create and add a slider for video seeking
        self.seek_slider = QSlider(Qt.Horizontal)
        self.layout.addWidget(self.seek_slider)

        # Modify seek_slider
        self.seek_slider.setRange(0, 1000)  # Example range
        self.seek_slider.sliderMoved.connect(self.set_position)

        # Volume Label
        self.volume_label = QLabel('Volume 100%')
        self.volume_label.setFont(QFont(DEFAULT_FONT_TYPE, DATA_FONT_SIZE))
        self.layout.addWidget(self.volume_label)

        # Create and add a slider for volume control
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(MIN_VOLUME, MAX_VOLUME)

        self.volume_slider.setValue(DEFAULT_VOLUME)
        initial_volume = self.media_player.audio_get_volume()
        self.volume_slider.setValue(initial_volume)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.layout.addWidget(self.volume_slider)

        # Timer to update seek_slider position
        self.timer = QTimer(self)
        self.timer.setInterval(UI_UPDATE_INTERVAL_MS)
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
        """
        Handle the event when the user selects a different video from the list.
        Reset play button text to 'Play' and stop the current video.
        """
        self.play_button.setText('Play')
        self.media_player.stop()

    def pause_video(self):
        """
        Toggle pause/unpause on the media player.
        """
        self.media_player.pause()


    def set_video_output(self):
        """
        Set the video output based on the operating system.
        """
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
        """
        Play or pause the video based on the current state of the media player.
        If the video is paused, resume playing; otherwise, fetch and play a new video.
        """
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_button.setText('Play')
        else:
            if self.media_player.get_media() and self.media_player.get_state() == vlc.State.Paused:
                self.media_player.play()
                self.play_button.setText('Pause')
            else:
                try:
                    # Fetch the URL of the selected video
                    video_name = self.video_list_widget.currentItem().text()
                    video_url = self.get_video_url(video_name)
                    if video_url:
                        # Create a new media instance with the URL only if it's different from the current one
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
        """
        Stop the currently playing video.
        """
        try:
            self.media_player.stop()
            self.play_button.setText('Play')
        except Exception as e:
            print(f"Error in stop_video: {e}")

    def closeEvent(self, event):
        """
        Override the close event to handle proper teardown.
        """
        self.rtsp_client.teardown()
        super().closeEvent(event)

    def get_video_url(self, video_name):
        """
        Construct the RTSP URL for the selected video.
        """
        return f"rtsp://localhost:8554/{video_name}"

    def set_volume(self, value):
        """
        Set the audio volume of the media player.
        Update the volume label in the user interface.
        """
        self.media_player.audio_set_volume(value)
        self.volume_label.setText(f'Volume {value}%')

    def set_position(self, value):
        """
        Set the media position based on the user's slider input.
        """
        self.media_player.set_position(value / 1000.0)
  
    def update_ui(self):
        """
        Update the user interface components, including the seek slider and playback time label.
        """        
        if self.media_player.is_playing() or self.media_player.get_state() == vlc.State.Paused:
            # Update the seek slider to the current media player time
            media_pos = int(self.media_player.get_position() * PERCENTAGE_TO_MILLISECONDS)
            self.seek_slider.setValue(media_pos)

            # Update playback time label
            current_time = self.media_player.get_time() // MILLISECONDS_TO_SECONDS
            total_time = self.media_player.get_length() // MILLISECONDS_TO_SECONDS
            current_time_str = f'{current_time // 60:02d}:{current_time % 60:02d}'
            total_time_str = f'{total_time // 60:02d}:{total_time % 60:02d}'
            self.playback_label.setText(f'{current_time_str} / {total_time_str}')
        else: # STOPPED
            self.seek_slider.setValue(0)
            self.playback_label.setText('00:00 / 00:00')

    def fetch_movie_list(self):
        """
        Fetch the list of available movies from the server and populate the video list widget.
        """
        try:
            response = requests.get('http://localhost:8000/movies')
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx and 5xx)
            
            if response.status_code == HTTP_STATUS_OK:
                movies = response.json()
                formatted_movies = [os.path.splitext(movie)[0] for movie in movies]
                self.video_list_widget.clear()
                self.video_list_widget.addItems(formatted_movies)
                # self.show_info_message("Movie List Fetched", 
                #                        f"Successfully fetched {len(formatted_movies)} movies.")
            else:
                self.show_error_message("Failed to fetch movie list", 
                                        f"Server responded with status code: {response.status_code}")
                sys.exit(0)
        except requests.exceptions.RequestException as e:
            # HTTP-related errors
            self.show_error_message("HTTP Error", f"Error fetching movie list: {e}")
            sys.exit(0)
        except Exception as e:
            self.show_error_message("Error", f"An unexpected error occurred: {e}")
            sys.exit(0)
    
    def show_error_message(self, title, message):
        """
        Display an error message dialog with the specified title and message.
        """
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        error_dialog.setStyleSheet("QLabel { color: black; } "
                                   "QMessageBox { background-color: #f8d7da; }")
        ok_button = error_dialog.addButton(QMessageBox.Ok)
        ok_button.clicked.connect(QCoreApplication.quit)
        error_dialog.exec_()
    
    def show_info_message(self, title, message):
        """
        Display an information message dialog box.
        """
        info_dialog = QMessageBox(self)
        info_dialog.setIcon(QMessageBox.Information)
        info_dialog.setWindowTitle(title)
        info_dialog.setText(message)

        # Set the text color to black
        text_color = QColor(0, 0, 0)
        info_dialog.setTextColor(text_color)

        info_dialog.setStandardButtons(QMessageBox.Ok)
        info_dialog.exec_()
def main():
    """
    Entry point of the application. Create the QApplication and start the main loop.
    """
    app = QApplication(sys.argv)
    ex = MediaPlayerApp()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
