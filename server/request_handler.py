import http.server
import socketserver
import json
import os

HTTP_PORT = 8000
HTTP_VIDEOS_PATH = '/movies'
LOCAL_VIDEOS_PATH = 'videos/'

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == HTTP_VIDEOS_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            movies = os.listdir(LOCAL_VIDEOS_PATH)  # Fetch the list of movies
            self.wfile.write(json.dumps(movies).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    with socketserver.TCPServer(("", HTTP_PORT), RequestHandler) as httpd:
        print("serving at port", HTTP_PORT)
        httpd.serve_forever()

