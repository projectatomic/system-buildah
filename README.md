# syscontainer-build
Simple toolbox for building system containers.

[![Build Status](https://travis-ci.org/ashcrow/syscontainer-build.svg)](https://travis-ci.org/ashcrow/syscontainer-build)

**Note**: This is a POC

## Requires

* python3
* docker binary and service
* ocitools binary
* jinja2 (python library)

## Install

1. Clone the repo
2. ```python setup.py install --user```

### Install via RPM

1. Download the source
2. Extract the source to the local directory
3. Move the tarball to your ``rpmbuild/SOURCES/`` directory
4. ```rpmbuild -ba contrib/rpm/syscontainer-build.spec```
5. ```rpm -ivh $PATH_OF_THE_BUILT_RPM```

## Example

```shell
# Generate system container files
$ syscontainer-build generate-files \
    --default=variable=value -D=another=anothervalue \
    --config="--hostname=confighost --cwd=/root" \
    new_container_image
# Generate a system container Dockerfile
$ syscontainer-build generate-dockerfile \
    --from-base fedora:latest \
    --output new_container_image name_of_image
# Build a system container image
$ syscontainer-build build \
    --path new_container_image my_system_container_image
[...]
# Export the image as a tar
$ syscontainer-build tar my_system_container_image
```
