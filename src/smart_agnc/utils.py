# -*- coding: utf-8 -*-

# system imports
import functools
import gobject
import logging
import pynotify
import threading

# local imports
import agn_binder as ab
import menu

logger = logging.getLogger(__name__)


def alert(msg):
    notice = pynotify.Notification('Smart AT&T Client', msg)
    notice.show()
    logger.warning('Alert: %s', msg.replace('\n', '\n > '))


def async(blocking=False):
    lock = threading.Lock()

    def outer(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            LockingThread(blocking, lock,
                          target=func, args=args, kwargs=kwargs).start()
        return wrapper
    return outer


class EventsManager(gobject.GObject):

    __gsignals__ = {
        'agn-action-requested': (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [
                gobject.TYPE_INT]),
        'agn-state-change': (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [
                gobject.TYPE_INT]),
        'configuration-error': (
            gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, [
                gobject.TYPE_INT])
    }

    def __init__(self):
        super(EventsManager, self).__init__()

    def emit(self, *args):
        gobject.idle_add(super(EventsManager, self).emit, *args)


class LockingThread(threading.Thread):

    def __init__(self, blocking, lock, **kwargs):
        super(LockingThread, self).__init__(**kwargs)
        self.blocking = blocking
        self.lock = lock

    def run(self):
        if self.lock.acquire(self.blocking):
            super(LockingThread, self).run()
            self.lock.release()


def restart_agnc_services():
    if ab.can_restart_agnc_services():
        menu.item_restart_service.set_label(_('Restarting AGNC services'))
        ab.restart_agnc_services()
    else:
        alert(_('AGNC Services should be restarted.'))
        menu.item_restart_service.show()
