# -*- coding: utf-8 -*-

import gtk
import os

try:
    import appindicator
    HAS_APPINDICATOR = True
except ImportError:
    HAS_APPINDICATOR = False

from . import icons_dir

if HAS_APPINDICATOR:

    class TrayIcon(appindicator.Indicator):

        def __init__(self, ti_id):
            super(TrayIcon, self).__init__(
                ti_id, '', appindicator.CATEGORY_SYSTEM_SERVICES)

            self.set_status(appindicator.STATUS_ACTIVE)
            self.set_attention_icon('indicator-messages-new')
            self.set_icon_theme_path(icons_dir)

        def set_icon(self, state):
            super(TrayIcon, self).set_icon('smart-agnc-' + state)

else:

    class TrayIcon(gtk.StatusIcon):

        menu = None

        def __init__(self, ti_id):
            super(TrayIcon, self).__init__()
            self.ti_id = ti_id
            self.connect('button-press-event', self.__on_click__)

        def set_icon(self, state):
            self.set_from_icon_name('smart-agnc-' + state)

        def set_menu(self, menu):
            self.menu = menu

        def __on_click__(self, _, evt):
            if self.menu:
                self.menu.popup(None, None,
                                self.__position_menu__, evt.button, evt.time)

        def __position_menu__(self, menu):
            return gtk.status_icon_position_menu(menu, self)
