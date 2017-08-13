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

# Third party imports
from qtpy.QtCore import QUrl, Slot
from qtpy.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QWidget, QMenu,
                            QToolButton)

# Spyder-IDE and Local imports
from spyder.widgets.browser import FrameWebView
from spyder.utils.sourcecode import disambiguate_fname
from spyder.widgets.waitingspinner import QWaitingSpinner
from spyder.widgets.tabs import BaseTabs
from spyder.utils import icon_manager as ima
from spyder.utils.qthelpers import (add_actions, create_toolbutton)

from ..utils import WELCOME_PATH


class RenderView(FrameWebView):
    """Web widget that shows rendered report."""

    def __init__(self, parent):
        """Initialiaze the WebView."""
        FrameWebView.__init__(self, parent)


class ReportsWidget(QWidget):
    """Reports widget."""

    def __init__(self, parent, menu_actions=None):
        """Initialiaze ReportsWidget."""
        QWidget.__init__(self, parent)

        self.renderviews = {}
        self.filenames = []
        self.menu_actions = menu_actions

        self.setWindowTitle("Reports")

        self.tabs = BaseTabs(self,
                             actions=self.menu_actions,
                             menu_use_tooltips=False)
        self.tabs.setMovable(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBar().tabMoved.connect(self.move_tab)

        # Progress bar
        self.progress_bar = QWidget(self)
        self.status_text = QLabel(self.progress_bar)
        self.spinner = QWaitingSpinner(self.progress_bar, centerOnParent=False)
        self.spinner.setNumberOfLines(12)
        self.spinner.setInnerRadius(2)
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.spinner)
        progress_layout.addWidget(self.status_text)
        self.progress_bar.setLayout(progress_layout)
        self.progress_bar.hide()

        # Menu as corner widget
        if self.menu_actions:
            options_button = create_toolbutton(self,
                                               text='Options',
                                               icon=ima.icon('tooloptions'))
            options_button.setPopupMode(QToolButton.InstantPopup)
            menu = QMenu(self)
            add_actions(menu, self.menu_actions)
            options_button.setMenu(menu)
            self.tabs.setCornerWidget(options_button)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

    def set_html(self, html_text, fname, base_url=None):
        """Set html text."""
        name = self.disambiguate_fname(fname)
        renderview = self.renderviews.get(fname)

        if WELCOME_PATH in self.renderviews and renderview is None:
            # Overwrite the welcome tab
            renderview = self.renderviews.pop(WELCOME_PATH)
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
        self.tabs.currentChanged.emit(self.tabs.currentIndex())

    def set_html_from_file(self, output_fname, input_fname=None):
        """Set html text from a file."""
        if input_fname is None:
            input_fname = output_fname
        html = ""
        with codecs.open(output_fname, encoding="utf-8") as file:
            html = file.read()

        base_url = QUrl()
        self.set_html(html, input_fname, base_url)

    @Slot(str)
    def render_started(self, fname):
        """Show progress bar and starts spinner.

        Args:
            fname (str): Name of the file being rendered
        """
        self.spinner.start()
        name = self.disambiguate_fname(fname)
        text = "Rendering: {}".format(name)
        self.status_text.setText(text)
        self.progress_bar.show()
        self.set_html('', fname)

    @Slot(str)
    def update_progress(self, text):
        """Update progress bar status text.

        Args:
            text (str):  text to be displayed.
        """
        if len(text) > 50:
            text = "{}...".format(text[:47])
        self.status_text.setText(text)

    @Slot(bool, object, object)
    def render_finished(self, ok, fname, error):
        """Handle render finish signal.

        If error, displays it, otherwise hide progress bar.

        Args:
            ok (bool): True f the rener was succesful
            fname (str): Name of the file being rendered
            error (str): Error string to display
        """
        self.spinner.stop()
        if error is not None:
            self.status_text.setText(error)
            self.close_tab(self.filenames.index(fname))
        else:
            self.progress_bar.hide()

    def close_tab(self, index):
        """Close tab, and remove its widget form renderviews."""
        fname = self.filenames.pop(index)
        self.renderviews.pop(fname)
        self.tabs.removeTab(index)

    def move_tab(self, start, end):
        """Move self.filenames list to be synchronized when tabs are moved."""
        if start < 0 or end < 0:
            return
        steps = abs(end - start)
        direction = (end - start) // steps  # +1 for right, -1 for left

        fnames = self.filenames
        for i in range(start, end, direction):
            fnames[i], fnames[i + direction] = fnames[i + direction], fnames[i]

    def disambiguate_fname(self, fname):
        """Generate a file name without ambiguation."""
        files_path_list = [filename for filename in self.filenames if filename]
        return disambiguate_fname(files_path_list, fname)

    def get_focus_report(self):
        """Return current report."""
        try:
            return self.filenames[self.tabs.currentIndex()]
        except IndexError:
            return None


def test():  # pragma: no cover
    """Run Find in Files widget test."""
    from spyder.utils.qthelpers import qapplication
    import sys
    app = qapplication()
    widget = ReportsWidget(None)
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test()
