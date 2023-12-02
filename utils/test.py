#!/usr/bin/python3

import kms
import os
import fcntl
import ctypes

card = kms.Card()


def create_dumb(fd):
    dumb = kms.drm_mode_create_dumb()
    dumb.width = 1920
    dumb.height = 1080
    dumb.bpp = 32
    fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_CREATE_DUMB, dumb, True)

    return dumb

dumb = create_dumb(card.fd)
print(dumb)
