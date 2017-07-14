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
Package containing CLI actions.
"""

import argparse
import logging


class SystemBuildahAction(argparse.Action):
    """
    Base class for system buildah specific actions.
    """

    def _setup_logger(self, namespace):
        """
        Sets up the logger for use.

        :name namespace: The namespace for parsed args.
        :type namespace: argparse.Namespace
        """
        level = namespace.log_level or 'info'
        logging.basicConfig(level=logging.getLevelName(level.upper()))

    def __call__(
            self, parser, namespace, values,
            option_string=None):  # pragma: no cover
        """
        Sets up for execution of action.

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
        self._setup_logger(namespace)
        return self.run(parser, namespace, values, option_string)
