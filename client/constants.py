# constants.py


# Platform-specific keys for setting video output
LINUX_XWINDOW = 'xwindow'
WIN32_HWND = 'hwnd'
DARWIN_NS_OBJECT = 'nsobject'

# Default volume settings
DEFAULT_VOLUME = 100
MIN_VOLUME = 0
MAX_VOLUME = 100

# Fonts
TITLE_FONT_SIZE = 14
LIST_FONT_SIZE = 12
DATA_FONT_SIZE = 10
DEFAULT_FONT_TYPE = 'Arial'

# Timer interval for updating UI components
UI_UPDATE_INTERVAL_MS = 100
MILLISECONDS_TO_SECONDS = 1000
PERCENTAGE_TO_MILLISECONDS = 1000

# Base RTSP URL
RTSP_BASE_URL = 'rtsp://localhost:8554/'

# GUI styles
GUI_STYLES = """
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
"""

HTTP_STATUS_OK = 200