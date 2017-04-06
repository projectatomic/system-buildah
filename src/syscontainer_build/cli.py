#!/usr/bin/env python
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

import json
import os
import shutil
import subprocess
import tempfile

import click
import jinja2

from syscontainer_build import util


MANIFEST_JSON_STRUCT = {
    "version": "1.0",
    "defaultValues": {},
}


@click.command(
    'generate-files',
    short_help='Generate system container files',
    help='Generates manifest.json, config.template, and service.template.')
@click.option('--output', '-o', prompt='Directory to write in', default='.')
@click.option('--description', '-d', prompt='Description of container')
@click.option(
    '--config', '-c', help='Options to pass to ocitools generate. Example: '
    '-c "--cwd=/tmp --os=linux"')
@click.option('--default', '-D', multiple=True,
              help='Default manifest values in the form of key=value')
def generate_files(output, description, config, default):
    """
    Generates manifest.json, config.template, and service.template
    for a system container.

    :param output: Directory to write in.
    :type output: str
    :param description: Description of the container.
    :type description: str
    :param config: Options to pass to ocitools generate.
    :type config: str
    :param default: Defaults for the manifest.
    :type default: dict
    :raises: click.exceptions.ClickException
    """
    output = util.mkdir(output)
    manifest_struct = MANIFEST_JSON_STRUCT.copy()
    for item in default:
        try:
            k, v = item.split('=')
            manifest_struct['defaultValues'][k] = v
        except ValueError as error:
            click.echo('{} not in a=b format. Skipping...'.format(item))

    # Generate the manifest.json
    manifest_out = os.path.sep.join([output, 'manifest.json'])
    with open(manifest_out, 'w') as manifest:
        json.dump(manifest_struct, manifest, indent='    ')

    # Generate the service.template
    service_out = os.path.sep.join([output, 'service.template'])
    with open(service_out, 'w') as service:
        loader = jinja2.PackageLoader('syscontainer_build')
        rendered = loader.load(
            jinja2.Environment(), 'service.template.j2').render(
                description=description)
        service.write(rendered)

    # Generate config.json using ocitools
    temp_dir = tempfile.mkdtemp()
    popd = util.pushd(temp_dir)
    try:
        ocitools_cmd = ['ocitools', 'generate']
        for item in config.split(' '):
            try:
                ocitools_cmd = ocitools_cmd + item.split('=')
            except ValueError as error:
                click.echo('{} not in a=b format. Skipping...'.format(item))
        click.echo(ocitools_cmd)
        subprocess.check_call(ocitools_cmd)
        config_out = os.path.sep.join([output, 'config.json.template'])
        shutil.move('config.json', config_out)
    except subprocess.CalledProcessError as error:
        raise click.exceptions.ClickException(
            'ocitools generate failed: {}'.format(error))
    finally:
        popd()
        shutil.rmtree(temp_dir)


@click.command(
    'generate-dockerfile',
    short_help='Generate a new Dockerfile',
    help='Generates a Dockerfile for use when creating a system container.')
@click.argument('name', required=True)
@click.option('--from-base', '-f', default='centos:latest')
@click.option('--maintainer', '-m', default='{}@{}'.format(
    os.getenv('USER', 'UNKNOWN'), os.getenv('HOSTNAME', 'UNKNOWN')))
@click.option('--license', '-l', default='UNKNOWN')
@click.option('--summary', '-s', prompt='Summary')
@click.option('--version', '-v', default='1')
@click.option('--help-text', '-H', prompt='Help')
@click.option('--architecture', '-a', default='x86_64')
@click.option('--scope', '-S', default='public', type=click.Choice([
    'private', 'authoritative-source-only', 'restricted', 'public']))
@click.option('--output', '-o', default='.')
def generate_dockerfile(
        name, from_base, maintainer, license_name, summary, version,
        help_text, architecture, scope, output):
    """
    Generates a Dockerfile for use when creating a system container.

    :param name: Name of the image.
    :type name: str
    :param from_base: The image to use as a base.
    :type from_base: str
    :param maintainer: The maintainer of the image.
    :type maintainer: str
    :param license_name: The license of the image.
    :type license_name: str
    :param summary: Description of the image.
    :type summary: str
    :param version: Version of the Dockerfile.
    :type version: str
    :param help_text: Help information for the image.
    :type help_text: str
    :param architecture: Image architecture.
    :type architecture: str
    :param scope: Scope of the image.
    :type architecture: str
    :param output: Directory to write in.
    :type output: str
    :raises: click.exceptions.ClickException
    """
    output = util.mkdir(output)
    with open(os.path.sep.join([output, 'Dockerfile']), 'w') as dockerfile:
        loader = jinja2.PackageLoader('syscontainer_build')
        rendered = loader.load(jinja2.Environment(), 'Dockerfile.j2').render(
            from_base=from_base, name=name, maintainer=maintainer,
            license_name=license_name, summary=summary, version=version,
            help_text=help_text, architecture=architecture, scope=scope)
        dockerfile.write(rendered)


@click.command(
    'build',
    short_help='Build a new image',
    help='Builds a new system container image.')
@click.option('--path', '-p', default='.')
@click.argument('tag', required=True)
def build(path, tag):
    """
    Builds a new system container image.

    :param path: Path to the directory containing the Dockerfile.
    :type path: str
    :param tag: The tag to use for the new image.
    :type tag: str
    :raises: click.exceptions.ClickException
    """
    popd = util.pushd(path)
    try:
        subprocess.check_call(['docker', 'build', '-t', tag, '.'])
    except subprocess.CalledProcessError as error:
        raise click.exceptions.ClickException(
            'Can not build image: {}'.format(error))
    finally:
        popd()


@click.command(
    'tar',
    short_help='Export image to a tar file',
    help='Exports an image as a tar file.')
@click.argument('image', required=True)
def docker_image_to_tar(image):
    """
    Exports an image as a tar file.

    :param image: The name of the image.
    :type image: str
    :raises: click.exceptions.ClickException
    """
    try:
        subprocess.check_call([
            'docker', 'save', '-o', '{}.tar'.format(image), image])
    except subprocess.CalledProcessError as error:
        raise click.exceptions.ClickException(
            'Unable to export image to a tar: {}'.format(error))


def main():
    """
    Main entry point.
    """
    cli = click.Group()
    cli.add_command(generate_files)
    cli.add_command(generate_dockerfile)
    cli.add_command(build)
    cli.add_command(docker_image_to_tar)
    cli()


if __name__ == '__main__':
    main()
