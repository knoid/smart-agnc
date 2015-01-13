"""tray_icon.py"""

import gtk
import os

try:
    import appindicator
    HAS_APPINDICATOR = True
except ImportError:
    HAS_APPINDICATOR = False

from . import resource_dir
icons_dir = os.path.join(resource_dir, 'icons')

if HAS_APPINDICATOR:

    class TrayIcon(appindicator.Indicator):
        """TrayIcon"""

        def __init__(self, ti_id):
            super(TrayIcon, self).__init__(ti_id, '',
                appindicator.CATEGORY_SYSTEM_SERVICES)

            self.set_status(appindicator.STATUS_ACTIVE)
            self.set_attention_icon('indicator-messages-new')
            self.set_icon_theme_path(icons_dir)

        def set_icon(self, state):
            super(TrayIcon, self).set_icon('smart-agnc-' + state)

else:

    class TrayIcon(gtk.StatusIcon):
        """TrayIcon"""

        menu = None

        def __init__(self, ti_id):
            super(TrayIcon, self).__init__()
            self.ti_id = ti_id
            gtk.icon_theme_get_default().append_search_path(icons_dir)
            self.connect('button-press-event', self.__on_click__)

        def set_icon(self, state):
            """set_icon"""
            self.set_from_icon_name('smart-agnc-' + state)

        def set_menu(self, menu):
            """set_menu"""
            self.menu = menu

        def __on_click__(self, _, evt):
            if self.menu:
                self.menu.popup(None, None,
                                self.__position_menu__, evt.button, evt.time)

        def __position_menu__(self, menu):
            return gtk.status_icon_position_menu(menu, self)

def main():
    """
    Tests the TrayIcon implementation
    """

    t_icon = TrayIcon('test-tray-icon')

    menu = gtk.Menu()

    m_item = gtk.MenuItem()
    m_item.set_label('Test Item')
    menu.append(m_item)

    menu.show_all()

    t_icon.set_menu(menu)

    gtk.main()

if __name__ == '__main__':
    main()
