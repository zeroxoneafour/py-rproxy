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

# url to local path
def url_to_path(url):
    return re.sub("https?:\/","",url)

# get mimetype
def get_mimetype(url, gatewaypath):
    if (os.path.isdir(gatewaypath + url_to_path(url))):
        return mimetypes.guess_type(gatewaypath + url_to_path(url))
    else:
        return mimetypes.guess_type(gatewaypath + url_to_path(url) + 'index.html')

# read website at url from the local cache
def read_website(url, gatewaypath):
    if (os.path.isdir(gatewaypath + url_to_path(url))):
        f = open(gatewaypath + url_to_path(url) + "index.html", "rb")
    else:
        f = open(gatewaypath + url_to_path(url), "rb")
    mimetype = mimetypes.guess_type(f.name)
    data = f.read()
    return data

# download a website without downloading website dependencies
def download_website(url, gateway, gatewaypath):
    if not (os.path.isdir(gatewaypath + url_to_path(url)) or os.path.isfile(gatewaypath + url_to_path(url))) or (".html" in url) or (url[-1] == '/'):
        r = requests.get(url)
        if (r.url[-1] == '/'):
            mimetype = 'text/html'
            os.makedirs(os.path.dirname(gatewaypath + url_to_path(r.url) + "index.html"), exist_ok=True)
            filepath = gatewaypath + url_to_path(r.url) + 'index.html'
        else:
            mimetype = mimetypes.guess_type(url)
            os.makedirs(os.path.dirname(gatewaypath + url_to_path(r.url)), exist_ok=True)
            filepath = gatewaypath + url_to_path(r.url)
        if not (os.path.isfile(filepath)):
            f = open(filepath, 'x')
            f.close()
        print(filepath)
        f = open(filepath, "wb")
        content = r.content
        f.write(content)
        f.close
    return

# handle various things like url swapping and dependency downloading
def fix_page(page, url, gateway, gatewaypath):
    page = page.decode("utf-8", "ignore")
    page = re.sub("\"\/", "\"https://" + urlparse(url).netloc + "/", page)
    # multithreading? idk
    with concurrent.futures.ThreadPoolExecutor() as executor:
        response_process = []
        for url in re.findall("\"https?:\/\/[^\"]*", page):
            response_process.append(executor.submit(download_website, re.sub("\"",'', url), gateway, gatewaypath))
    page = re.sub("\"https?:\/", "\"/" + gateway, page)
    return page.encode("utf-8", "ignore")

# main fetch website script that downloads a website and resolved dependencies
def fetch_website(url, gateway, gatewaypath):
    r = requests.get(url)
    if (r.url[-1] == '/'):
        mimetype = 'text/html'
        os.makedirs(os.path.dirname(gatewaypath + url_to_path(r.url) + "index.html"), exist_ok=True)
        filepath = gatewaypath + url_to_path(r.url) + 'index.html'
    else:
        mimetype = mimetypes.guess_type(url)
        os.makedirs(os.path.dirname(gatewaypath + url_to_path(r.url)), exist_ok=True)
        filepath = gatewaypath + url_to_path(r.url)
    if not (os.path.isfile(filepath)):
        f = open(filepath, 'x')
        f.close()
    print(filepath)
    f = open(filepath, "wb")
    content = r.content
    if ('text' in mimetype):
        content = fix_page(content, r.url, gateway, gatewaypath)
    f.write(content)
    f.close
    return

# idk, probably for post?
def read_post(path, data):
    url = get_url(path)
    post = requests.post(url, data)
    post = post.text
    post = fix_page(post, url)
    return post.encode("utf-8", "ignore")
