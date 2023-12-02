#!/usr/bin/python3

import kms
import os
import fcntl
import ctypes

fd = os.open("/dev/dri/card0", os.O_RDWR | os.O_NONBLOCK)
assert(fd != -1)


def get_version(fd):
    ver = kms.drm_version()
    fcntl.ioctl(fd, kms.DRM_IOCTL_VERSION, ver, True)

    ver.name = kms.String(b' ' * ver.name_len)
    ver.date = kms.String(b' ' * ver.date_len)
    ver.desc = kms.String(b' ' * ver.desc_len)

    fcntl.ioctl(fd, kms.DRM_IOCTL_VERSION, ver, True)

    print(ver.name)

    return ver

def get_res(fd):
    res = kms.drm_mode_card_res()
    fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_GETRESOURCES, res, True)

    fb_ids = (ctypes.c_uint32 * res.count_fbs)()
    res.fb_id_ptr = ctypes.addressof(fb_ids)

    crtc_ids = (ctypes.c_uint32 * res.count_crtcs)()
    res.crtc_id_ptr = ctypes.addressof(crtc_ids)

    connector_ids = (ctypes.c_uint32 * res.count_connectors)()
    res.connector_id_ptr = ctypes.addressof(connector_ids)

    encoder_ids = (ctypes.c_uint32 * res.count_encoders)()
    res.encoder_id_ptr = ctypes.addressof(encoder_ids)

    fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_GETRESOURCES, res, True)

    crtcs = []
    connectors = []
    encoders = []

    for crtc_id in crtc_ids:
        crtc = kms.drm_mode_crtc()

        crtc.crtc_id = crtc_id

        fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_GETCRTC, crtc, True)

        print(f"CRTC {crtc_id}: fb: {crtc.fb_id}")

        crtcs.append(crtc)

    for connector_id in connector_ids:
        connector = kms.drm_mode_get_connector()

        connector.connector_id = connector_id

        fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_GETCONNECTOR, connector, True)

        print(f"connector {connector_id}: type: {connector.connector_type}")

        connectors.append(connector)

    for encoder_id in encoder_ids:
        encoder = kms.drm_mode_get_encoder()

        encoder.encoder_id = encoder_id

        fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_GETENCODER, encoder, True)

        print(f"encoder {encoder_id}: type: {encoder.encoder_type}")

        encoders.append(encoder)


    return (crtcs, connectors, encoders)

res = get_res(fd)

print(res)


def create_dumb(fd):
    dumb = kms.drm_mode_create_dumb()
    dumb.width = 1920
    dumb.height = 1080
    dumb.bpp = 32
    fcntl.ioctl(fd, kms.DRM_IOCTL_MODE_CREATE_DUMB, dumb, True)

    return dumb

dumb = create_dumb(fd)
print(dumb)
