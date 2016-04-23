import re
import requests
from html.parser import HTMLParser


class MetaHTMLParser(HTMLParser):
    def __init__(self):
        self.meta = {}
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            d = dict(attrs)
            if 'name' in d and d['name'] == 'kpm-package':
                name, source = d['content'].split(" ")
                if name not in self.meta:
                    self.meta[name] = []
                self.meta[name].append(source)


def ishosted(package):
    m = re.search("(.+)/(.+)", package)
    host = m.group(1)
    if "." in host:
        return True
    else:
        return False


def discover_sources(package, secure=False):
    m = re.search("(.+)/(.+)", package)
    host = m.group(1)
    schemes = ["https://", "http://"]
    for scheme in schemes:
        url = scheme + host
        try:
            r = requests.get(url, params={"kpm-discovery": 1})
        except requests.ConnectionError as e:
            if scheme == "https://" and not secure:
                continue
            else:
                raise e

        r.raise_for_status()
        p = MetaHTMLParser()
        p.feed(r.content)
    if package in p.meta:
        return p.meta[package]
    else:
        return None
