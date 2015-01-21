# -*- coding: utf-8 -*-

"""
This app will create a seamless VPN connection between you and your enterprise
by adding a tray icon and keeping you connected whenever possible.
"""

import os

__title__ = 'smart_agnc'
__version__ = '0.0.8'

module_dir = os.path.abspath(os.path.dirname(__file__))

if module_dir.startswith('/usr/'):  # we are in production
    root_path = '/usr'
else:
    root_path = os.path.abspath(os.path.join(module_dir, '..', '..'))
    os.environ["PATH"] += os.pathsep + os.path.join(root_path, 'bin')

config_dir = os.path.expanduser('~/.smart-agnc')
logs_dir = os.path.join(config_dir, 'logs')
config_file = os.path.join(config_dir, 'config')
share_dir = os.path.join(root_path, 'share')
