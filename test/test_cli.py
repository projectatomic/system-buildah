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
import subprocess
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah import cli

# Args that should be used with ever namespace for tests
GLOBAL_NAMESPACE_KWARGS = {
    'manager': 'moby',
}


def test_SystemBuildahAction__setup_logger(monkeypatch):
    """Verify SystemBuildahAction__setup_logger sets the logger level"""
    ns = argparse.Namespace(log_level='debug', **GLOBAL_NAMESPACE_KWARGS)

    def assert_call(level):
        assert level == logging.DEBUG

    monkeypatch.setattr(logging, 'basicConfig', assert_call)

    result = cli.SystemBuildahAction('', '')._setup_logger(ns)


def test_GenerateFilesAction__render_service_template(monkeypatch):
    """Verify GenerateFiles__render_service_template renders"""
    ns = argparse.Namespace(description='testing', **GLOBAL_NAMESPACE_KWARGS)

    result = cli.GenerateFilesAction('', '')._render_service_template(ns)
    assert type(result) is str
    assert '\nDescription=testing\n' in result


def test_GenerateFilesAction__render_init_template(monkeypatch):
    """Verify GenerateFiles__render_init_template renders"""
    ns = argparse.Namespace(**GLOBAL_NAMESPACE_KWARGS)

    result = cli.GenerateFilesAction('', '')._render_init_template(ns)
    assert type(result) is str
    assert '#!/bin/bash' in result


def test_GenerateFilesAction_create_manifest(monkeypatch):
    """Verify GenerateFiles_create_manifest returns proper data"""
    ns = argparse.Namespace(
        default=['a=a', 'b=c', 'skipped'], **GLOBAL_NAMESPACE_KWARGS)
    parser = argparse.ArgumentParser()

    def assert_call(arg):
        assert 'skipped' in arg

    monkeypatch.setattr(parser, '_print_message', assert_call)

    result = cli.GenerateFilesAction('', '')._create_manifest(ns, parser)
    assert result['defaultValues'].get('a') == 'a'
    assert result['defaultValues'].get('b') == 'c'
    assert 'skipped' not in result['defaultValues']


def test_GenerateFilesAction__generate_ocitools_command(monkeypatch):
    """
    Verify GenerateFiles__generate_ocitools_command returns proper a command
    """
    ns = argparse.Namespace(
        config='--key=value --second=one ignore',
        **GLOBAL_NAMESPACE_KWARGS)
    parser = argparse.ArgumentParser()

    def assert_call(arg):
        assert 'ignore' in arg
        assert 'Skipping' in arg

    monkeypatch.setattr(parser, '_print_message', assert_call)
    cmd = [
        'ocitools', 'generate', '--read-only',
        '--key', 'value', '--second', 'one']

    result = cli.GenerateFilesAction('', '')._generate_ocitools_command(ns, parser)
    assert result == cmd


def test_TarAction(monkeypatch):
    """Verify TarAction runs the proper command"""
    image = 'a:a'
    tar = 'a-a.tar'
    def assert_call(args):
        assert args == [
            'docker', '--tlsverify', '--host=example.org',
            'save', '-o', tar, image]

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    cli.TarAction('', '').run(
        '', argparse.Namespace(
            host='example.org', tlsverify=True,
            **GLOBAL_NAMESPACE_KWARGS),
        image)


def test_BuildAction(monkeypatch):
    """Verify BuildAction runs the proper command"""
    tag = 'a'
    def assert_call(args):
        assert args == [
            'docker', '--tlsverify', '--host=example.org',
            'build', '-t', tag, '.']

    monkeypatch.setattr(subprocess, 'check_call', assert_call)
    cli.BuildAction('', '').run(
        '', argparse.Namespace(
            path='.', host='example.org', tlsverify=True,
            **GLOBAL_NAMESPACE_KWARGS),
        tag, '')


def test_GenerateDockerfileAction(tmpdir):
    """Verify GenerateDockerfile writes the expected file"""
    tmp = tmpdir.dirname
    file_path = os.path.sep.join([tmp, 'Dockerfile'])
    input = argparse.Namespace(
        output=tmp,
        from_base='from_base',
        maintainer='maintainer', license='license',
        summary='summary', version='version', help_text='help_text',
        architecture='architecture', scope='scope', add_file=[],
        **GLOBAL_NAMESPACE_KWARGS)
    cli.GenerateDockerfileAction('', '').run('', input, 'name', '')
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
            elif k in ['output', 'add_file', 'manager']:
                continue
            assert '{}="{}"'.format(k, v) in data
