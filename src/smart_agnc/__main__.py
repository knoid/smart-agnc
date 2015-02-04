# -*- coding: utf-8 -*-

import gettext
import gtk
import logging
from logging.handlers import RotatingFileHandler
from optparse import OptionParser
import os
import sys

from . import config_dir, config_file, logs_dir, share_dir
from agn_binder import AgnBinder
from agn_notifier import AgnNotifier
from config import UserPreferences

# move config file to .smart-agnc folder (remove in July)
if os.path.isfile(config_dir):
    os.rename(config_dir, config_dir + '_backup')
    os.mkdir(config_dir)
    os.rename(config_dir + '_backup', config_file)
elif not os.path.isdir(config_dir):
    os.mkdir(config_dir)
if not os.path.isdir(logs_dir):
    os.mkdir(logs_dir)

i18n_dir = os.path.join(share_dir, 'locale')
gettext.install(__package__, i18n_dir)

optp = OptionParser()
optp.add_option('--exit-button', dest='exit_button', action='store_true',
                help='Add an exit button to the icon\'s context menu')
optp.add_option('--no-check-update', dest='check_update', action='store_false',
                help='Disable checking for application updates.')
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)')
opts, args = optp.parse_args()

if opts.check_update is None:
    opts.check_update = True

log_level = logging.WARNING  # default
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG

# setting up two loggers
streamLog = logging.StreamHandler(sys.stdout)
streamLog.setLevel(log_level)

fileLog = RotatingFileHandler(os.path.join(logs_dir, 'log'), 'a', 1 << 20,
                              backupCount=5, encoding='utf-8')
fileLog.setLevel(logging.INFO)

formatter_keys = ('asctime', 'name', 'levelname', 'message')
formatter_string = '|'.join(['%%(%s)s' % key for key in formatter_keys])
formatter = logging.Formatter(formatter_string)
streamLog.setFormatter(formatter)
fileLog.setFormatter(formatter)

logger = logging.getLogger(__package__)
logger.setLevel(logging.DEBUG)
logger.addHandler(streamLog)
logger.addHandler(fileLog)
logger.info('new run')

AGN_BINDER = AgnBinder()
CONFIG = UserPreferences({'keepalive': True, 'timeout': 40}, AGN_BINDER)
AgnNotifier(CONFIG, AGN_BINDER, opts)

gtk.main()
