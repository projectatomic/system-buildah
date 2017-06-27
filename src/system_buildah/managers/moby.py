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
Moby/Docker specific manager.
"""

import subprocess

from system_buildah import managers, util


class Manager(managers.ImageManager):
    """
    Works with moby/docker.
    """

    def _additional_switches(self, namespace, command):
        """
        Adds additional switches to the moby/docker command.

        :param namespace: namespace passed in via cli.
        :type namespace: argparse.namespace
        :param command: Command to execute as a list
        :type command: list(str, str,...)
        """
        if namespace.host:
            command.insert(1, '--host={}'.format(namespace.host))
        if namespace.tlsverify:
            command.insert(1, '--tlsverify')
        return command

    def build(self, namespace, tag):
        """
        Builds a specific image.

        :param namespace: namespace passed in via cli.
        :type namespace: argparse.namespace
        :param tag: The tag to use when building.
        :type tag: str
        :raises: subprocess.CalledProcessError
        """
        command = self._additional_switches(
            namespace,
            ['docker', 'build', '-t', tag, '.'])

        with util.pushd(namespace.path):
            subprocess.check_call(command)

    def tar(self, namespace, output):
        """
        Exports a specific image to a tar file.

        :param namespace: Namespace passed in via CLI.
        :type namespace: argparse.Namespace
        :param output: The name of the file to output.
        :type output: str
        :raises: subprocess.CalledProcessError
        """
        tar = '{}.tar'.format(output.replace(':', '-').replace('/', '-'))

        command = self._additional_switches(
            namespace,
            ['docker', 'save', '-o', tar, output])

        subprocess.check_call(command)
