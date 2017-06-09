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
System Container build tool.
"""

import argparse
import json
import os
import shutil
import subprocess
import tempfile

import jinja2

from system_buildah import util


class GenerateFilesAction(argparse.Action):
    """
    Creates new system container files.
    """

    def __call__(self, parser, namespace, values, dest, option_string=None):
        """
        Execution of the action.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :name values: Values for the action.
        :type values: mixed
        :name option_string: Option string.
        :type option_string: str or None
        :raises: subprocess.CalledProcessError
        """
        output = util.mkdir(values)
        manifest_struct = {
            "version": "1.0",
            "defaultValues": {},
        }
        for item in namespace.default:
            try:
                k, v = item.split('=')
                manifest_struct['defaultValues'][k] = v
            except ValueError as error:
                parser._print_message(
                    '{} not in a=b format. Skipping...'.format(item))

        # Generate the manifest.json
        manifest_out = os.path.sep.join([output, 'manifest.json'])
        with open(manifest_out, 'w') as manifest:
            json.dump(manifest_struct, manifest, indent='    ')

        # Generate the service.template
        service_out = os.path.sep.join([output, 'service.template'])
        with open(service_out, 'w') as service:
            loader = jinja2.PackageLoader('system_buildah')
            rendered = loader.load(
                jinja2.Environment(), 'service.template.j2').render(
                    description=namespace.description)
            service.write(rendered)

        # Generate config.json using ocitools
        temp_dir = tempfile.mkdtemp()
        with util.pushd(temp_dir):
            try:
                ocitools_cmd = ['ocitools', 'generate', "--read-only"]
                for item in namespace.config.split(' '):
                    try:
                        ocitools_cmd = ocitools_cmd + item.split('=')
                    except ValueError as error:
                        parser._print_message(
                            '{} not in a=b format. Skipping...'.format(item))
                subprocess.check_call(ocitools_cmd)
                config_out = os.path.sep.join([output, 'config.json.template'])
                try:
                    with open('config.json', 'r') as config_file:
                        configuration = json.load(config_file)
                        configuration['process']['terminal'] = False
                    with open(config_out, 'w') as dest:
                        json.dump(
                            configuration, dest, indent=8, sort_keys=True)
                finally:
                    os.unlink('config.json')
            finally:
                shutil.rmtree(temp_dir)


class GenerateDockerfileAction(argparse.Action):
    """
    Creates a new Dockerfile.
    """

    def __call__(self, parser, namespace, values, dest, option_string=None):
        """
        Execution of the action.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :name values: Values for the action.
        :type values: mixed
        :name option_string: Option string.
        :type option_string: str or None
        :raises: subprocess.CalledProcessError
        """
        hostfs_dirs = []
        add_files = {}
        for item in namespace.add_file:
            local, host = item.split('=')
            hostfs_dirs.append(os.path.dirname(host))
            add_files[local] = host

        output = util.mkdir(namespace.output)
        with open(os.path.sep.join([output, 'Dockerfile']), 'w') as dockerfile:
            loader = jinja2.PackageLoader('system_buildah')
            rendered = loader.load(
                jinja2.Environment(), 'Dockerfile.j2').render(
                    from_base=namespace.from_base, name=values,
                    maintainer=namespace.maintainer,
                    license_name=namespace.license, summary=namespace.summary,
                    version=namespace.version, help_text=namespace.help_text,
                    architecture=namespace.architecture, scope=namespace.scope,
                    add_files=add_files, hostfs_dirs=set(hostfs_dirs))
            dockerfile.write(rendered)


class BuildAction(argparse.Action):
    """
    Builds a new system container image.
    """

    def __call__(self, parser, namespace, values, dest, option_string=None):
        """
        Execution of the action.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :name values: Values for the action.
        :type values: mixed
        :name option_string: Option string.
        :type option_string: str or None
        :raises: subprocess.CalledProcessError
        """
        path = namespace.path
        tag = values
        command = ['docker', 'build', '-t', tag, '.']

        if namespace.host:
            command.insert(1, '--host={}'.format(namespace.host))
        if namespace.tlsverify:
            command.insert(1, '--tlsverify')
        with util.pushd(path):
            subprocess.check_call(command)


class TarAction(argparse.Action):
    """
    Exports an image as a tar file.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        """
        Execution of the action.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :name values: Values for the argument calling the action.
        :type values: mixed
        :name option_string: Option string.
        :type option_string: str or None
        :raises: subprocess.CalledProcessError
        """
        tar = '{}.tar'.format(values.replace(':', '-'))
        command = ['docker', 'save', '-o', tar, values]
        if namespace.host:
            command.insert(1, '--host={}'.format(namespace.host))
        if namespace.tlsverify:
            command.insert(1, '--tlsverify')

        subprocess.check_call(command)


def main():  # pragma: no cover
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        title='commands', description='commands')

    # generate-files command
    files_command = subparsers.add_parser(
        'generate-files',
        help='Generates manifest.json, config.template, and service.template')
    files_command.add_argument(
        '-d', '--description',
        default='UNKNOWN', help='Description of container')
    files_command.add_argument(
        '-c', '--config', default='',
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
        'generate-dockerfile', help='Generate a new Dockerfile')
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
        help='Name for the new system container image',
        action=GenerateDockerfileAction)

    # build command
    build_command = subparsers.add_parser(
        'build', help='Builds a new system container image')
    build_command.add_argument(
        '-H', '--host', help='Remote Docker host to connect to')
    build_command.add_argument(
        '--tlsverify', action="store_true", help='Enable TLS Verification')
    build_command.add_argument(
        '-p', '--path', default='.', help='Path to the Dockerfile directory')
    build_command.add_argument(
        'tag', help='Tag for the new image', action=BuildAction)

    # tar command
    tar_command = subparsers.add_parser(
        'tar', help='Exports an image as a tar file')
    tar_command.add_argument(
        'image', help='Name of the image', action=TarAction)
    tar_command.add_argument(
        '-H', '--host', help='Remote Docker host to connect to')
    tar_command.add_argument(
        '--tlsverify', action="store_true", help='Enable TLS Verification')

    try:
        parser.parse_args()
    except subprocess.CalledProcessError as error:
        parser.error('Unable to execute command: {}'.format(error))
    raise SystemExit


if __name__ == '__main__':
    main()
