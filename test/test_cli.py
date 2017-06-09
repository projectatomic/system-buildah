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
import os
import subprocess
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah import cli


def test_TarAction(monkeypatch):
    """Verify TarAction runs the proper command"""
    image = 'a:a'
    tar = 'a-a.tar'
    def assert_call(args):
        assert args == ['docker', '--tlsverify', '--host=example.org', 'save', '-o', tar, image]

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    cli.TarAction('', '').__call__('', argparse.Namespace(host='example.org', tlsverify=True), image)


def test_BuildAction(monkeypatch):
    """Verify BuildAction runs the proper command"""
    tag = 'a'
    def assert_call(args):
        assert args == ['docker', '--tlsverify', '--host=example.org', 'build', '-t', tag, '.']

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    cli.BuildAction('', '').__call__('', argparse.Namespace(path='.', host='example.org', tlsverify=True), tag, '')


def test_GenerateDockerfileAction(tmpdir):
    """Verify GenerateDockerfile writes the expected file"""
    tmp = tmpdir.dirname
    file_path = os.path.sep.join([tmp, 'Dockerfile'])
    input = argparse.Namespace(
        output=tmp,
        from_base='from_base',
        maintainer='maintainer', license='license',
        summary='summary', version='version', help_text='help_text',
        architecture='architecture', scope='scope', add_file=[])
    cli.GenerateDockerfileAction('', '').__call__('', input, 'name', '')
    # Verify the file exists
    assert os.path.isfile(file_path)

    # Make sure we have expected items in the file
    with open(file_path, 'r') as _file:
        data = _file.read()
        for k, v in input.__dict__.items():
            # Rename help_text to help
            if k == 'help_text':
                k = 'help'
            # from_base is for the FROM
            elif k == 'from_base':
                assert 'FROM {}'.format(v) in data
                continue
            # output isn't used inside the file so continue
            elif k in ['output', 'add_file']:
                continue
            assert '{}="{}"'.format(k, v) in data
