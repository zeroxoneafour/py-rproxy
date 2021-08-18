import re
import mimetypes
from urllib.parse import urlparse
import requests

# local path to url
def path_to_url(path):
    r = requests.get("https:/" + path)
    if (r.status_code == 200):
        return r.url
    else:
        r = requests.get("http:/" + path)
        return r.url

# local path to post request
def path_to_req_post(path, post):
    r = requests.post("https:/" + path, data=post)
    if (r.status_code == 200):
        return r
    else:
        r = requests.post("http:/" + path, data=post)
        return r

# local path to get request
def path_to_req(path):
    req = requests.get("https:/" + path)
    if (req.status_code == 200):
        return req
    else:
        req = requests.get("http:/" + path)
        return req

# get mimetype
def get_mimetype(url):
    mimetype = mimetypes.guess_type(url)[0]
    if (mimetype is None):
        return "text/html"
    else:
        return mimetype

# handle various things like url swapping and dependency downloading
def fix_page(page, url, gateway):
    page = page.decode("utf-8", "ignore")
    # still, somehow, doesn't really work
    page = re.sub("\"\/", "\"/" + gateway + "/" + urlparse(url).netloc + "/", page)
    # multithreading now in server
    page = re.sub("https?:\/", "/" + gateway, page)
    return page.encode("utf-8", "ignore")

# main fetch website script that downloads a website and returns content. Also might work with post
def fetch_website(req, gateway):
    content = req.content
    mimetype = get_mimetype(req.url)
    if (mimetype is None) or (mimetype.find("text/html") != -1) or (mimetype.find("application/javascript") != -1) or (mimetype.find("text/php") != -1):
        content = fix_page(content, req.url, gateway)
    return content

# fetch post - look similar?
def fetch_post(req, gateway):
    content = req.content
    mimetype = get_mimetype(req.url)
    if (mimetype is None) or (mimetype.find("text/html") != -1):
        content = fix_page(content, req.url, gateway)
    return content
