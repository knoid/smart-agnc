import gettext
import gtk
import logging
from optparse import OptionParser
import os

from . import __title__, resource_dir
from config import UserPreferences
from agn_binder import AgnBinder
from main import AgnNotifier

i18n_dir = os.path.join(resource_dir, 'locale')
gettext.install(__title__, i18n_dir)

optp = OptionParser()
optp.add_option('-v', '--verbose', dest='verbose', action='count',
                help='Increase verbosity (specify multiple times for more)')
opts, args = optp.parse_args()

log_level = logging.WARNING # default
if opts.verbose == 1:
    log_level = logging.INFO
elif opts.verbose >= 2:
    log_level = logging.DEBUG

logging.basicConfig(level=log_level)

CONFIG = UserPreferences({'keepalive': True, 'timeout': 40})
AGN_BINDER = AgnBinder()
AgnNotifier(CONFIG, AGN_BINDER)

gtk.main()
