# -*- coding: utf-8 -*-

"""
This app will create a seamless VPN connection between you and your enterprise
by adding a tray icon and keeping you connected whenever possible.
"""

import gtk
import logging
import os
import pynotify

__version__ = '0.1.2'
__author__ = 'Ariel Barabas'

module_dir = os.path.abspath(os.path.dirname(__file__))

if module_dir.startswith('/usr/'):  # we are in production
    root_path = '/usr'
else:
    root_path = os.path.abspath(os.path.join(module_dir, '..', '..'))
    os.environ["PATH"] = os.path.join(root_path, 'bin') + os.pathsep + \
        os.environ["PATH"]

config_dir = os.path.expanduser('~/.smart-agnc')
logs_dir = os.path.join(config_dir, 'logs')
config_file = os.path.join(config_dir, 'config')
share_dir = os.path.join(root_path, 'share')

icons_dir = os.path.join(share_dir, 'icons')
gtk.icon_theme_get_default().append_search_path(icons_dir)

logger = logging.getLogger(__name__)


def alert(msg):
    notice = pynotify.Notification('Smart AT&T Client', msg)
    notice.show()
    logger.warning('Alert: %s', msg.replace('\n', '\n > '))
