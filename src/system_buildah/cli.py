# Copyright (C) 2017 Red Hat
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
System Image build tool.
"""

import argparse
import logging
import platform
import subprocess

# CLI Actions
from system_buildah.actions.tar_action import TarAction
from system_buildah.actions.build_action import BuildAction
from system_buildah.actions.generate_files_action import GenerateFilesAction
from system_buildah.actions.generate_dockerfile_action import (
    GenerateDockerfileAction)


def main():  # pragma: no cover
    """
    Main entry point.
    """
    # Default to info logging
    parser = argparse.ArgumentParser()
    # Verify that we are being executed with Python 3+
    if int(platform.python_version_tuple()[0]) <= 2:
        parser.error('system-buildah requires Python 3.x')

    # Parent parser used by all commands
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        '--log-level', default='info',
        choices=('debug', 'info', 'warn', 'fatal'))
    parent_parser.add_argument(
        '--manager', default='moby', choices=('moby', 'buildah'))

    # Parent parser to use with commands that may use moby/docker
    extra_moby_switches = argparse.ArgumentParser(add_help=False)
    extra_moby_switches.add_argument(
        '-H', '--host',
        help='Remote Docker host to connect to (Docker specific)')
    extra_moby_switches.add_argument(
        '--tlsverify', action="store_true",
        help='Enable TLS Verification (Docker specific)')

    subparsers = parser.add_subparsers(
        title='commands', description='commands')

    # generate-files command
    files_command = subparsers.add_parser(
        'generate-files',
        help='Generates manifest.json, config.template, and service.template',
        parents=[parent_parser])
    files_command.add_argument(
        '-d', '--description',
        default='UNKNOWN', help='Description of image')
    files_command.add_argument(
        '-c', '--config', default=None,
        help=('Options to pass to ocitools generate. '
              'Example: -c "--cwd=/tmp --os=linux"'))
    files_command.add_argument(
        '-D', '--default',
        action='append',
        default=[],
        help='Default manifest values in the form of key=value')
    files_command.add_argument(
        'output',
        help='Path to write the new files',
        action=GenerateFilesAction)

    # generate-dockerfile command
    dockerfile_command = subparsers.add_parser(
        'generate-dockerfile', help='Generate a new Dockerfile',
        parents=[parent_parser])
    dockerfile_command.add_argument(
        '-o', '--output', default='.', help='Path to write the new Dockerfile')
    dockerfile_command.add_argument(
        '-f', '--from-base', default='centos:latest',
        help='Base image to build upon')
    dockerfile_command.add_argument(
        '-m', '--maintainer', default='UNKNOWN',
        help='Maintainer of the image')
    dockerfile_command.add_argument(
        '-l', '--license', default='UNKNOWN', help='License of the image')
    dockerfile_command.add_argument(
        '-S', '--summary', default='UNKNOWN', help='Summary of the image')
    dockerfile_command.add_argument(
        '-v', '--version', default='1', help='Version of the image')
    dockerfile_command.add_argument(
        '-H', '--help-text', default='No help', help='Help text for the image')
    dockerfile_command.add_argument(
        '-a', '--architecture', default='x86_64',
        help='Architecture of the image')
    dockerfile_command.add_argument(
        '-s', '--scope', default='private', help='Scope of the image',
        choices=[
            'private', 'authoritative-source-only', 'restricted', 'public'])
    dockerfile_command.add_argument(
        '-A', '--add-file',
        action='append',
        default=[],
        help=('Add a file to the host on install. '
              'file=/full/host/path EX: file.txt=/etc/file.txt'))
    dockerfile_command.add_argument(
        'name',
        help='Name for the new system image',
        action=GenerateDockerfileAction)

    # build command
    build_command = subparsers.add_parser(
        'build', help='Builds a new system image',
        parents=[extra_moby_switches, parent_parser])
    build_command.add_argument(
        '-p', '--path', default='.', help='Path to the Dockerfile directory')
    build_command.add_argument(
        'tag', help='Tag for the new image', action=BuildAction)

    # tar command
    tar_command = subparsers.add_parser(
        'tar', help='Exports an image as a tar file',
        parents=[extra_moby_switches, parent_parser])
    tar_command.add_argument(
        'image', help='Name of the image', action=TarAction)

    try:
        parser.parse_args()
    except subprocess.CalledProcessError as error:
        logging.debug('Stack Trace: {}'.format(error))
        parser.error('Unable to execute command: {}'.format(error))
    raise SystemExit


if __name__ == '__main__':  # pragma: no cover
    main()
