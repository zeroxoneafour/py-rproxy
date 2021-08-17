from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import gofetch
import os
import mimetypes

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
            req = gofetch.path_to_req(self.path[len(gateway)+1:])
            data = gofetch.fetch_website(req, gateway)
            mimetype = gofetch.get_mimetype(req.url)
            self.send_response(200)
            self.send_header("Content-Type", mimetype)
            self.end_headers()
            self.wfile.write(data)
        else:
            webroot_path = os.path.dirname(__file__) + '/' + webroot
            if (os.path.isdir(webroot_path + self.path)):
                file = open(webroot_path + self.path + "/index.html")
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(self.path))
                self.end_headers()
                file_data = file.read()
                file.close()
                file_data = file_data.encode("utf-8")
                self.wfile.write(file_data)
            elif (os.path.isfile(webroot_path + self.path)):
                file = open(webroot_path + self.path)
                self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(self.path))
                self.end_headers()
                file_data = file.read()
                file.close()
                file_data = file_data.encode("utf-8")
                self.wfile.write(file_data)
            else:
                self.send_response(404)
                self.send_header("Content-Type", 'index/html')
                self.end_headers()

    def do_POST(self):
        if (gateway in self.path):
            content_length = int(self.headers["Content-length"])
            post = self.rfile.read(content_length)
            req = gofetch.path_to_req_post(self.path[len(gateway)+1:], post)
            data = gofetch.fetch_website(req, gateway)
            mimetype = gofetch.get_mimetype(req.url)
            self.send_response(200)
            self.send_header("Content-Type", mimetype)
            self.end_headers()
            self.wfile.write(data)

server = ThreadingHTTPServer((hostname, int(port)), MyProxy)
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
