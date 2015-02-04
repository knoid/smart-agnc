# -*- coding: utf-8 -*-

# system imports
import base64
import gtk
import logging
import os
import pynotify
from subprocess import Popen, PIPE

# local imports
import agn_binder as ab
from conn_info_win import ConnectionInformationWindow
import menu
from new_password_win import NewPasswordWindow
from settings_win import ConfigurationWindow
from tray_icon import TrayIcon
import update
import utils

logger = logging.getLogger(__name__)


class AgnNotifier(TrayIcon):
    """AgnNotifier"""

    _id = 'at&t-smart'

    changing_password = False

    def __init__(self, user_config, vpn, monitor, events, opts):
        super(AgnNotifier, self).__init__(self._id)
        pynotify.init(self._id)

        self.config = user_config
        self.events = events

        self.new_password_win = NewPasswordWindow()
        self.new_password_win.connect('new-password', self.set_new_password)

        self.monitor = monitor
        self.vpn = vpn
        events.connect('agn-state-change', self.on_vpn_state_change)
        events.connect('agn-state-change', self.trigger_external_script)
        events.connect('configuration-error', self.do_configure)

        vpn_values, proxy_values = self.config.get_connection_values()
        self.config_win = ConfigurationWindow(
            events, vpn_values, user_config.getboolean('proxy', 'enabled'),
            proxy_values, self.new_password_win)
        self.config_win.connect('save', self.do_save)

        self.conn_info_win = ConnectionInformationWindow()
        self.set_menu(menu.create(
            conn_toggle=self.do_toggle_connection,
            keepalive_init_state=self.config.getboolean('vpn', 'keepalive'),
            keepalive_toggle=self.do_toggle_keepalive,
            conn_info=self.do_conn_info,
            configure=self.do_configure,
            restart_agnc_services=self.do_restart_agnc_services,
            exit_button=opts.exit_button))

        if opts.check_update:
            update.check_periodically(self.upgrade_available)

        gtk.gdk.notify_startup_complete()

    @utils.async()
    def trigger_external_script(self, unused_events, state):
        logger.info('trigger_external_script, state=%d', state)
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
                utils.alert('\n'.join(output))

    @utils.async()
    def on_vpn_state_change(self, unused_events, new_state):
        logger.info('on_vpn_state_change, new_state=%d', new_state)

        # ignoring higher states than STATE_CONNECTED we can be sure that 'the
        # higher the state, the more `connected` we are' remains True
        if new_state > ab.STATE_CONNECTED:
            return

        if new_state == ab.STATE_DAEMON_DEAD:
            utils.restart_agnc_services()

        attempt = self.vpn.get_connect_attempt_info()
        menu.item_conn_status.set_label(attempt['StatusText'])

        toggle_btn_text = _('Connect')
        if self.monitor.want_to == ab.STATE_CONNECTED:
            toggle_btn_text = _('Disconnect')
        menu.item_conn_toggle.set_label(toggle_btn_text)

        ip_address = _('Not available.')
        icon_state = 'disabled'
        if new_state > ab.STATE_VPN_CONNECTING:
            ip_address = ab.long2ip(attempt['VPNIPAddress'])
            icon_state = 'enabled'

            if self.changing_password:
                encoded_password = base64.b64encode(self.changing_password)
                self.config.set('vpn', 'password', encoded_password)
                self.config.write_to_disk()
                self.changing_password = False

        menu.item_conn_ip.set_label(_('IP: %s') % ip_address)
        self.set_icon(icon_state)

        # 12 = password expired
        # 16 = incorrect new password
        if attempt['StatusCode'] in [12, 16]:
            self.monitor.set_want_to(ab.STATE_NOT_CONNECTED)
            utils.alert(_('It is time to change your password!'))
            self.new_password_win.request_new_password()

        # 8 = Invalid credentials
        elif 8 == attempt['StatusCode']:
            self.monitor.set_want_to(ab.STATE_NOT_CONNECTED)
            utils.alert(_('Invalid credentials'))
            self.events.emit('configuration-error', attempt['StatusCode'])

        # 502 = User-requested disconnect
        elif 0 < attempt['StatusCode'] and 502 != attempt['StatusCode']:
            self.monitor.set_want_to(ab.STATE_NOT_CONNECTED)
            utils.alert(_('Unknown error!') + '\n' + attempt['StatusText'])
            self.events.emit('configuration-error', attempt['StatusCode'])

    def set_new_password(self, unused_win, new_password):
        vpn, proxy = self.config.get_config_values()
        self.changing_password = new_password
        self.monitor.vpn_connect(vpn, proxy, new_password)
        self.monitor.set_want_to(ab.STATE_CONNECTED)

    def upgrade_available(self):
        utils.alert(_('There is a new version available!'))
        menu.item_new_version.show()

    def do_configure(self, unused_m_item=None, unused_state=None):
        self.config_win.present()

    def do_conn_info(self, unused_m_item=None):
        attempt = self.vpn.get_connect_attempt_info()
        self.conn_info_win.set_dict(attempt)
        self.conn_info_win.present()

    def do_restart_agnc_services(self, unused_m_item=None):
        ab.restart_agnc_services()

    def do_save(self, config_win,
                v_account, v_username, v_password,
                use_proxy, p_server, p_user, p_password):
        config_win.hide()
        self.config.set('vpn', 'account', v_account)
        self.config.set('vpn', 'username', v_username)
        self.config.set('vpn', 'password', base64.b64encode(v_password))
        self.config.setboolean('proxy', 'enabled', use_proxy)
        self.config.set('proxy', 'server', p_server)
        self.config.set('proxy', 'user', p_user)
        self.config.set('proxy', 'password', base64.b64encode(p_password))
        self.config.write_to_disk()
        self.monitor.set_want_to(ab.STATE_CONNECTED)
        self.monitor.check_connection()

    def do_toggle_connection(self, unused_m_item=None):
        if self.monitor.want_to == ab.STATE_CONNECTED:
            self.monitor.set_want_to(ab.STATE_NOT_CONNECTED)
            self.vpn.action_disconnect()
            self.on_vpn_state_change(self.vpn, ab.STATE_NOT_CONNECTED)
        else:
            self.monitor.set_want_to(ab.STATE_CONNECTED)
            self.monitor.check_connection(True)

    def do_toggle_keepalive(self, m_item):
        self.config.setboolean('vpn', 'keepalive', m_item.get_active())
        self.config.write_to_disk()
