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
Managers for working with images.
"""

from abc import ABCMeta, abstractmethod


class ImageManager(metaclass=ABCMeta):
    """
    Base class for image management.
    """

    def _normalize_filename(self, data):
        """
        Replaces problematic chars in filesnames.

        :param data: The filename to normalize
        :type data: str
        :returns: A normalized filename
        :rtype: str
        """
        return data.replace(':', '-').replace('/', '-')

    @abstractmethod
    def build(self, namespace, tag):  # pragma: no cover
        """
        Builds a specific image.

        :param namespace: Namespace passed in via CLI.
        :type namespace: argparse.Namespace
        :param tag: The tag to use when building.
        :type tag: str
        :raises: subprocess.CalledProcessError
        """
        pass

    @abstractmethod
    def tar(self, namespace, output):  # pragma: no cover
        """
        Exports a specific image to a tar file.

        :param namespace: Namespace passed in via CLI.
        :type namespace: argparse.Namespace
        :param output: The name of the file to output.
        :type output: str
        :raises: subprocess.CalledProcessError
        """
        pass
