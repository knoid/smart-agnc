# -*- coding: utf-8 -*-

# system imports
import gobject
import gtk


class _Window(gtk.Window):
    """
    Abstract Window class that predefines the behaviour of every window. It
    lets you close with Esc and submit with Return. It also adds a new signal
    called `form-submit` to handle the Return key.
    """

    def __init__(self):
        super(_Window, self).__init__()

        self.set_resizable(False)
        self.set_border_width(10)
        self.connect('delete-event', __prevent_destroy__)
        self.connect('key-press-event', __on_key__)

gobject.signal_new('form-submit', _Window, gobject.SIGNAL_RUN_FIRST, None, ())


def __on_key__(widget, evt):
    if evt.keyval == gtk.keysyms.Escape:
        widget.hide()

    if evt.keyval == gtk.keysyms.Return:
        widget.emit('form-submit')


def __prevent_destroy__(widget, _=None):
    widget.hide()
    return True


class _WindowCentered(object):

    def present(self):
        self.set_position(gtk.WIN_POS_CENTER)
        super(_Window, self).present()


class _WindowForm(_Window):

    def __init__(self):
        super(_WindowForm, self).__init__()

        table = gtk.Table(rows=4, columns=3)
        table.set_col_spacings(10)
        table.set_row_spacings(10)
        self.add(table)

        self.table = table

    def _attach(self, widget, left, top, width=1, height=1, table=None):
        """
        Attaches a widget into a position inside the table occupying one cell.
        Returns the inserted widget
        """
        if not table:
            table = self.table
        table.attach(widget, left, left + width, top, top + height)
        return widget

    def _make_entry(self, left, top, table=None):
        """
        Returns and attaches an entry with some defaults appropriate to AGNC.
        """
        entry = gtk.Entry()
        entry.set_max_length(128)
        entry.set_width_chars(20)
        return self._attach(entry, left, top, table=table)

    def _make_label(self, txt, left, top, table=None):
        """
        Attaches a label to the table. Returns the new label.
        """
        label = gtk.Label(txt)
        label.set_alignment(0, 0.5)
        return self._attach(label, left, top, table=table)
