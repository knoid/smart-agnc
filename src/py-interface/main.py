"""
This app will create a seamless VPN connection between you and your enterprise
by adding a tray icon and keeping you connected whenever possible.
"""

# system imports
import base64
import gettext
import gobject
import gtk
import logging
import optparse
import os
import pynotify
import re
from subprocess import Popen, PIPE
import time

# local imports
from config import UserPreferences
from conn_info_win import ConnectionInformationWindow
import menu
from new_password_win import NewPasswordWindow
from settings_win import ConfigurationWindow
from tray_icon import TrayIcon
import agn_binder as ab

__title__ = 'smart-agnc'

logger = logging.getLogger(__name__)

class AgnNotifier(TrayIcon):
    """AgnNotifier"""

    config_win = None
    title = 'Smart AT&T Client'
    _id = 'at&t-smart'
    reconnect_interval = 10 # seconds
    last_state = 0
    changing_password = False
    connecting_timeout = 0
    want_to = ab.STATE_CONNECTED

    def __init__(self, root_dir, user_config, vpn):
        icons_dir = os.path.join(root_dir, 'resources', 'icons')
        super(AgnNotifier, self).__init__(self._id, icons_dir)
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
                configure=self.do_configure))

        gobject.timeout_add(self.reconnect_interval * 1000, self.reconnect)

    def alert(self, msg):
        """alert"""
        notice = pynotify.Notification(self.title, msg)
        notice.show()
        logger.warning('Alert: %s', msg.replace('\n', ' \\n '))

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
            if proc: # the external process was successfully initialized
                output += [s.rstrip() for s in proc.communicate() if s]
            if len(output) > 1:
                self.alert('\n'.join(output))

    def on_vpn_state_change(self, vpn, new_state):
        """on_vpn_state_change"""

        # ignoring higher states than STATE_CONNECTED we can be sure that 'the
        # higher the state, the more `connected` we are' remains True
        if new_state > ab.STATE_CONNECTED:
            return

        icon_state = 'disabled'
        if new_state > ab.STATE_VPN_CONNECTING:
            icon_state = 'enabled'
        self.set_icon(icon_state)

        attempt = self.vpn.get_connect_attempt_info()

        toggle_btn_text = _('Connect')
        if self.want_to == ab.STATE_CONNECTED:
            toggle_btn_text = _('Disconnect')
        menu.item_conn_toggle.set_label(toggle_btn_text)

        # 12 = password expired
        # 16 = incorrect new password
        if attempt['StatusCode'] in [12, 16]:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('It is time to change your password!'))
            self.new_password_win.request_new_password()

        elif 8 == attempt['StatusCode']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Invalid credentials'))
            self.do_configure()

        elif 'SMX 0x00' in attempt['StatusText']:
            # unknown error or timeout, try again
            pass

        elif 'SMX 0x' in attempt['StatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Unknown error!') + '\n' + attempt['StatusText'])
            self.do_configure()

        menu.item_conn_status.set_label(attempt['StatusText'])

        ip_address = _('None')
        if new_state > ab.STATE_VPN_CONNECTING:
            ip_address = ab.long2ip(attempt['VPNIPAddress'])
        menu.item_conn_ip.set_label(_('IP: %s') % ip_address)

        self.last_state = new_state

    def reconnect(self, force=False):
        """reconnect"""
        logger.info('Connection status check')

        state = self.last_state
        if state == ab.STATE_UNKNOWN:
            state = self.vpn.get_state()
            if state == ab.STATE_UNKNOWN:
                attempt = self.vpn.get_connect_attempt_info()
                if attempt['StatusText'] in ["Connected.", "Reconnected."]:
                    state = ab.STATE_CONNECTED
                else:
                    state = ab.STATE_NOT_CONNECTED
            self.last_state = state

        # if it is connecting and exceeds the timeout -> disconnect
        if ab.STATE_BEFORE_CONNECT < state < ab.STATE_VPN_RECONNECTED and \
                self.connecting_timeout < time.time():
            logger.info('Timeout! Disconnecting...')
            self.vpn.action_disconnect()
            return True

        if ab.STATE_BEFORE_CONNECT <= state <= ab.STATE_CONNECTED:
            # I'm connected

            if self.changing_password:
                encoded_password = base64.b64encode(self.changing_password)
                self.config.set('vpn', 'password', encoded_password)
                self.config.write_to_disk()
                self.changing_password = False

            if self.want_to < state: # I want to get disconnected

                self.vpn.action_disconnect()

        else:
            # I'm disconnected

            if self.want_to > state: # I want to get connected

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

        return True # prevent the timeout from expiring

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
                logger.warning(_('Password was not encoded in config file.'))

        if len(values) == 0:
            user = self.vpn.get_user_info()
            for key in keys:
                values[key] = user[key.title()]

        # do not return empty values
        return dict((key, val) for key, val in values.items() if len(val) > 0)

non_printables = ''.join([unichr(x) for x in (range(0,32) + range(127,160))])
non_printables_re = re.compile('[%s]' % re.escape(non_printables))
def is_printable(string):
    return non_printables_re.search(string) == None

if __name__ == "__main__":

    __ROOT_DIR__ = os.path.join(os.path.dirname(__file__), '..', '..')
    i18n_dir = os.path.join(__ROOT_DIR__, 'resources', 'i18n')
    gettext.install(__title__, i18n_dir)

    optp = optparse.OptionParser()
    optp.add_option('-v', '--verbose', dest='verbose', action='count',
                    help=_("Increase verbosity (specify multiple times for more)"))
    opts, args = optp.parse_args()

    log_level = logging.WARNING # default
    if opts.verbose == 1:
        log_level = logging.INFO
    elif opts.verbose >= 2:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level)

    CONFIG = UserPreferences({'keepalive': True, 'timeout': 40})
    AGN_BINDER = ab.AgnBinder()
    AgnNotifier(__ROOT_DIR__, CONFIG, AGN_BINDER)

    gtk.main()
