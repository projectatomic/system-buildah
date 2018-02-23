#!/usr/bin/env python3
#
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
Build and installation script.
"""

from setuptools import setup, find_packages


def extract_requirements(filename):
    with open(filename, 'r') as requirements_file:
        return [x.split()[0] for x in requirements_file.readlines()]


install_requires = extract_requirements('requirements.txt')
test_require = extract_requirements('test-requirements.txt')


setup(
    name='system-buildah',
    version='0.1.0',
    description='Simple System Image build toolbox',
    author='Steve Milner',
    url='https://github.com/projectatomic/system-buildah',
    license="GPLv3+",

    install_requires=install_requires,
    tests_require=test_require,
    package_dir={'': 'src'},
    packages=find_packages('src'),
    package_data={
        '': ['templates/*'],
    },
    entry_points={
        'console_scripts': [
            'system-buildah = system_buildah.cli:main',
        ],
    }
)
