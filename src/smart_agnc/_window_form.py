# -*- coding: utf-8 -*-

import gtk

from _window import _Window


class _WindowForm(_Window):

    def __init__(self):
        super(_WindowForm, self).__init__()

        table = gtk.Table(rows=4, columns=3)
        table.set_col_spacings(10)
        table.set_row_spacings(10)
        self.add(table)

        self.table = table

    def _attach(self, widget, left, top):
        """
        Attaches a widget into a position inside the table occupying one cell.
        Returns the inserted widget
        """
        self.table.attach(widget, left, left + 1, top, top + 1, 0, 0, 0, 0)
        return widget

    def _make_entry(self, left, top):
        """
        Returns and attaches an entry with some defaults appropriate to AGNC.
        """
        entry = gtk.Entry()
        entry.set_max_length(128)
        entry.set_width_chars(20)
        return self._attach(entry, left, top)

    def _make_label(self, txt, left, top):
        """
        Attaches a label to the table. Returns the new label.
        """
        label = gtk.Label(txt)
        return self._attach(label, left, top)
