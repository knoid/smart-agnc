# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import json
import urllib2

from . import __version__

# short link to https://api.github.com/repos/knoid/smart-agnc/releases
gh_api = 'http://bit.ly/5pezDr'
current_version = StrictVersion(__version__)


def new_version_available():
    req = urllib2.Request(gh_api)

    # Github API requirements
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', __package__ + '_' + __version__)

    # Bitly requirement
    req.add_header('Referer', 'http://' + __package__ + '/' + __version__)

    content = urllib2.urlopen(req)
    for release in json.loads(content.read()):
        if StrictVersion(release['tag_name'][1:]) > current_version:
            return True
    return False
