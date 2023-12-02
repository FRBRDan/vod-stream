import http.server
import socketserver
import json
import os

PORT = 8000

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/movies':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            movies = os.listdir('videos/')  # Fetch the list of movies
            self.wfile.write(json.dumps(movies).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_http_server():
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print("serving at port", PORT)
        httpd.serve_forever()

