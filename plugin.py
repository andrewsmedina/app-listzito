#!/usr/bin/env python

import os
import json
import sys
import urllib2


def get_env(name):
    env = os.environ.get(name)
    if not env:
        sys.stderr.write("ERROR: missing {}\n".format(name))
        sys.exit(5)
    return env


class Request(urllib2.Request):

    def __init__(self, method, *args, **kwargs):
        self._method = method
        urllib2.Request.__init__(self, *args, **kwargs)

    def get_method(self):
        return self._method


def proxy_request(instance_name, method, path, body=None, headers=None):
    target = get_env("TSURU_TARGET").rstrip("/")
    token = get_env("TSURU_TOKEN")

    if not target.startswith("http://") and not target.startswith("https://"):
        target = "http://{}".format(target)

    url = "{}{}".format(target, instance_name, path)

    if body:
        body = json.dumps(body)

    request = Request(method, url, data=body)
    request.add_header("Authorization", "bearer " + token)

    if headers:
        for header, value in headers.items():
            request.add_header(header, value)

    return urllib2.urlopen(request, timeout=30)


def app_list(name):
    url = "/apps"
    headers = {"Content-Type": "application/json"}
    response = proxy_request(name, "GET", url, "", headers)
    urls = response.read()
    sys.stdout.write(urls + "\n")


def main(*args):
    app_list(*args)


if __name__ == "__main__":
    main(sys.argv[1:])
