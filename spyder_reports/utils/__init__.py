# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)
# -----------------------------------------------------------------------------
"""Spyder Reports Utils."""
import os.path as osp
import subprocess
from pweave import __version__ as pweave_version

WELCOME_PATH = osp.join(osp.dirname(__file__), 'templates', 'welcome.md')

PWEAVE03 = pweave_version.startswith('0.3')

PANDOC_INSTALLED = False
try:
    subprocess.call(['pandoc', '--version'])
except OSError:
    pass
else:
    PANDOC_INSTALLED = True
