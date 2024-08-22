#!/usr/bin/python3

import argparse
import sys

from PIL import Image
import numpy as np

import kms
import kms.uapi
import kms.uapi.dma_heap

def draw_test_pattern(fb):
    image = Image.open('pics/wallpaper.png')
    image = image.resize((fb.width, fb.height),
                         Image.Resampling.LANCZOS)
    pixels = np.array(image)

    map = fb.map(0)
    b = np.frombuffer(map, dtype=np.uint8).reshape(fb.height, fb.width, 4)
    b[:, :, :] = pixels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--connector", default="")
    parser.add_argument("--dmabuf", action="store_true", help="use dmabuf")
    args = parser.parse_args()

    card = kms.Card()

    res = kms.ResourceManager(card)
    conn = res.reserve_connector(args.connector)
    crtc = res.reserve_crtc(conn)
    plane = res.reserve_generic_plane(crtc)
    mode = conn.get_default_mode()
    modeb = kms.Blob(card, mode)

    if args.dmabuf:
        heap_fd = kms.uapi.dma_heap.dma_heap_alloc(mode.hdisplay * mode.vdisplay * 4,
                                                   'reserved')

        fb = kms.DmabufFramebuffer(card, mode.hdisplay, mode.vdisplay,
                                   kms.PixelFormats.XRGB8888,
                                   [heap_fd], [mode.hdisplay * 4], [0])
    else:
        fb = kms.DumbFramebuffer(card, mode.hdisplay, mode.vdisplay, kms.PixelFormats.XRGB8888)

    draw_test_pattern(fb)

    card.disable_planes()

    req = kms.AtomicReq(card)

    req.add_connector(conn, crtc)
    req.add_crtc(crtc, modeb)
    req.add_plane(plane, fb, crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

    req.commit_sync(allow_modeset = True)

    input("press enter to exit\n")

if __name__ == '__main__':
    sys.exit(main())
