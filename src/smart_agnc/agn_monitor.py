# -*- coding: utf-8 -*-

# system imports
import gobject
import logging
import threading
import time

# local imports
import agn_binder as ab
import menu
import utils

SERVICES_RESTART_AFTER = 2
RECONNECT_INTERVAL = 10 * 1000
logger = logging.getLogger(__name__)
is_running = threading.RLock()


class AgnMonitor(object):

    connecting_timeout = 0
    fail_connect = 0
    want_to = ab.STATE_CONNECTED

    def __init__(self, binder, config, events):
        super(AgnMonitor, self).__init__()

        self.binder = binder
        self.config = config
        self.events = events
        self.check_connection()

    @utils.async()
    def check_connection(self, force=False):
        logger.info('check_connection')

        # to keep the subprocess alive
        state = self.binder.get_state()

        # if it is connecting and exceeds the timeout -> disconnect
        if ab.STATE_BEFORE_CONNECT < state < ab.STATE_VPN_RECONNECTED and \
                self.connecting_timeout < time.time():
            logger.info('Timeout! Disconnecting...')
            self.binder.action_disconnect()

            if self.fail_connect > SERVICES_RESTART_AFTER:
                self.fail_connect = 0
                utils.restart_agnc_services()
            else:
                self.fail_connect += 1

            return self.thread_end()

        if ab.STATE_BEFORE_CONNECT < state <= ab.STATE_CONNECTED:
            # I'm connected

            if ab.STATE_VPN_RECONNECTED <= state:
                menu.item_restart_service.hide()
                self.fail_connect = 0

            if self.want_to < state:  # I want to get disconnected
                self.binder.action_disconnect()

        else:
            # I'm disconnected

            if self.want_to > state:  # I want to get connected

                vpn, proxy = self.config.get_connection_values()
                use_proxy = self.config.getboolean('proxy', 'enabled')
                if len(vpn) == 3 and (not use_proxy or len(proxy) == 3):

                    if force or self.config.getboolean('vpn', 'keepalive'):
                        self.vpn_connect(vpn, proxy)
                    else:
                        utils.alert(_('VPN Disconnected'))
                        self.want_to = ab.STATE_NOT_CONNECTED

                else:
                    utils.alert(_('Complete credentials to connect'))
                    self.events.emit('configuration-error', state)
                    self.want_to = ab.STATE_NOT_CONNECTED

        return self.thread_end()

    @utils.async(False)
    def check_connection_nonblock(self):
        """
        The call will be made only if available and will be skiped if busy.
        """
        self.check_connection()

    def set_want_to(self, state):
        self.want_to = state
        connection_timeout = self.config.getint('vpn', 'timeout')
        self.connecting_timeout = time.time() + connection_timeout

    def thread_end(self):
        gobject.timeout_add(RECONNECT_INTERVAL, self.check_connection_nonblock)

    def vpn_connect(self, vpn, proxy=None, new_password=''):
        timeout_secs = self.config.getint('vpn', 'timeout')
        if not self.config.getboolean('proxy', 'enabled'):
            proxy = None
        self.connecting_timeout = time.time() + timeout_secs
        self.binder.action_connect(vpn['account'], vpn['username'],
                                   vpn['password'], new_password, proxy)
