# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Widget."""

# Third party imports
from qtpy.QtWidgets import QVBoxLayout, QWidget

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

        self.renderview = RenderView(self)

        layout = QVBoxLayout()
        layout.addWidget(self.renderview)
        self.setLayout(layout)

    def set_html(self, html_text, base_url=None):
        """Set html text."""
        if base_url is not None:
            self.renderview.setHtml(html_text, base_url)
        else:
            self.renderview.setHtml(html_text)

    def clear(self):
        """Clear widget web view content."""
        self.set_html('')
