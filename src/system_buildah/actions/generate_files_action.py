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
GenerateFilesAction CLI Action.
"""

import json
import os
import shutil
import subprocess
import tempfile

import jinja2


from system_buildah import util
from system_buildah.actions import SystemBuildahAction


class GenerateFilesAction(SystemBuildahAction):
    """
    Creates new system image files.
    """

    def _create_manifest(self, namespace, parser):
        """
        Creates the manifest structure based on input.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :returns: manifest structure
        :rtype: dict
        """
        manifest = {
            "version": "1.0",
            "defaultValues": {},
        }

        for item in namespace.default:
            try:
                k, v = item.split('=')
                manifest['defaultValues'][k] = v
            except ValueError as error:
                parser._print_message(
                    '{} not in a=b format. Skipping...'.format(item))
        return manifest

    def _render_service_template(self, namespace):
        """
        Renders and returns the service template.

        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :returns: Rendered template
        :rtype: str
        """
        loader = jinja2.PackageLoader('system_buildah')
        return loader.load(
            jinja2.Environment(), 'service.template.j2').render(
                description=namespace.description)

    def _render_init_template(self, namespace):
        """
        Renders and returns the init.sh.

        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :returns: Rendered template
        :rtype: str
        """
        loader = jinja2.PackageLoader('system_buildah')
        return loader.load(
            jinja2.Environment(), 'init.sh.j2').render()

    def _generate_ocitools_command(self, namespace, parser):
        """
        Generates and returns the ocitools command for execution.

        :name parser: The argument parser in use.
        :type parser: argparse.ArgumentParser
        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        :returns: The ocitools command to execute
        :rtype: list
        """
        ocitools_cmd = ['ocitools', 'generate', "--read-only"]
        if namespace.config:
            for item in namespace.config.split(' '):
                try:
                    item.index('=')
                    ocitools_cmd = ocitools_cmd + item.split('=')
                except ValueError as error:
                    parser._print_message(
                        '{} not in a=b format. Skipping...'.format(item))
        return ocitools_cmd

    def run(self, parser, namespace, values, dest, option_string=None):
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
        manifest_struct = self._create_manifest(namespace, parser)

        # Generate the manifest.json
        manifest_out = os.path.sep.join([output, 'manifest.json'])
        with open(manifest_out, 'w') as manifest:
            json.dump(manifest_struct, manifest, indent=8)

        # Generate the service.template
        rendered = self._render_service_template(namespace)
        service_out = os.path.sep.join([output, 'service.template'])
        with open(service_out, 'w') as service:
            service.write(rendered)

        # Generate the init.sh file
        rendered_init = self._render_init_template(namespace)
        init_out = os.path.sep.join([output, 'init.sh'])
        with open(init_out, 'w') as init:
            init.write(rendered_init)

        # Generate config.json using ocitools
        temp_dir = tempfile.mkdtemp()
        ocitools_cmd = self._generate_ocitools_command(namespace, parser)
        with util.pushd(temp_dir):
            try:
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
