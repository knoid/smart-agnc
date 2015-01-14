# -*- coding: utf-8 -*-

import gettext
import gtk
import logging
from optparse import OptionParser
import os

from . import __title__, share_dir
from agn_binder import AgnBinder
from agn_notifier import AgnNotifier
from config import UserPreferences

i18n_dir = os.path.join(share_dir, 'locale')
gettext.install(__title__, i18n_dir)

optp = OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)')
opts, args = optp.parse_args()

log_level = logging.WARNING  # default
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG

logging.basicConfig(level=log_level)

CONFIG = UserPreferences({'keepalive': True, 'timeout': 40})
AGN_BINDER = AgnBinder()
AgnNotifier(CONFIG, AGN_BINDER)

gtk.main()
