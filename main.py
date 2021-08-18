from http.server import BaseHTTPRequestHandler, HTTPServer
import gofetch
import mimetypes
import os
import shutil

# default values
port = 8080
hostname = "localhost"
gateway = "gateway"
webroot = "server"

# read config
config = open("config.txt", "r")

for line in config.readlines():
    line = line.replace("\n", "")
    if (line[0] != '#'):
        if ("port" in line):
            port = line[line.index('=')+1:]
        elif ("hostname" in line):
            hostname = line[line.index('=')+1:]
        elif ("gateway" in line):
            gateway = line[line.index('=')+1:]
        elif ("webroot" in line):
            webroot = line[line.index('=')+1:]

class MyProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        if (gateway in self.path):
            gatewaypath = os.path.dirname(__file__) + '/' + gateway
            url = gofetch.path_to_url(self.path[len(gateway)+1:])
            gofetch.fetch_website(url, gateway, gatewaypath)
            data = gofetch.read_website(url, gatewaypath)
            mimetype = gofetch.get_mimetype(url, gatewaypath)
            self.send_response(200)
            self.send_header("Content-type", mimetype)
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(200)
            self.send_header("Content-type", mimetypes.guess_type(self.path))
            self.end_headers()
            webroot_path = os.path.dirname(__file__) + '/' + webroot
            if (os.path.isdir(webroot_path + self.path)):
                file = open(webroot_path + self.path + "/index.html")
            else:
                file = open(webroot_path + self.path)
            file_data = file.read()
            file.close()
            file_data = file_data.encode("utf-8")
            self.wfile.write(file_data)

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        data = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-type", mimetypes.guess_type(self.path))
        self.end_headers()
        if ( gateway in self.path):
            self.wfile.write(read_post(self.path, data))

server = HTTPServer((hostname, int(port)), MyProxy)
print("py-rproxy - Gateway")
print("Server started on http://%s:%s" % (hostname, port))
print("Gateway: %s" % (gateway))
print("Web root: %s" % (webroot))

try:
    server.serve_forever()
except KeyboardInterrupt:
    pass

server.server_close()
print("Server stopped")
print("Clearing gateway")
shutil.rmtree(os.path.dirname(__file__) + '/' + gateway)
