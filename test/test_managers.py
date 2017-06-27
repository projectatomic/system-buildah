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
Tests for managers.
"""

import os
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah import managers


# Dummy manager to test with
class IM(managers.ImageManager):
    tar = build = lambda s: s


def test_ImageManager_normalize_filename():
    """Verify normalize_filename replaces expected chars"""
    im = IM()
    for tc in (
            {'raw': 'some/test:file', 'expected': 'some-test-file'},
            {'raw': 'some:file', 'expected': 'some-file'},
            {'raw': 'some/test', 'expected': 'some-test'}):
        assert im._normalize_filename(tc['raw']) == tc['expected']
