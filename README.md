# Video Streaming Server and Client

## Overview

This project consists of a Video Streaming Server and a Client. The server is built to handle RTSP (Real-Time Streaming Protocol) requests for setting up, playing, pausing, and tearing down video streams. The client is designed to send RTSP requests to the server and display the streamed video content.

## Server

The server is a Python application that listens for RTSP requests over TCP and streams video content to clients using RTP (Real-Time Protocol). It can handle multiple clients simultaneously by spawning a new thread for each client connection.

## Client

The client is a Python application with a GUI for user interaction. It uses the VLC library to render video content streamed from the server. The GUI allows the user to play, pause, and stop video streams.

## Dependencies

To run the project, you need to have Python installed on your system. Additionally, you need to install the following Python libraries:

- `socket`
- `threading`
- `logging`
- `os`
- `vlc` (Python bindings for VLC)
- `PyQt5` (for GUI components)

Most of these libraries are included in the Python Standard Library. However, `vlc` and `PyQt5` can be installed using `pip3`.

## Installation

Before running the applications, install the required third-party libraries using `pip3`:

```
pip3 install python-vlc PyQt5
```

or

```
sudo apt-get install python3-pyqt5
```


*Make sure VLC Media Player is installed on your system as the vlc Python library requires it to function properly.*



## Don't forget - Mapping of video names to file paths inside client/gui.py and server/rtsp_server.py

```    
def get_video_url(self, video_name):
        # Mapping of video names to file paths
        video_urls = {
            "Movie 1": "/path/to/your/video/sample.mp4",
            "Movie 2": "/path/to/your/video/test.mp4",
            "Movie 3": "/path/to/your/video/test2.mp4",
        }
        return video_urls.get(video_name)
```

 ### Make sure to replace the placeholders in the video_urls dictionary with the correct paths to your video files 