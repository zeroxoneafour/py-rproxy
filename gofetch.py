import re
import mimetypes
import os
import urllib
from urllib.parse import urlparse
import requests
import concurrent.futures

# local path to url
def path_to_url(path):
    r = requests.get("https:/" + path)
    if (r.status_code == 200):
        return r.url
    else:
        r = requests.get("http:/" + path)
        return r.url

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
    page = re.sub("\"\/", "\"https://" + urlparse(url).netloc + "/", page)
    # no more multithreading :(
    page = re.sub("\"https?:\/", "\"/" + gateway, page)
    return page.encode("utf-8", "ignore")

# main fetch website script that downloads a website and resolved dependencies
def fetch_website(req, gateway):
    content = req.content
    mimetype = mimetypes.guess_type(req.url)[0]
    if (mimetype is None) or (mimetype.find("text") != -1):
        content = fix_page(content, req.url, gateway)
    return content

# idk, probably for post?
def read_post(path, data):
    url = get_url(path)
    post = requests.post(url, data)
    post = post.text
    post = fix_page(post, url)
    return post.encode("utf-8", "ignore")
