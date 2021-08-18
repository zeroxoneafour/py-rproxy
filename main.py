from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import gofetch
import os
import mimetypes

# version
version="0.0.1"

# default values
port = 8080
hostname = "localhost"
gateway = "gateway"
webroot = "server"

# read config
config = open("config.txt", "r")

for line in config.readlines():
    line = line.replace("\n", "")
    # config comments with #
    if (line[0] != '#'):
        # read manually
        if ("port" in line):
            port = line[line.index('=')+1:]
        elif ("hostname" in line):
            hostname = line[line.index('=')+1:]
        elif ("gateway" in line):
            gateway = line[line.index('=')+1:]
        elif ("webroot" in line):
            webroot = line[line.index('=')+1:]

class MyProxy(BaseHTTPRequestHandler):
    # get request
    def do_GET(self):
        # check if trying to access gateway
        if (gateway in self.path):
            req = gofetch.path_to_req(self.path[len(gateway)+1:]) # path excluding /<gateway>/
            data = gofetch.fetch_website(req, gateway)
            mimetype = gofetch.get_mimetype(req.url)
            self.send_response(200)
            self.send_header("Content-Type", mimetype)
            self.end_headers()
            self.wfile.write(data)
        else: # normal web server with root __file__/webroot
            webroot_path = os.path.dirname(__file__) + '/' + webroot
            if (os.path.isdir(webroot_path + self.path)): # load directory
                file = open(webroot_path + self.path + "/index.html")
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(self.path))
                self.end_headers()
                file_data = file.read()
                file.close()
                file_data = file_data.encode("utf-8")
                self.wfile.write(file_data)
            elif (os.path.isfile(webroot_path + self.path)): # load file
                file = open(webroot_path + self.path)
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(self.path))
                self.end_headers()
                file_data = file.read()
                file.close()
                file_data = file_data.encode("utf-8")
                self.wfile.write(file_data)
            else: # 404 handler
                self.send_response(404)
                self.send_header("Content-Type", 'index/html')
                self.end_headers()

    # post request
    def do_POST(self):
        if (gateway in self.path):
            content_length = int(self.headers["Content-Length"])
            post = self.rfile.read(content_length) # read post
            req = gofetch.path_to_req_post(self.path[len(gateway)+1:], post) # exclude gateway from path
            data = gofetch.fetch_post(req, gateway)
            mimetype = gofetch.get_mimetype(req.url)
            self.send_response(200)
            self.send_header("Content-Type", mimetype)
            self.end_headers()
            self.wfile.write(data)

server = ThreadingHTTPServer((hostname, int(port)), MyProxy)
print("py-rproxy v" + version)
print("Server started on http://%s:%s" % (hostname, port))
print("Gateway: %s" % (gateway))
print("Web root: %s" % (webroot))

# server until ^C
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass

server.server_close()
print("Server stopped")
