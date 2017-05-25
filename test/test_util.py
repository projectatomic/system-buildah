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
Tests for the util module.
"""

import os
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah import util


def test__expand_path():
    """Verify _expand_path expands to proper paths"""
    assert util._expand_path('/') == '/'
    assert util._expand_path('/tmp/../tmp/../usr') == '/usr'
    home_path = util._expand_path('~')
    assert home_path[0] == '/'


def test_mkdir(tmpdir):
    """Verify mkdir creates directories"""
    path = tmpdir.mkdir('mkdir').dirname
    assert util.mkdir(path) == path  # New directory
    assert util.mkdir(path) == path  # Already exists


def test_pushd(tmpdir):
    """Verify pushd acts like pushd in the shell"""
    original_cwd = os.getcwd()
    path = tmpdir.mkdir('pushd').dirname
    popd = util.pushd(path)
    assert callable(popd)  # We must get a callable
    assert os.getcwd() == path  # We should have moved to dir
    popd()
    assert os.getcwd() == original_cwd  # Now back to the original
