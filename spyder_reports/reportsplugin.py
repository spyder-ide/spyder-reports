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
import shutil
from distutils.dir_util import copy_tree
from contextlib import redirect_stdout
from io import StringIO
from collections import defaultdict

# Third party imports
from pweave import Pweb, __version__ as pweave_version
from qtpy import PYQT4, PYSIDE
from qtpy.compat import getsavefilename, getexistingdirectory
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QVBoxLayout, QMessageBox

# Spyder-IDE and Local imports
from spyder.py3compat import PY3
from spyder.utils.programs import TEMPDIR
from spyder.utils.qthelpers import create_action
from spyder.utils.workers import WorkerManager
from spyder.utils import icon_manager as ima

from .widgets.reportsgui import ReportsWidget
from .utils import WELCOME_PATH

try:
    from spyder.api.plugins import SpyderPluginWidget
except ImportError:
    from spyder.plugins import SpyderPluginWidget  # Spyder 3 compatibility

REPORTS_TEMPDIR = osp.join(TEMPDIR, 'reports')


class CaptureStdOutput(StringIO):
    """Captures IO stream and emit a signal."""

    def __init__(self, sig_write):
        """Initialize object.

        Args:
            sig_write (Signal): signal to emit
        """
        super(CaptureStdOutput).__init__()
        self.sig_write = sig_write

    def write(self, text):
        """Emit a signal instead of writing. (Overloaded method)."""
        self.sig_write.emit(text.strip())
        return len(text)


class Report():
    """Report file.

    Save information about a rendered report

    render_tmpdir (str): Temporary dir path where the render has been saved
    save_path (str) Path where the plugin was last saved.

    TODO: Some ReportPlugin logic, as save_report, render_report could be
    moved to this class.
    """

    render_tmpdir = None
    save_path = None


class ReportsPlugin(SpyderPluginWidget):
    """Reports plugin."""

    CONF_SECTION = 'reports'
    CONFIGWIDGET_CLASS = None
    sig_render_started = Signal(str)  # input filename

    # Success, output filename(str), error(str)
    # When an error happened returns input filename instead
    sig_render_finished = Signal(bool, object, object)

    sig_render_progress = Signal(str)

    def __init__(self, parent=None):
        """
        Initialize main widget.

        Create a basic layout and add ReportWidget.
        """
        SpyderPluginWidget.__init__(self, parent)
        self.main = parent  # Spyder 3 compatibility
        self.render_action = None
        self.save_action = None
        self.save_as_action = None

        # Initialize plugin
        self.initialize_plugin()

        # Create widget and add to dockwindow
        self.report_widget = ReportsWidget(self.main, [self.save_action,
                                                       self.save_as_action])
        layout = QVBoxLayout()
        layout.addWidget(self.report_widget)
        self.setLayout(layout)

        self.sig_render_started.connect(self.report_widget.render_started)
        self.sig_render_progress.connect(self.report_widget.update_progress)
        self.sig_render_finished.connect(self.report_widget.render_finished)

        self.report_widget.tabs.currentChanged.connect(
                self.update_actions_status)

        # This worker runs in a thread to avoid blocking when rendering
        # a report
        self._worker_manager = WorkerManager()

        # Dict to save reports information:
        self._reports = defaultdict(Report)

    # --- SpyderPluginWidget API ----------------------------------------------
    def get_plugin_title(self):
        """Return widget title."""
        return "Reports"

    def refresh_plugin(self):
        """Refresh Reports widget."""
        pass

    def get_plugin_actions(self):
        """Return a list of actions related to plugin."""
        self.render_action = create_action(self,
                                           "Render report to HTML",
                                           icon=self.get_plugin_icon(),
                                           triggered=self.run_reports_render)

        self.save_action = create_action(self,
                                         "Save Report...",
                                         icon=ima.icon('filesave'),
                                         triggered=self.save_report)

        self.save_as_action = create_action(
                self,
                "Save Report as...",
                icon=ima.icon('filesaveas'),
                triggered=lambda: self.save_report(new_path=True))
        self.main.run_menu_actions += [self.render_action]

        return [self.render_action, self.save_action, self.save_as_action]

    def register_plugin(self):
        """Register plugin in Spyder's main window."""
        self.main.add_dockwidget(self)

        # Render welcome.md in a temp location
        self.render_report_thread(WELCOME_PATH)

        self.save_action.setEnabled(False)
        self.save_as_action.setEnabled(False)

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

    def update_actions_status(self):
        """Disable/enable actions, avoiding the welcome page to be saved."""
        report = self.report_widget.get_focus_report()
        enabled = report is not None and report != WELCOME_PATH

        self.save_action.setEnabled(enabled)
        self.save_as_action.setEnabled(enabled)

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

    def save_report(self, new_path=False):
        """Save report.

        If the report was already saved, save it in the same path.

        If the output are several files copy temporary dir to user
        selected directory.

        If the output is just one file copy it, to the user selected path.

        Args:
            new_path: force saving in a new path
        """
        report_filename = self.report_widget.get_focus_report()
        if report_filename is None:
            return
        report = self._reports[report_filename]

        output_filename = report.render_dir
        input_dir, _ = osp.split(report_filename)
        tmpdir, output_fname = osp.split(output_filename)

        output = None if new_path else report.save_path

        # TODO This should be improved because Pweave creates a
        # figures dir even when there isn't figures causing this
        # to evaluate always to True
        if len([name for name in os.listdir(tmpdir)]) > 1:
            # if there is more than one file save a dir
            if output is None:
                output = getexistingdirectory(parent=self,
                                              caption='Save Report',
                                              basedir=input_dir)
                if not osp.isdir(output):
                    return
                report.save_path = output
            # Using distutils instead of shutil.copytree
            # because shutil.copytree fails if the dir already exists
            copy_tree(tmpdir, output)
        else:
            if output is None:
                basedir = osp.join(input_dir, output_fname)
                output, _ = getsavefilename(parent=self,
                                            caption='Save Report',
                                            basedir=basedir)
                if not osp.isfile(output):
                    return
                report.save_path = output
            shutil.copy(output_filename, output)

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
            report = self._reports.get(file)
            if report is not None:
                output = report.render_dir
            if output is None:
                name = osp.splitext(osp.basename(file))[0]
                id_ = str(uuid.uuid4())
                output = osp.join(REPORTS_TEMPDIR, id_, '{}.html'.format(name))
                self._reports[file].render_dir = output

        folder = osp.split(output)[0]
        self.check_create_tmp_dir(folder)
        doc = Pweb(file, output=output)

        # TODO Add more formats support
        if doc.file_ext == '.mdw':
            _format = 'md2html'
        elif doc.file_ext == '.md':
            _format = 'pandoc2html'
        else:
            raise Exception("Format not supported ({})".format(doc.file_ext))

        f = CaptureStdOutput(self.sig_render_progress)

        if pweave_version.startswith('0.3'):
            with redirect_stdout(f):
                self.sig_render_progress.emit("Readign")
                doc.read()
                self.sig_render_progress.emit("Running")
                doc.run()
                self.sig_render_progress.emit("Formating")
                doc.format(doctype=_format)
                self.sig_render_progress.emit("Writing")
                doc.write()
            return doc.sink
        else:
            with redirect_stdout(f):
                doc.setformat(_format)
                doc.detect_reader()
                doc.parse()
                doc.run()
                doc.format()
                doc.write()
            return doc.sink
