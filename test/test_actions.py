# Copyright (C) 2017  Red Hat, Inc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for the cli module.
"""

import argparse
import logging
import os
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah.actions import SystemBuildahAction

from .constants import *


def test_SystemBuildahAction__setup_logger(monkeypatch):
    """Verify SystemBuildahAction__setup_logger sets the logger level"""
    ns = argparse.Namespace(log_level='debug', **GLOBAL_NAMESPACE_KWARGS)

    def assert_call(level):
        assert level == logging.DEBUG

    monkeypatch.setattr(logging, 'basicConfig', assert_call)

    result = SystemBuildahAction('', '')._setup_logger(ns)
