# syscontainer-build
Simple toolbox for building system containers.

[![Build Status](https://travis-ci.org/ashcrow/syscontainer-build.svg)](https://travis-ci.org/ashcrow/syscontainer-build)

**Note**: This is a POC

## Requires

* python3
* click (python library)
* jinja2 (python library)

## Example

```shell
$ syscontainer-build generate-files --default=variable=value -D=another=anothervalue --output new_container_image
$ syscontainer-build generate-dockerfile --from-base fedora:latest --output new_container_image
Container Name: mycontainer
Summary: This is my container
Help: Help text would go here
$ syscontainer-build build --path new_container_image my_system_container_image
[...]
# Export as a tar
$ syscontainer-build tar my_system_container_image
```
