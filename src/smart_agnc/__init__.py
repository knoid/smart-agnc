# -*- coding: utf-8 -*-

"""
This app will create a seamless VPN connection between you and your enterprise
by adding a tray icon and keeping you connected whenever possible.
"""

import os

__title__ = 'smart_agnc'
__version__ = '0.0.6'
__dir__ = os.path.abspath(os.path.dirname(__file__))

if __dir__.startswith('/usr/'): # we are in production
    resource_dir = '/usr/share'
else:
    resource_dir = os.path.join(__dir__, '..', '..', 'resources')
