# -*- coding: utf-8 -*-

import gtk

item_conn_status = gtk.MenuItem()
item_conn_ip = gtk.MenuItem()
item_conn_toggle = gtk.MenuItem()


def create(conn_toggle, keepalive_init_state, keepalive_toggle, conn_info,
           configure):

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

    # Auto reconnect checkbox
    m_item = item_conn_toggle
    m_item.connect("activate", conn_toggle)
    menu.append(m_item)

    # Auto reconnect checkbox
    m_item = gtk.CheckMenuItem(_("Keep alive"))
    m_item.set_active(keepalive_init_state)
    m_item.connect("activate", keepalive_toggle)
    menu.append(m_item)

    # Separator
    m_item = gtk.SeparatorMenuItem()
    menu.append(m_item)

    # Configuration menu item
    m_item = gtk.MenuItem(_("VPN Connection Information"))
    m_item.connect("activate", conn_info)
    menu.append(m_item)

    # Configuration menu item
    m_item = gtk.MenuItem(_("Edit Account settings..."))
    m_item.connect("activate", configure)
    menu.append(m_item)

    menu.show_all()
    return menu
