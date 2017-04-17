# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Reports Widget."""

from qtpy.QtWidgets import QWidget

class ReportsWidget(QWidget):
    """Reports widget."""
    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.setWindowTitle("Reports")
