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
Tests for GenerateFilesAction.
"""

import argparse
import os
import sys

# Ensure the package is in the path
sys.path.insert(1, os.path.realpath('./src/'))

from system_buildah.actions.generate_files_action import GenerateFilesAction

from .constants import *


def test_GenerateFilesAction__render_service_template(monkeypatch):
    """Verify GenerateFiles__render_service_template renders"""
    ns = argparse.Namespace(description='testing', **GLOBAL_NAMESPACE_KWARGS)

    result = GenerateFilesAction('', '')._render_service_template(ns)
    assert type(result) is str
    assert '\nDescription=testing\n' in result


def test_GenerateFilesAction__render_init_template(monkeypatch):
    """Verify GenerateFiles__render_init_template renders"""
    ns = argparse.Namespace(**GLOBAL_NAMESPACE_KWARGS)

    result = GenerateFilesAction('', '')._render_init_template(ns)
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

    result = GenerateFilesAction('', '')._create_manifest(ns, parser)
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

    result = GenerateFilesAction('', '')._generate_ocitools_command(ns, parser)
    assert result == cmd
