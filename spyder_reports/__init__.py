# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Spyder Reports Plugin."""

from ._version import __version__

# The following statements are required to register this 3rd party plugin:

from .reportsplugin import ReportsPlugin

PLUGIN_CLASS = ReportsPlugin
