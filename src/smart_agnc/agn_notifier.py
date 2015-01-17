# -*- coding: utf-8 -*-

# system imports
import base64
import gobject
import logging
import os
import pynotify
import re
from subprocess import Popen, PIPE
import time

# local imports
from conn_info_win import ConnectionInformationWindow
import menu
from new_password_win import NewPasswordWindow
from settings_win import ConfigurationWindow
from tray_icon import TrayIcon
import agn_binder as ab

logger = logging.getLogger(__name__)


class AgnNotifier(TrayIcon):
    """AgnNotifier"""

    config_win = None
    title = 'Smart AT&T Client'
    _id = 'at&t-smart'

    reconnect_interval = 10
    """Time interval (in seconds) between VPN connection checks."""

    services_restart_after = 0
    """Amount of connection failures to wait after an AGNC Service Restart"""

    last_state = 0
    changing_password = False
    fail_connect = 0
    connecting_timeout = 0
    want_to = ab.STATE_CONNECTED

    def __init__(self, user_config, vpn, exit_button):
        super(AgnNotifier, self).__init__(self._id)
        pynotify.init(self._id)

        self.config = user_config

        self.new_password_win = NewPasswordWindow()
        self.new_password_win.connect('new-password', self.set_new_password)

        self.vpn = vpn
        vpn.connect('agn_state_change', self.on_vpn_state_change)
        vpn.connect('agn_state_change', self.trigger_external_script)

        self.config_win = ConfigurationWindow(vpn, self.get_config_values(),
                                              self.new_password_win)
        self.config_win.connect('save', self.do_save)

        self.on_vpn_state_change(None, vpn.get_state())

        self.conn_info_win = ConnectionInformationWindow()
        self.set_menu(menu.create(
            conn_toggle=self.do_toggle_connection,
            keepalive_init_state=self.config.getboolean('vpn', 'keepalive'),
            keepalive_toggle=self.do_toggle_keepalive,
            conn_info=self.do_conn_info,
            configure=self.do_configure,
            restart_agnc_services=self.do_restart_agnc_services,
            exit_button=exit_button))

        gobject.timeout_add(self.reconnect_interval * 1000, self.reconnect)

    def alert(self, msg):
        """alert"""
        notice = pynotify.Notification(self.title, msg)
        notice.show()
        logger.warning('Alert: %s', msg.replace('\n', '\n > '))

    def trigger_external_script(self, vpn, state):
        script_path = self.config.get('scripts', str(state))
        if len(script_path) > 0:
            output = [script_path]
            try:
                proc = Popen([os.path.expanduser(script_path)],
                             close_fds=True, stdout=PIPE, stderr=PIPE)
            except OSError as err:
                output.append(str(err))
                proc = False
            if proc:  # the external process was successfully initialized
                output += [s.rstrip() for s in proc.communicate() if s]
            if len(output) > 1:
                self.alert('\n'.join(output))

    def on_vpn_state_change(self, vpn, new_state):
        logger.info('on_vpn_state_change, new_state=%d', new_state)

        # ignoring higher states than STATE_CONNECTED we can be sure that 'the
        # higher the state, the more `connected` we are' remains True
        if new_state > ab.STATE_CONNECTED:
            return

        attempt = self.vpn.get_connect_attempt_info()
        menu.item_conn_status.set_label(attempt['StatusText'])

        toggle_btn_text = _('Connect')
        if self.want_to == ab.STATE_CONNECTED:
            toggle_btn_text = _('Disconnect')
        menu.item_conn_toggle.set_label(toggle_btn_text)

        ip_address = _('None')
        icon_state = 'disabled'
        if new_state > ab.STATE_VPN_CONNECTING:
            ip_address = ab.long2ip(attempt['VPNIPAddress'])
            icon_state = 'enabled'
            self.fail_connect = 0
        menu.item_conn_ip.set_label(_('IP: %s') % ip_address)
        self.set_icon(icon_state)

        # 12 = password expired
        # 16 = incorrect new password
        if attempt['StatusCode'] in [12, 16]:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('It is time to change your password!'))
            self.new_password_win.request_new_password()

        # 8 = Invalid credentials
        elif 8 == attempt['StatusCode']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Invalid credentials'))
            self.do_configure()

        # 502 = User-requested disconnect
        elif 0 < attempt['StatusCode'] and 502 != attempt['StatusCode']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Unknown error!') + '\n' + attempt['StatusText'])
            self.do_configure()

        self.last_state = new_state

    def reconnect(self, force=False):
        logger.info('Connection status check, force=%s', str(force))

        state = self.last_state
        if state == ab.STATE_UNKNOWN:
            state = self.last_state = self.vpn.get_state()

        # if it is connecting and exceeds the timeout -> disconnect
        if ab.STATE_BEFORE_CONNECT < state < ab.STATE_VPN_RECONNECTED and \
                self.connecting_timeout < time.time():
            logger.info('Timeout! Disconnecting...')
            self.vpn.action_disconnect()

            if self.fail_connect > self.services_restart_after:
                logger.info('AGNC Services should be restarted')

                if ab.can_restart_agnc_services():
                    ab.restart_agnc_services()
                    self.fail_connect = 0
                else:
                    menu.item_restart_service.show()
            else:
                self.fail_connect += 1

            return True

        if ab.STATE_BEFORE_CONNECT <= state <= ab.STATE_CONNECTED:
            # I'm connected

            menu.item_restart_service.hide()

            if self.changing_password:
                encoded_password = base64.b64encode(self.changing_password)
                self.config.set('vpn', 'password', encoded_password)
                self.config.write_to_disk()
                self.changing_password = False

            if self.want_to < state:  # I want to get disconnected

                self.vpn.action_disconnect()

        else:
            # I'm disconnected

            if self.want_to > state:  # I want to get connected

                cval = self.get_config_values()
                if len(cval) == 3:

                    if force or self.config.getboolean('vpn', 'keepalive'):
                        self.vpn_connect(cval)
                    else:
                        self.alert('VPN Disconnected')
                        self.want_to = ab.STATE_NOT_CONNECTED

                else:
                    self.alert('Complete credentials to connect')
                    self.do_configure()
                    self.want_to = ab.STATE_NOT_CONNECTED

        return True  # prevent the timeout from expiring

    def set_new_password(self, win, new_password):
        cval = self.get_config_values()
        self.changing_password = new_password
        self.vpn_connect(cval, new_password)
        self.want_to = ab.STATE_CONNECTED

    def vpn_connect(self, vpn, new_password=''):
        timeout_secs = self.config.getint('vpn', 'timeout')
        self.connecting_timeout = time.time() + timeout_secs
        self.vpn.action_connect(vpn['account'], vpn['username'],
                                vpn['password'], new_password)

    def do_configure(self, m_item=None):
        """do_configure"""
        self.config_win.present()

    def do_conn_info(self, m_item=None):
        """do_conn_info"""
        self.conn_info_win.set_text(_('Refreshing...'))
        self.conn_info_win.show_all()
        self.conn_info_win.present()

        attempt = self.vpn.get_connect_attempt_info()
        self.conn_info_win.set_dict(attempt)

    def do_restart_agnc_services(self, m_item=None):
        ab.restart_agnc_services()

    def do_save(self, config_win, account, username, password):
        """do_save"""
        config_win.hide()
        self.config.set('vpn', 'account', account)
        self.config.set('vpn', 'username', username)
        self.config.set('vpn', 'password', base64.b64encode(password))
        self.config.write_to_disk()
        self.want_to = ab.STATE_CONNECTED
        self.reconnect()

    def do_toggle_connection(self, m_item=None):
        """do_toggle_connection"""
        if self.want_to == ab.STATE_CONNECTED:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.vpn.action_disconnect()
            self.on_vpn_state_change(self.vpn, ab.STATE_NOT_CONNECTED)
        else:
            self.want_to = ab.STATE_CONNECTED
            self.reconnect(True)

    def do_toggle_keepalive(self, m_item):
        """do_toggle_keepalive"""
        self.config.setboolean('vpn', 'keepalive', m_item.get_active())
        self.config.write_to_disk()

    def get_config_values(self):
        """get_config_values"""
        keys = ['account', 'username', 'password']
        values = {}
        for key in keys:
            values[key] = self.config.get('vpn', key)

        if len(values['password']) > 0:
            try:
                decoded_password = base64.b64decode(values['password'])
            except TypeError:
                decoded_password = ''
            if len(decoded_password) > 0 and is_printable(decoded_password):
                # password was base64 encoded
                values['password'] = decoded_password
            else:
                logger.warning('Password was not encoded in config file.')

        if len(values) == 0:
            user = self.vpn.get_user_info()
            for key in keys:
                values[key] = user[key.title()]

        # do not return empty values
        return dict((key, val) for key, val in values.items() if len(val) > 0)

non_printables = ''.join([unichr(x) for x in (range(0, 32) + range(127, 160))])
non_printables_re = re.compile('[%s]' % re.escape(non_printables))


def is_printable(string):
    return non_printables_re.search(string) is None
