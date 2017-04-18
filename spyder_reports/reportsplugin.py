# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Plugin."""

from qtpy.QtWidgets import QVBoxLayout

try:
    from spyder.api.plugins import SpyderPluginWidget
except ImportError:
    from spyder.plugins import SpyderPluginWidget # Spyder 3 compatibility

from .widgets.reportsgui import ReportsWidget


class ReportsPlugin(SpyderPluginWidget):
    """Reports plugin."""

    CONF_SECTION = 'reports'
    CONFIGWIDGET_CLASS = None

    def __init__(self, parent=None):
        SpyderPluginWidget.__init__(self, parent)
        self.main = parent # Spyder 3 compatibility

        # Create widget and add to dockwindow
        self.widget = ReportsWidget(self.main)
        layout = QVBoxLayout()
        layout.addWidget(self.widget)
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

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.help, self)

    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings."""
        pass
