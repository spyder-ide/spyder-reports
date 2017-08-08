# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
#
"""Tests for the plugin."""

# Third party imports
import pytest
import os.path as osp

# Spyder-IDE and Local imports
from spyder.utils.programs import TEMPDIR
from spyder_reports.reportsplugin import ReportsPlugin


@pytest.fixture
def setup_reports(qtbot):
    """Set up the Reports plugin."""
    reports = ReportsPlugin(None)
    qtbot.addWidget(reports)
    reports.show()
    return reports


@pytest.fixture(scope='session', params=['mdw', 'md'])
def report_file(request, tmpdir_factory):
    """
    Fixture for create a temporary report file.

    Returns:
        str: Path of temporary report file.
    """
    report_file = tmpdir_factory.mktemp('data').join(
            "'test_report.{}".format(request.param))
    report_file.write('# This is a Markdown report')
    return str(report_file)


def test_basic_initialization(qtbot):
    """Test Reports plugin initialization."""
    reports = setup_reports(qtbot)

    # Assert that reports exist
    assert reports is not None


def test_basic_render(qtbot, report_file):
    """Test rendering of an basic .mdw report returning a .html file."""
    reports = setup_reports(qtbot)
    output_file = reports._render_report(report_file)

    # Assert that output_file is an html file
    assert output_file.split('.')[-1] == 'html'


def test_check_compability(qtbot, monkeypatch):
    """Test state and message returned by check_compatibility."""
    monkeypatch.setattr('spyder_reports.reportsplugin.PYQT4', True)
    monkeypatch.setattr('spyder_reports.reportsplugin.PY3', False)

    reports = setup_reports(qtbot)

    valid, message = reports.check_compatibility()
    assert not valid
    assert 'qt4' in message.lower()
    assert 'python2' in message.lower()


def test_run_reports_render(qtbot, report_file, monkeypatch):
    """Test rendering a report when calling it from menu entry."""
    reports = setup_reports(qtbot)

    class EditorStackMock():
        def save(self):
            return True

    class EditorMock():
        def get_current_editorstack(self):
            return EditorStackMock()

        def get_current_filename(self):
            return report_file

    class MainMock():
        editor = EditorMock()

    def switch_to_plugin():
        pass

    # patch reports object with mock MainWindow
    reports.main = MainMock()
    reports.switch_to_plugin = switch_to_plugin

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        reports.run_reports_render()

    ok, filename, error = sig.args
    assert ok
    assert error is None
    assert osp.exists(filename)

    renderview = reports.report_widget.renderviews.get(report_file)
    assert renderview is not None


def test_render_report_thread(qtbot, report_file):
    """Test rendering report in a worker thread."""
    reports = setup_reports(qtbot)

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        with qtbot.waitSignal(reports.sig_render_started):
            reports.render_report_thread(report_file)

        # Assert that progress bar was shown
        assert reports.report_widget.progress_bar.isVisible()
        assert 'Rendering' in reports.report_widget.status_text.text()

    ok, filename, error = sig.args
    assert ok
    assert error is None
    assert osp.exists(filename)

    # Assert that progress bar was hidden
    assert not reports.report_widget.progress_bar.isVisible()

    renderview = reports.report_widget.renderviews.get(report_file)
    assert renderview is not None


def test_render_report_thread_error(qtbot):
    """Test rendering report in a worker thread."""
    reports = setup_reports(qtbot)

    with qtbot.waitSignal(reports.sig_render_finished, timeout=5000) as sig:
        reports.render_report_thread('file_that_doesnt_exist.mdw')

    ok, filename, error = sig.args
    assert not ok
    assert "[Errno 2]" in error
    assert filename == 'file_that_doesnt_exist.mdw'

    def tab_closed():
        assert reports.report_widget.tabs.count() == 0

    qtbot.waitUntil(tab_closed)
    for renderview in reports.report_widget.renderviews:
        assert 'file_that_doesnt_exist' not in renderview

    # Assert that progress bar shows the error
    assert reports.report_widget.progress_bar.isVisible()
    assert error in reports.report_widget.status_text.text()


def test_render_tmp_dir(qtbot, report_file):
    """Test that rendered files are created in spyder's tempdir."""
    reports = setup_reports(qtbot)
    output_file = reports._render_report(report_file)

    # Test that outfile is in spyder tmp dir
    assert osp.samefile(osp.commonprefix([output_file, TEMPDIR]), TEMPDIR)


def test_render_same_file(qtbot, report_file):
    """Test that re-rendered files are created in the same tempdir."""
    reports = setup_reports(qtbot)

    output_file1 = reports._render_report(report_file)
    output_file2 = reports._render_report(report_file)

    assert osp.exists(output_file2)
    # Assert that file has been re-rendered in the same path
    assert osp.samefile(output_file1, output_file2)


if __name__ == "__main__":
    pytest.main()
