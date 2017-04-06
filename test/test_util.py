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
import shutil

from syscontainer_build import util


def test__expand_path():
    """Verify _expand_path expands to proper paths"""
    assert util._expand_path('/') == '/'
    assert util._expand_path('/tmp/../tmp/../usr') == '/usr'
    home_path = util._expand_path('~')
    assert home_path[0] == '/'


def test_mkdir():
    """Verify mkdir creates directories"""
    dir = '/tmp/syscontainerbuildtest'
    try:
        assert util.mkdir(dir) == dir  # New directory
        assert util.mkdir(dir) == dir  # Already exists
    finally:
        # Clean up
        shutil.rmtree(dir)


def test_pushd():
    """Verify pushd acts like pushd in the shell"""
    original_cwd = os.getcwd()
    dir = '/tmp'
    popd = util.pushd(dir)
    assert callable(popd)  # We must get a callable
    assert os.getcwd() == dir  # We should have moved to dir
    popd()
    assert os.getcwd() == original_cwd  # Now back to the original
