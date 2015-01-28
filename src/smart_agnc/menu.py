# -*- coding: utf-8 -*-

import gtk
import webbrowser

from about_win import AboutWindow

item_conn_status = gtk.MenuItem()
item_conn_ip = gtk.MenuItem()
item_conn_toggle = gtk.MenuItem()
item_restart_service = gtk.MenuItem()
item_new_version = gtk.MenuItem()

releases_url = 'https://github.com/knoid/smart-agnc/releases'


def create(conn_toggle, keepalive_init_state, keepalive_toggle, conn_info,
           configure, restart_agnc_services, exit_button):

    menu = gtk.Menu()

    m_item = item_conn_status
    m_item.set_sensitive(False)
    menu.append(m_item)

    m_item = item_conn_ip
    m_item.set_sensitive(False)
    menu.append(m_item)

    # Separator
    m_item = gtk.SeparatorMenuItem()
    menu.append(m_item)

    # Restart AGNC services (only visible after a few connection timeouts)
    m_item = item_restart_service
    m_item.set_label('>> %s <<' % _('Restart AGNC Services'))
    m_item.connect('activate', restart_agnc_services)
    menu.append(m_item)

    # Toggle connection state
    m_item = item_conn_toggle
    m_item.connect('activate', conn_toggle)
    menu.append(m_item)

    # Auto reconnect checkbox
    m_item = gtk.CheckMenuItem(_('Keep alive'))
    m_item.set_active(keepalive_init_state)
    m_item.connect('activate', keepalive_toggle)
    menu.append(m_item)

    # Separator
    m_item = gtk.SeparatorMenuItem()
    menu.append(m_item)

    # Configuration menu item
    m_item = gtk.MenuItem(_('VPN Connection Information'))
    m_item.connect('activate', conn_info)
    menu.append(m_item)

    # Configuration menu item
    m_item = gtk.MenuItem(_('Edit Account settings...'))
    m_item.connect('activate', configure)
    menu.append(m_item)

    # Separator
    m_item = gtk.SeparatorMenuItem()
    menu.append(m_item)

    # New version
    m_item = item_new_version
    m_item.set_label(_('Download new version'))
    m_item.connect('activate', lambda a: webbrowser.open(releases_url))
    menu.append(m_item)

    # About
    m_item = gtk.MenuItem(_('About'))
    m_item.connect('activate', lambda mi: AboutWindow().present())
    menu.append(m_item)

    # Exit button
    if exit_button:
        m_item = gtk.MenuItem(_('Quit'))
        m_item.connect('activate', gtk.main_quit)
        menu.append(m_item)

    menu.show_all()
    item_restart_service.hide()
    item_new_version.hide()

    return menu
