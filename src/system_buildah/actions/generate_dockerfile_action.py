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
GenerateDockerfile Action.
"""

import os

import jinja2

from system_buildah import util
from system_buildah.actions import SystemBuildahAction


class GenerateDockerfileAction(SystemBuildahAction):
    """
    Creates a new Dockerfile.
    """

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
