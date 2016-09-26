#!/usr/bin/env python
from __future__ import print_function, division
import glob
import os
from os.path import join, exists

from pprint import pformat, pprint

try:
    from tkinter import *
    from tkinter import ttk
except ImportError:
    from Tkinter import *
    import ttk

import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import numpy as np


from vendor.jwxml import SIAF

NIRCAM = 'NIRCam'
NIRSPEC = 'NIRSpec'
NIRISS = 'NIRISS'
MIRI = 'MIRI'
FGS = 'FGS'

class SIAFViewer(object):
    instruments = [NIRCAM, NIRSPEC, NIRISS, MIRI, FGS]
    instrument_filepaths = None
    FILTER_SELECTED, FILTER_ALL = 1, 2

    def __init__(self, instrument_filepaths):
        self.root = Tk()
        self.root.title("SIAF Viewer")
        self.instrument_filepaths = instrument_filepaths

        def close_app():
            self.root.quit()
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", close_app)
        self._construct()
        self.redraw()

    def start(self):
        self.root.mainloop()

    def redraw(self):
        mode = self.filter_behavior.get()
        show_labels = self.show_labels.get()
        self.ax.clear()
        # print("show_labels:", show_labels)
        if mode == self.FILTER_ALL:
            for instrument, siaf in self.siaf_lookup.items():
                for item in siaf.apernames:
                    siaf[item].plot(frame='Tel', ax=self.ax, label=show_labels)
        elif mode == self.FILTER_SELECTED:
            # hacky/slow way to go from selected IDs back to SIAF instances
            for item in self.instrument_tree.selection():
                # print("item:", item)
                for instrument, siaf in self.siaf_lookup.items():
                    # print('item', item, 'instrument', instrument)
                    if item in siaf.apernames:
                        siaf[item].plot(frame='Tel', ax=self.ax, label=show_labels)
                        self.ax.scatter(siaf[item].V2Ref, siaf[item].V3Ref)
        self.ax.set_xlabel('V2 [arcsec]')
        self.ax.set_ylabel('V3 [arcsec]')
        self._canvas.show()

    def apply_filter(self):
        pattern = self.filter_value.get()
        # print("Pattern: {}".format(pattern))
        # pprint(self.instrument_tree.get_children(NIRCAM))

        def traverse_items(base=''):
            # recurse down the tree structure to find all matches
            matches = []
            for item in self.instrument_tree.get_children(base):
                if pattern in item:
                    # print("pattern:", pattern, "item:", item)
                    matches.append(item)
                matches.extend(traverse_items(item))
            return matches

        if pattern not in ('', '*'):
            self.filter_behavior.set(self.FILTER_SELECTED)
            self.instrument_tree.selection_remove(self.instrument_tree.selection())
            matches = traverse_items()
            # print('matches:', matches)
            self.instrument_tree.selection_set(' '.join(matches))
            map(self.instrument_tree.see, matches)
        else:
            self.clear_filter()

    def clear_filter(self):
        self.filter_value.set('')
        self.filter_behavior.set(self.FILTER_ALL)
        self.instrument_tree.selection_remove(self.instrument_tree.selection())
        self.redraw()

    def _construct_plot(self):
        # plot panel
        self.plotframe = ttk.Frame(self.main)
        self.plotframe.grid(column=1, row=0, sticky=(N, W, E, S))

        self.figure = Figure(figsize=(10, 5), dpi=72)
        self.ax = self.figure.add_subplot(1, 1, 1)
        self.ax.set_aspect('equal')
        self.figure.subplots_adjust(left=0.09, right=0.96)

        self._canvas = FigureCanvasTkAgg(self.figure, master=self.plotframe)
        self._canvas.show()
        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self._toolbar = NavigationToolbar2TkAgg(self._canvas, self.plotframe)
        self._toolbar.update()
        self._canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)

        def on_key_event(event):
            # print('you pressed %s' % event.key)
            key_press_handler(event, self._canvas, self._toolbar)

        self._canvas.mpl_connect('key_press_event', on_key_event)

    def _construct_filter(self):
        # filter / tree panel
        self.filterframe = ttk.Frame(self.main)
        self.filterframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.filterframe.columnconfigure(1, weight=1)

        self.filter_value = StringVar()
        filter_label = ttk.Label(self.filterframe, text="Select by pattern:")
        filter_label.grid(column=0, row=0, sticky=(N, W))
        self.filter_entry = ttk.Entry(self.filterframe, textvariable=self.filter_value)
        self.filter_entry.grid(column=1, row=0, sticky=(N, W, E, S))

        filter_button = ttk.Button(self.filterframe, text="Filter", command=self.apply_filter)
        filter_button.grid(column=2, row=0, sticky=(N, E))

        clear_button = ttk.Button(self.filterframe, text="Clear", command=self.clear_filter)
        clear_button.grid(column=2, row=1, sticky=(N, E))


        filter_behavior_label = ttk.Label(self.filterframe, text="Show:")
        filter_behavior_label.grid(column=0, row=1)
        self.filter_behavior = IntVar(value=self.FILTER_ALL)
        self.filter_behavior.trace("w", lambda evt, x, y: self.redraw())
        radiobuttons_frame = ttk.Frame(self.filterframe)
        radiobuttons_frame.grid(column=1, row=1)

        self.filter_behavior_selected = ttk.Radiobutton(
            radiobuttons_frame,
            text='Selected',
            value=self.FILTER_SELECTED,
            variable=self.filter_behavior
        )
        self.filter_behavior_selected.grid(column=1, row=0)
        self.filter_behavior_all = ttk.Radiobutton(
            radiobuttons_frame,
            text='All',
            value=self.FILTER_ALL,
            variable=self.filter_behavior
        )
        self.filter_behavior_all.grid(column=3, row=0)

        self.instrument_tree = ttk.Treeview(self.filterframe)
        self.instrument_tree.grid(column=0, row=2, sticky=(N, W, E, S), columnspan=3)
        self._load_instruments()
        self.filterframe.rowconfigure(2, weight=1)

        info = ttk.Label(self.filterframe, text='Hold control and click to select multiple.\nHold shift and click to select ranges.')
        info.grid(column=0, row=3, columnspan=3)

        self.show_labels = BooleanVar(value=False)
        self.show_labels_checkbox = ttk.Checkbutton(
            self.filterframe,
            text='Show labels?',
            variable=self.show_labels,
            command=self.redraw,
            onvalue=True,
            offvalue=False
        )
        self.show_labels_checkbox.grid(column=0, row=4, columnspan=3)

    def _construct(self):
        self.root.minsize(width=1024, height=500)
        # ensure resizing happens:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.main = ttk.Frame(self.root)
        self.main.grid(column=0, row=0, sticky=(N, W, E, S))

        self._construct_plot()
        self._construct_filter()

        # massage the gui library a bit
        for child in self.main.winfo_children():
            child.grid_configure(padx=5, pady=5)
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=1)
        self.main.rowconfigure(0, weight=1)

    def _load_instrument(self, instrument):
        print("Loading {} from {}".format(instrument, self.instrument_filepaths[instrument]))
        return SIAF(
            instr=instrument,
            filename=self.instrument_filepaths[instrument]
        )

    def _load_instruments(self):
        self.siaf_lookup = {}

        # Every instrument is a unique snowflake, so load them one by one
        self.siaf_lookup[NIRCAM] = self._load_instrument(NIRCAM)
        # NIRCam
        #  - NRCA
        #    - NRCA1 .. 5
        #  - NRCB
        #    - NRCB1 .. 5

        self.instrument_tree.insert('', 'end', iid=NIRCAM, text=NIRCAM)
        self.instrument_tree.insert(NIRCAM, 'end', iid='NRCA', text='NRCA')
        a_segments = ('NRCA1', 'NRCA2', 'NRCA3', 'NRCA4', 'NRCA5')
        for segment in a_segments:
            self.instrument_tree.insert('NRCA', 'end', iid=segment, text=segment)

        self.instrument_tree.insert(NIRCAM, 'end', iid='NRCB', text='NRCB')
        b_segments = ('NRCB1', 'NRCB2', 'NRCB3', 'NRCB4', 'NRCB5')
        for segment in b_segments:
            self.instrument_tree.insert('NRCB', 'end', iid=segment, text=segment)

        for aper in sorted(self.siaf_lookup[NIRCAM].apernames):
            if 'NRCA' in aper and not 'NRCALL' in aper:
                if aper[:5] in a_segments:
                    self.instrument_tree.insert(aper[:5], 'end', iid=aper, text=aper)
                else:
                    self.instrument_tree.insert('NRCA', 'end', iid=aper, text=aper)
            elif 'NRCB' in aper:
                if aper[:5] in b_segments:
                    self.instrument_tree.insert(aper[:5], 'end', iid=aper, text=aper)
                else:
                    self.instrument_tree.insert('NRCB', 'end', iid=aper, text=aper)
            else:
                self.instrument_tree.insert(NIRCAM, 'end', iid=aper, text=aper)

        # MIRI
        #  - MIRIM
        #  - MIRIFU
        self.siaf_lookup[MIRI] = self._load_instrument(MIRI)
        self.instrument_tree.insert('', 'end', iid=MIRI, text=MIRI)
        self.instrument_tree.insert(MIRI, 'end', iid='MIRIFU', text='MIRIFU')
        self.instrument_tree.insert(MIRI, 'end', iid='MIRIM', text='MIRIM')

        for aper in sorted(self.siaf_lookup[MIRI].apernames):
            if 'MIRIFU' in aper:
                self.instrument_tree.insert('MIRIFU', 'end', iid=aper, text=aper)
            elif 'MIRIM' in aper:
                self.instrument_tree.insert('MIRIM', 'end', iid=aper, text=aper)

        for instrkey in (a for a in self.instruments if a != NIRCAM and a != MIRI):
            self.siaf_lookup[instrkey] = self._load_instrument(instrkey)
            self.instrument_tree.insert('', 'end', iid=instrkey, text=instrkey)
            for aper in sorted(self.siaf_lookup[instrkey].apernames):
                self.instrument_tree.insert(instrkey, 'end', iid=aper, text=aper)

        self.instrument_tree.bind('<<TreeviewSelect>>', lambda evt: self.handle_selection())

    def handle_selection(self):
        if self.filter_behavior.get() == self.FILTER_ALL:
            return
        else:
            self.redraw()
