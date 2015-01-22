# -*- coding: utf-8 -*-

import gettext
import gtk
import logging
from logging.handlers import TimedRotatingFileHandler
from optparse import OptionParser
import os
import sys

from . import __title__, config_dir, config_file, logs_dir, share_dir
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
gettext.install(__title__, i18n_dir)

optp = OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)')
optp.add_option('--exit-button', dest='exit_button', action='store_true',
                help='Add an exit button to the icon\'s context menu')
opts, args = optp.parse_args()

log_level = logging.WARNING  # default
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG

# setting up two loggers
streamLog = logging.StreamHandler(sys.stdout)
streamLog.setLevel(log_level)

fileLog = TimedRotatingFileHandler(os.path.join(logs_dir, 'log'),
                                   encoding='utf-8', when='D', backupCount=5)
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

CONFIG = UserPreferences({'keepalive': True, 'timeout': 40})
AGN_BINDER = AgnBinder()
AgnNotifier(CONFIG, AGN_BINDER, opts.exit_button)

gtk.main()
