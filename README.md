# system-buildah
Simple toolbox for building system images. Read more on the [Project Atomic Blog](http://www.projectatomic.io/blog/2017/06/creating-system-containers/).

[![Build Status](https://travis-ci.org/ashcrow/system-buildah.svg)](https://travis-ci.org/ashcrow/system-buildah)

## Requires

The list of requirements are limited to keep portability between OS variations as simple as possible.

* python3
* docker binary and service
* ocitools binary
* jinja2 (python library)

## Install

### For Your User
1. Clone the repo
2. ```python setup.py install --user```

### Install via RPM

1. Download the source
2. Extract the source to the local directory
3. Move the tarball to your ``rpmbuild/SOURCES/`` directory
4. ```rpmbuild -ba contrib/rpm/system-buildah.spec```
5. ```rpm -ivh $PATH_OF_THE_BUILT_RPM```

## Example

```shell
# Generate system container files
$ system-buildah generate-files \
    --default=variable=value -D=another=anothervalue \
    --config="--hostname=confighost --cwd=/root" \
    new_container_image
# Generate a system container Dockerfile
$ system-buildah generate-dockerfile \
    --from-base fedora:latest \
    --output new_container_image name_of_image
# Build a system container image
$ system-buildah build \
    --path new_container_image my_system_container_image
[...]
# Export the image as a tar
$ system-buildah tar my_system_container_image
```
