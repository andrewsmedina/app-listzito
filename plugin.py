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


def request(method, path, body=None, headers=None):
    target = get_env("TSURU_TARGET").rstrip("/")
    token = get_env("TSURU_TOKEN")

    if not target.startswith("http://") and not target.startswith("https://"):
        target = "http://{}".format(target)

    url = "{}{}".format(target, path)

    if body:
        body = json.dumps(body)

    request = Request(method, url, data=body)
    request.add_header("Authorization", "bearer " + token)

    if headers:
        for header, value in headers.items():
            request.add_header(header, value)

    return urllib2.urlopen(request, timeout=30)


def extract_filters(args):
    filters = {}

    for f in args:
        key, value = f.split("=")
        filters[key] = value

    return filters


def match_all(app, filters):
    matchers = len(filters)
    ok = 0
    for key, value in filters.items():
        if app[key] == value:
            ok += 1
    return ok == matchers


def app_list(args):
    filters = extract_filters(args)

    url = "/apps"
    headers = {"Content-Type": "application/json"}
    response = request("GET", url, "", headers)
    data = response.read()
    apps = json.loads(data)

    for app in apps:
        if not match_all(app, filters):
            continue

        sys.stdout.write("{} - {}\n".format(app["name"], app["ip"]))


def main(*args):
    app_list(*args)


if __name__ == "__main__":
    main(sys.argv[1:])
