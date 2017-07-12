# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Plugin."""

# Standard library imports
import codecs
import os.path as osp

# Third party imports
from pweave import Pweb
from qtpy.QtCore import QUrl
from qtpy.QtWidgets import QVBoxLayout

# Spyder-IDE and Local imports
from spyder.utils.qthelpers import create_action

from .widgets.reportsgui import ReportsWidget

try:
    from spyder.api.plugins import SpyderPluginWidget
except ImportError:
    from spyder.plugins import SpyderPluginWidget  # Spyder 3 compatibility


class ReportsPlugin(SpyderPluginWidget):
    """Reports plugin."""

    CONF_SECTION = 'reports'
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent=None):
        """
        Initialize main widget.

        Create a basic layout and add ReportWidget.
        """
        SpyderPluginWidget.__init__(self, parent)
        self.main = parent  # Spyder 3 compatibility

        # Create widget and add to dockwindow
        self.report_widget = ReportsWidget(self.main)
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
        """Call report rendering and displays its output."""
        editorstack = self.main.editor.get_current_editorstack()
        if editorstack.save():
            fname = osp.abspath(self.main.editor.get_current_filename())
            output_file = self.render_report(fname)
            if output_file is None:
                return
            html = ""
            with codecs.open(output_file, encoding="utf-8") as file:
                html = file.read()

            base_url = QUrl()
            name = osp.basename(output_file)
            self.report_widget.set_html(html, name, base_url)

        self.switch_to_plugin()

    def render_report(self, file):
        """
        Parse report document using pweave.

        Args:
            file: Path of the file to be parsed.

        Return:
            Output file path
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

        return doc.sink
