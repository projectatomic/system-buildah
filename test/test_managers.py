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

import argparse
import os
import subprocess
import sys

import pytest

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah import managers, util
from system_buildah.managers.buildah import Manager as BuildahManager
from system_buildah.managers.moby import Manager as MobyManager


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



def test_MobyManager_tar(monkeypatch):
    """
    Test the Moby manager tar command.
    """
    mm = MobyManager()

    def assert_call(arg):
        assert arg == ['docker', 'save', '-o', 'output.tar', 'output']

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    mm.tar(argparse.Namespace(host=None, tlsverify=None), 'output')


def test_MobyManager_build(monkeypatch):
    """
    Test the Moby manager tar command.
    """
    mm = MobyManager()

    def assert_call(arg):
        assert arg == ['docker', 'build', '-t', 'tag', '.']

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    mm.build(argparse.Namespace(host=None, tlsverify=None, path='.'), 'tag')


def test_BuildahManager_tar(monkeypatch):
    """
    Test the Buildah manager tar command.
    """
    bm = BuildahManager()
    output = 'output:latest'

    def assert_call(arg):
        # First call is a buildah push
        if arg[0] == 'buildah':
            assert arg[0:3] == ['buildah', 'push', output]
        # Anything else is totally unexpected
        else:
            pytest.fail(
                'Unexpected input to subprocess.check_call: {}'.format(arg))

    def assert_rename(src, dest):
        assert src == 'output'
        assert dest == 'output-latest.tar'

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    monkeypatch.setattr(os, 'rename', assert_rename)
    bm.tar(argparse.Namespace(host=None, tlsverify=None), output)


def test_BuildahManager_build(monkeypatch):
    """
    Test the Buildah manager tar command.
    """
    bm = BuildahManager()

    def assert_call(arg):
        assert arg == ['buildah', 'bud', '-t', 'tag', '.']

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    bm.build(argparse.Namespace(host=None, tlsverify=None, path='.'), 'tag')
