# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Plugin."""

from pweave import Pweb
import codecs

from qtpy.QtCore import QUrl
from qtpy.QtWidgets import QVBoxLayout

try:
    from spyder.api.plugins import SpyderPluginWidget
except ImportError:
    from spyder.plugins import SpyderPluginWidget  # Spyder 3 compatibility

from spyder.utils.qthelpers import create_action

from .widgets.reportsgui import ReportsWidget


class ReportsPlugin(SpyderPluginWidget):
    """Reports plugin."""

    CONF_SECTION = 'reports'
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent=None):
        SpyderPluginWidget.__init__(self, parent)
        self.main = parent  # Spyder 3 compatibility

        # Create widget and add to dockwindow
        self.report_widget = ReportsWidget(self.main)
        self.report_widget.clear()
        layout = QVBoxLayout()
        layout.addWidget(self.report_widget)
        self.setLayout(layout)

        # Initialize plugin
        self.initialize_plugin()

    # --- SpyderPluginWidget API ----------------------------------------------
    def get_plugin_title(self):
        """Return widget title."""
        return "Reports"

    def refresh_plugin(self):
        """Refresh Reports widget."""
        pass

    def get_plugin_actions(self):
        """Return a list of actions related to plugin."""
        return []

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        self.main.add_dockwidget(self)

        reports_act = create_action(self,
                                    "Render report to HTML ",
                                    icon=self.get_plugin_icon(),
                                    triggered=self.run_reports_render)

        self.main.run_menu_actions += [reports_act]

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.help, self)

    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings."""
        pass

    # -------------------------------------------------------------------------

    def run_reports_render(self):
        self.update_html(self.main.editor.get_current_filename())

    def update_html(self, file):
        """
        Parse report document and dysplays it.

        Args:
            file: Path of the file to be parsed.
        """
        doc = Pweb(file)

        # TODO Add more formats support
        if doc.file_ext == '.mdw':
            doc.setformat('md2html', theme="skeleton")
        elif doc.file_ext == '.md':
            doc.setformat('pandoc2html')
        else:
            print("Format not supported ({})".format(doc.file_ext))
            return

        doc.detect_reader()

        doc.parse()
        doc.run(shell="ipython")
        doc.format()
        doc.write()

        output_file = doc.sink

        html = ""
        with codecs.open(output_file, encoding="utf-8") as f:
            html = f.read()

        base_url = QUrl()
        self.report_widget.set_html(html, base_url)
