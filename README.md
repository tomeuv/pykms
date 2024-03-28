[![Lint Status](https://github.com/tomba/pykms/actions/workflows/pylint.yml/badge.svg)](https://github.com/tomba/pykms/actions/workflows/pylint.yml)

# Pure-Python Linux kernel mode setting (KMS) bindings

## kms.uapi

kms.uapi namespace contains the kernel user-space API (uAPI).

The uAPI is generated with (slighly customized) ctypesgen, with the gen.py script. Also, the kms/uapi/__init__.py contains some minor additions to the uAPI.

## kms

kms namespace contains wrappers to the uAPI to simplify the use of the uAPI. The target is that the user of the kms namespace does not need to use any types from the kms.uapi namespace.

## utils

utils directory contains miscallaneous more-or-less under-work utilities.

## License

This project is covered by the [LGPL-3.0](LICENSE.md) license.
