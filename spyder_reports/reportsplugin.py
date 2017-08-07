# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Plugin."""

# Standard library imports
import os
import os.path as osp
import uuid

# Third party imports
from pweave import Pweb, __version__ as pweave_version
from qtpy import PYQT4, PYSIDE
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QVBoxLayout, QMessageBox

# Spyder-IDE and Local imports
from spyder.py3compat import PY3
from spyder.utils.programs import TEMPDIR
from spyder.utils.qthelpers import create_action
from spyder.utils.workers import WorkerManager

from .widgets.reportsgui import ReportsWidget

try:
    from spyder.api.plugins import SpyderPluginWidget
except ImportError:
    from spyder.plugins import SpyderPluginWidget  # Spyder 3 compatibility

REPORTS_TEMPDIR = osp.join(TEMPDIR, 'reports')


class ReportsPlugin(SpyderPluginWidget):
    """Reports plugin."""

    CONF_SECTION = 'reports'
    CONFIGWIDGET_CLASS = None
    sig_render_started = Signal(str)  # input filename

    # Success, output filename(str), error(str)
    # When an error happened returns input filename instead
    sig_render_finished = Signal(bool, object, object)

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

        self.sig_render_started.connect(self.report_widget.show_progress)
        self.sig_render_finished.connect(self.report_widget.render_finished)

        # This worker runs in a thread to avoid blocking when rendering
        # a report
        self._worker_manager = WorkerManager()

        # Dict to save output files to regenerate files in the same tmpdir
        self._output_tmpfile = {}

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

        # Render welcome.md in a temp location
        welcome_path = osp.join(osp.dirname(__file__), 'utils', 'welcome.md')
        self.render_report_thread(welcome_path)

    def on_first_registration(self):
        """Action to be performed on first plugin registration."""
        self.main.tabify_plugins(self.main.help, self)

    def apply_plugin_settings(self, options):
        """Apply configuration file's plugin settings."""
        pass

    def check_compatibility(self):
        """
        Check plugin requirements.

        - python version is greater or equal to 3.
        - PyQt version is greater or equal to 5.
        """
        messages = []
        valid = True
        if not PY3:
            messages.append('Spyder-reports does not work with Python2')
            valid = False
        if PYQT4 or PYSIDE:
            messages.append('Spyder-reports does not work with Qt4')
            valid = False
        return valid, ", ".join(messages)

    # -------------------------------------------------------------------------

    def check_create_tmp_dir(self, folder):
        """Create temp dir if it does not exists."""
        if not os.path.exists(folder):
            os.makedirs(folder)

    def show_error_message(self, message):
        """Show error message."""
        messageBox = QMessageBox(self)
        messageBox.setWindowModality(Qt.NonModal)
        messageBox.setAttribute(Qt.WA_DeleteOnClose)
        messageBox.setWindowTitle('Render Report Error')
        messageBox.setText(message)
        messageBox.setStandardButtons(QMessageBox.Ok)
        messageBox.show()

    def run_reports_render(self):
        """Call report rendering and displays its output."""
        editorstack = self.main.editor.get_current_editorstack()
        if editorstack.save():
            fname = osp.abspath(self.main.editor.get_current_filename())
            self.render_report_thread(fname)
        self.switch_to_plugin()

    def render_report_thread(self, file_name):
        """Render report in a thread and update the widget when finished."""
        def worker_output(worker, output_file, error):
            """Receive the worker output, and update the widget."""
            if error is None and output_file:
                self.report_widget.set_html_from_file(output_file, file_name)
                self.sig_render_finished.emit(True, output_file, None)
            else:
                self.show_error_message(str(error))
                self.sig_render_finished.emit(False, file_name, str(error))

        # Before starting a new worker process make sure to end previous
        # incarnations
        self._worker_manager.terminate_all()

        worker = self._worker_manager.create_python_worker(
            self._render_report,
            file_name,
        )
        worker.sig_finished.connect(worker_output)
        self.sig_render_started.emit(file_name)
        worker.start()

    def _render_report(self, file, output=None):
        """
        Parse report document using pweave.

        Args:
            file: Path of the file to be parsed.

        Return:
            Output file path
        """
        if output is None:
            output = self._output_tmpfile.get(file)
            if output is None:
                name = osp.splitext(osp.basename(file))[0]
                id_ = str(uuid.uuid4())
                output = osp.join(REPORTS_TEMPDIR, id_, '{}.html'.format(name))
                self._output_tmpfile[file] = output

        folder = osp.split(output)[0]
        self.check_create_tmp_dir(folder)
        doc = Pweb(file, output=output)

        # TODO Add more formats support
        if doc.file_ext == '.mdw':
            _format = 'md2html'
        elif doc.file_ext == '.md':
            _format = 'pandoc2html'
        else:
            print("Format not supported ({})".format(doc.file_ext))
            return

        if pweave_version.startswith('0.3'):
            doc.read()
            doc.run()
            doc.format(doctype=_format)
            doc.write()
            return doc.sink
        else:
            doc.setformat(_format)
            doc.detect_reader()
            doc.parse()
            doc.run(shell="ipython")
            doc.format()
            doc.write()
            return doc.sink
