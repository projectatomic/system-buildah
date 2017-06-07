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
Utility functions.
"""

import os

from contextlib import contextmanager


def _expand_path(path):
    """
    Expands a path.

    :param path: A file system path.
    :type path: str
    :returns: A full path starting from the system root.
    :rtype: str
    """
    return os.path.realpath(os.path.expanduser(path))


def mkdir(path):
    """
    Shortcut for making directories.

    :param path: A file system path.
    :type path: str
    :returns: The full path starting from system root that was created.
    :rtype: str
    """
    path = _expand_path(path)
    try:
        os.mkdir(path)
    except FileExistsError:
        pass

    return path


@contextmanager
def pushd(path):
    """
    Changes to a path until end of context.

    :param path: A file system path.
    :type path: str
    """
    original_cwd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(original_cwd)
