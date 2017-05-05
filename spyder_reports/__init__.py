# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Spyder Reports Plugin."""

from ._version import __version__
from .reportsplugin import ReportsPlugin

# The following statements are required to register this 3rd party plugin:

PLUGIN_CLASS = ReportsPlugin
