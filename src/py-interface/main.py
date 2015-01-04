"""main.py"""

# system imports
import gobject
import gtk
import pynotify

# local imports
from config import UserPreferences
from conn_info_win import ConnectionInformationWindow
from settings_win import ConfigurationWindow
from tray_icon import TrayIcon
import agn_binder as ab

class AgnNotifier(TrayIcon):
    """AgnNotifier"""

    config_win = None
    title = 'AT&T Notifier'
    reconnect_interval = 10 # seconds
    last_state = 0
    want_to = ab.STATE_CONNECTED

    def __init__(self, user_config, vpn):
        super(AgnNotifier, self).__init__("at&t-smart")

        pynotify.init('AgnNotifier')

        self.config = user_config
        self.vpn = vpn
        vpn.connect('agn_state_change', self.on_vpn_state_change)

        self.config_win = ConfigurationWindow(self.get_config_values())
        self.config_win.connect('save', self.do_save)

        self.m_item_conn_status = gtk.MenuItem()
        self.m_item_conn_toggle = gtk.MenuItem()
        self.on_vpn_state_change(None, vpn.get_state())

        self.conn_info_win = ConnectionInformationWindow()
        self.set_menu(self.create_menu())

        gobject.timeout_add(self.reconnect_interval * 1000, self.reconnect)

    def alert(self, msg):
        """alert"""
        notice = pynotify.Notification(self.title, msg)
        notice.show()
        print 'Alert:', msg

    def on_vpn_state_change(self, _, new_state):
        """on_vpn_state_change"""

        # ignoring higher states than STATE_CONNECTED we can be sure that 'the
        # higher the state, the more `connected` we are' remains True
        if new_state > ab.STATE_CONNECTED:
            return

        attempt = self.vpn.get_connect_attempt_info()

        toggle_btn_text = 'Connect'
        if self.want_to == ab.STATE_CONNECTED:
            toggle_btn_text = 'Disconnect'
        self.m_item_conn_toggle.set_label(toggle_btn_text)

        # TODO: Find out `password change required` status code
        if 'SMX 0xXX' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert('It is time to change your password!')
            self.new_password_win.request_new_password()

        elif 'SMX 0x08' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert('Invalid credentials')
            self.do_configure()

        elif 'SMX 0x00' in attempt['szStatusText']:
            # unknown error or timeout, try again
            pass

        elif 'SMX 0x' in attempt['szStatusText']:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.alert('Unknown error!\n' + attempt['szStatusText'])
            self.do_configure()

        self.m_item_conn_status.set_label(attempt['szStatusText'])

        self.last_state = new_state

    def reconnect(self):
        """reconnect"""
        print "reconnect"

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
                    if self.config.getboolean('keepalive'):
                        self.vpn_connect(cval)
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

        # Auto reconnect checkbox
        m_item = self.m_item_conn_toggle
        m_item.connect("activate", self.do_toggle_connection)
        menu.append(m_item)

        # Auto reconnect checkbox
        m_item = gtk.CheckMenuItem("Keep alive")
        m_item.set_active(self.config.getboolean('keepalive'))
        m_item.connect("activate", self.do_toggle_keepalive)
        menu.append(m_item)

        # Separator
        m_item = gtk.SeparatorMenuItem()
        menu.append(m_item)

        # Configuration menu item
        m_item = gtk.MenuItem("VPN Connection Information")
        m_item.connect("activate", self.do_conn_info)
        menu.append(m_item)

        # Configuration menu item
        m_item = gtk.MenuItem("Edit Account settings...")
        m_item.connect("activate", self.do_configure)
        menu.append(m_item)

        menu.show_all()
        return menu

    def do_configure(self, _=None):
        """do_configure"""
        self.config_win.present()

    def do_conn_info(self, _=None):
        """do_conn_info"""
        self.conn_info_win.set_text('Refreshing...')
        self.conn_info_win.show_all()
        self.conn_info_win.present()
        attempt = self.vpn.get_connect_attempt_info().iteritems()
        attempt_txt = '\n'.join([key + ':' + val for key, val in attempt])
        self.conn_info_win.set_text(attempt_txt)

    def do_save(self, _, account, username, password):
        """do_save"""
        self.config.set('account', account)
        self.config.set('username', username)
        self.config.set('password', password)
        self.config_win.hide()
        self.want_to = ab.STATE_CONNECTED
        self.reconnect()

    def do_toggle_connection(self, _):
        """do_toggle_connection"""
        if self.want_to == ab.STATE_CONNECTED:
            self.want_to = ab.STATE_NOT_CONNECTED
            self.vpn.action_disconnect()
        else:
            self.want_to = ab.STATE_CONNECTED
            self.vpn_connect()

    def do_toggle_keepalive(self, win):
        """do_toggle_keepalive"""
        self.config.setboolean('keepalive', win.get_active())

    def get_config_values(self):
        """get_config_values"""
        keys = ['account', 'username', 'password']
        values = {}
        for key in keys:
            val = self.config.get(key)
            if len(val) > 0:
                values[key] = val

        if len(values) == 0:
            user = self.vpn.get_user_info()
            for key in keys:
                values[key] = user['sz' + key.title()]

        return values

    def vpn_connect(self, cval=None):
        """vpn_connect"""
        if not cval:
            cval = self.get_config_values()

        if len(cval) == 3:
            self.vpn.action_connect(cval['account'],
                                    cval['username'],
                                    cval['password'])

if __name__ == "__main__":

    CONFIG = UserPreferences({'keepalive': 'on'})
    AGN_BINDER = ab.AgnBinder()
    AgnNotifier(CONFIG, AGN_BINDER)

    gtk.main()
