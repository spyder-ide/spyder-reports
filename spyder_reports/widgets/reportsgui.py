# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Widget."""

# Third party imports
from qtpy.QtWidgets import QVBoxLayout, QWidget, QTabWidget

# Spyder-IDE and Local imports
from spyder.widgets.browser import FrameWebView


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

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.set_html('', 'Welcome')

    def set_html(self, html_text, name, base_url=None):
        """Set html text."""
        renderview = self.renderviews.get(name)

        if 'Welcome' in self.renderviews:
            # Overwrite the welcome tab
            renderview =self.renderviews.pop('Welcome')
            self.renderviews[name] = renderview
            self.tabs.setTabText(0, name)

        if renderview is None:
            # create a new renderview
            renderview = RenderView(self)
            self.renderviews[name] = renderview
            self.tabs.addTab(renderview, name)

        if base_url is not None:
            renderview.setHtml(html_text, base_url)
        else:
            renderview.setHtml(html_text)

        self.tabs.setCurrentWidget(renderview)

    def close_tab(self, index):
        "Close tab, and remove its widget form renderviews."
        self.renderviews.pop(self.tabs.tabText(index))
        self.tabs.removeTab(index)


    def clear_all(self):
        """Clear widget web view content."""
        for name in self.renderviews:
            self.set_html('', name)
