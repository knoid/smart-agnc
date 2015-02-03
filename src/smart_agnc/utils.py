# -*- coding: utf-8 -*-

# system imports
import logging
import pynotify

# local imports
import agn_binder as ab
import menu

logger = logging.getLogger(__name__)


def alert(msg):
    notice = pynotify.Notification('Smart AT&T Client', msg)
    notice.show()
    logger.warning('Alert: %s', msg.replace('\n', '\n > '))


def restart_agnc_services():
    if ab.can_restart_agnc_services():
        menu.item_restart_service.set_label(_('Restarting AGNC services'))
        ab.restart_agnc_services()
    else:
        alert(_('AGNC Services should be restarted.'))
        menu.item_restart_service.show()
