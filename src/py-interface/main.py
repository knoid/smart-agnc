"""main.py"""

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
from subprocess import Popen

# local imports
from config import UserPreferences
from conn_info_win import ConnectionInformationWindow
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
    want_to = ab.STATE_CONNECTED

    def __init__(self, user_config, vpn):
        super(AgnNotifier, self).__init__(self._id)
        pynotify.init(self._id)

        self.config = user_config
        self.vpn = vpn
        vpn.connect('agn_state_change', self.on_vpn_state_change)

        self.config_win = ConfigurationWindow(self.get_config_values())
        self.config_win.connect('save', self.do_save)

        self.m_item_conn_status = gtk.MenuItem()
        self.m_item_conn_ip = gtk.MenuItem()
        self.m_item_conn_toggle = gtk.MenuItem()
        self.on_vpn_state_change(None, vpn.get_state())

        self.conn_info_win = ConnectionInformationWindow()
        self.set_menu(self.create_menu())

        gobject.timeout_add(self.reconnect_interval * 1000, self.reconnect)

    def alert(self, msg):
        """alert"""
        notice = pynotify.Notification(self.title, msg)
        notice.show()
        logger.warning('Alert: %s', msg)

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
        self.m_item_conn_toggle.set_label(toggle_btn_text)

        # TODO: Find out `password change required` status code
        if 'SMX 0xXX' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('It is time to change your password!'))
            self.new_password_win.request_new_password()

        elif 'SMX 0x08' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Invalid credentials'))
            self.do_configure()

        elif 'SMX 0x00' in attempt['szStatusText']:
            # unknown error or timeout, try again
            pass

        elif 'SMX 0x' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert(_('Unknown error!') + '\n' + attempt['szStatusText'])
            self.do_configure()

        self.m_item_conn_status.set_label(attempt['szStatusText'])

        ip_address = _('None')
        if new_state > ab.STATE_VPN_CONNECTING:
            ip_address = ab.long2ip(int(attempt['VPNIPAddress']))
        self.m_item_conn_ip.set_label(_('IP: %s') % ip_address)

        script_path = self.config.get('scripts', str(new_state))
        if self.last_state != new_state and len(script_path) > 0:
            try:
                Popen([script_path])
            except OSError as err:
                print script_path, err

        self.last_state = new_state

    def reconnect(self, force=False):
        """reconnect"""
        logger.info(_('Connection status check'))

        state = self.last_state
        if state == ab.STATE_UNKNOWN:
            state = self.vpn.get_state()
            if state == ab.STATE_UNKNOWN:
                attempt = self.vpn.get_connect_attempt_info()
                if attempt['szStatusText'] in ["Connected.", "Reconnected."]:
                    state = ab.STATE_CONNECTED
                else:
                    state = ab.STATE_NOT_CONNECTED
            self.last_state = state

        if ab.STATE_BEFORE_CONNECT <= state <= ab.STATE_CONNECTED:
            # I'm connected

            if self.want_to < state: # I want to get disconnected

                self.vpn.action_disconnect()

        else:
            # I'm disconnected

            if self.want_to > state: # I want to get connected

                cval = self.get_config_values()
                if len(cval) == 3:

                    if force or self.config.getboolean('vpn', 'keepalive'):
                        self.vpn.action_connect(cval['account'],
                                                cval['username'],
                                                cval['password'])
                    else:
                        self.alert('VPN Disconnected')
                        self.want_to = ab.STATE_NOT_CONNECTED

                else:
                    self.alert('Complete credentials to connect')
                    self.do_configure()
                    self.want_to = ab.STATE_NOT_CONNECTED

        return True # prevent the timeout from expiring

    def create_menu(self):
        """create_menu"""
        menu = gtk.Menu()

        m_item = self.m_item_conn_status
        m_item.set_sensitive(False)
        menu.append(m_item)

        m_item = self.m_item_conn_ip
        m_item.set_sensitive(False)
        menu.append(m_item)

        # Separator
        m_item = gtk.SeparatorMenuItem()
        menu.append(m_item)

        # Auto reconnect checkbox
        m_item = self.m_item_conn_toggle
        m_item.connect("activate", self.do_toggle_connection)
        menu.append(m_item)

        # Auto reconnect checkbox
        m_item = gtk.CheckMenuItem(_("Keep alive"))
        m_item.set_active(self.config.getboolean('vpn', 'keepalive'))
        m_item.connect("activate", self.do_toggle_keepalive)
        menu.append(m_item)

        # Separator
        m_item = gtk.SeparatorMenuItem()
        menu.append(m_item)

        # Configuration menu item
        m_item = gtk.MenuItem(_("VPN Connection Information"))
        m_item.connect("activate", self.do_conn_info)
        menu.append(m_item)

        # Configuration menu item
        m_item = gtk.MenuItem(_("Edit Account settings..."))
        m_item.connect("activate", self.do_configure)
        menu.append(m_item)

        menu.show_all()
        return menu

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
            val = self.config.get('vpn', key)
            if len(val) > 0:
                values[key] = val

        if 'password' in values:
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
                values[key] = user['sz' + key.title()]

        return values

non_printables = ''.join([unichr(x) for x in (range(0,32) + range(127,160))])
non_printables_re = re.compile('[%s]' % re.escape(non_printables))
def is_printable(string):
    return non_printables_re.search(string) == None

if __name__ == "__main__":

    __DIR__ = os.path.dirname(__file__)
    i18n_dir = os.path.join(__DIR__, '../../resources/i18n')
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

    CONFIG = UserPreferences({'keepalive': True})
    AGN_BINDER = ab.AgnBinder()
    AgnNotifier(CONFIG, AGN_BINDER)

    gtk.main()
