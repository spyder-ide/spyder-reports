# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Widget."""

# Standard library imports
import codecs
import os.path as osp

# Third party imports
from qtpy.QtCore import QUrl
from qtpy.QtWidgets import QVBoxLayout, QWidget, QTabWidget

# Spyder-IDE and Local imports
from spyder.widgets.browser import FrameWebView
from spyder.utils.sourcecode import disambiguate_fname


class RenderView(FrameWebView):
    """Web widget that shows rendered report."""

    def __init__(self, parent):
        """Initialiaze the WebView."""
        FrameWebView.__init__(self, parent)


class ReportsWidget(QWidget):
    """Reports widget."""

    def __init__(self, parent):
        """Initialiaze ReportsWidget."""
        QWidget.__init__(self, parent)

        self.setWindowTitle("Reports")

        self.tabs = QTabWidget()
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)

        self.renderviews = {}
        self.filenames = []

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.set_html('', 'Welcome')

    def set_html(self, html_text, fname, base_url=None):
        """Set html text."""
        name = self.disambiguate_fname(fname)
        renderview = self.renderviews.get(fname)

        if 'Welcome' in self.renderviews and renderview is None:
            # Overwrite the welcome tab
            renderview = self.renderviews.pop('Welcome')
            self.renderviews[fname] = renderview
            self.tabs.setTabText(0, name)
            self.filenames[0] = fname

        if renderview is None:
            # create a new renderview
            renderview = RenderView(self)
            self.renderviews[fname] = renderview
            self.tabs.addTab(renderview, name)
            self.filenames.append(fname)

        if base_url is not None:
            renderview.setHtml(html_text, base_url)
        else:
            renderview.setHtml(html_text)

        self.tabs.setCurrentWidget(renderview)

    def set_html_from_file(self, output_fname, input_fname=None):
        """Set html text from a file."""
        if input_fname is None:
            input_fname = output_fname
        html = ""
        with codecs.open(output_fname, encoding="utf-8") as file:
            html = file.read()

        base_url = QUrl()
        self.set_html(html, input_fname, base_url)

    def close_tab(self, index):
        """Close tab, and remove its widget form renderviews."""
        fname = self.filenames.pop(index)
        self.renderviews.pop(fname)
        self.tabs.removeTab(index)

    def disambiguate_fname(self, fname):
        """Generate a file name without ambiguation."""
        files_path_list = [filename for filename in self.filenames
                           if filename]
        return disambiguate_fname(files_path_list, fname)

    def clear_all(self):
        """Clear widget web view content."""
        for name in self.renderviews:
            self.set_html('', name)
