# -*- coding: utf-8 -*-

# system imports
from distutils.version import StrictVersion
import gobject
import json
import logging
import threading
import urllib2

# local imports
from . import __version__

logger = logging.getLogger(__name__)
current_version = StrictVersion(__version__)
# short link to https://api.github.com/repos/knoid/smart-agnc/releases
gh_api = 'http://bit.ly/5pezDr'
two_hours = 1000 * 60 * 60 * 2


def check_periodically(upgrade_available_callback):
    gobject.timeout_add(two_hours, check_updates, upgrade_available_callback)


def check_updates(callback):
    threading.Thread(target=check_new_version, args=(callback, )).start()
    return True


def check_new_version(callback):
    logger.info('Checking updates')
    req = urllib2.Request(gh_api)

    # Github API requirements
    req.add_header('Accept', 'application/vnd.github.v3+json')
    req.add_header('User-Agent', __package__ + '_' + __version__)

    # Bitly requirement
    req.add_header('Referer', 'http://' + __package__ + '/' + __version__)

    try:
        content = urllib2.urlopen(req)
    except urllib2.URLError:
        content = None

    if content:
        for release in json.loads(content.read()):
            if StrictVersion(release['tag_name'][1:]) > current_version:
                return callback()

    logger.info('No new updates')
