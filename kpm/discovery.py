import re
import requests
from HTMLParser import HTMLParser


package_regexp = "(.+?)/(.+)"


class MetaHTMLParser(HTMLParser):
    def __init__(self, variables):
        self.meta = {}
        self.variables = variables
        HTMLParser.__init__(self)

    def replace_values(self, s):
        for k, v in self.variables.iteritems():
            s = s.replace("{%s}" % k, v)
        return s

    def handle_starttag(self, tag, attrs):
        if tag == "meta":
            d = dict(attrs)
            if 'name' in d and d['name'] == 'kpm-package':
                name, source = d['content'].split(" ")
                name = self.replace_values(name)
                source = self.replace_values(source)
                if name not in self.meta:
                    self.meta[name] = []
                self.meta[name].append(source)


def ishosted(package):
    m = re.search(package_regexp, package)
    host = m.group(1)
    if "." in host:
        return True
    else:
        return False


def discover_sources(package, secure=False):
    m = re.search(package_regexp, package)
    host, name = (m.group(1), m.group(2))
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
        p = MetaHTMLParser({'name': name})
        p.feed(r.content)
        if package in p.meta:
            return p.meta[package]
    return None
