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
Tar CLI action.
"""

from system_buildah import util
from system_buildah.actions import SystemBuildahAction


class TarAction(SystemBuildahAction):
    """
    Exports an image as a tar file.
    """

    def run(self, parser, namespace, values, option_string=None):
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
        builder = util.get_manager_class(namespace.manager)()
        builder.tar(namespace, values)
