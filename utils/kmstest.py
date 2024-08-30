#!/usr/bin/python3

import argparse
import sys
import time

import numpy as np

from pixutils.dmaheap import DMAHeap

import kms
import kms.uapi

def fill_rect(b, x, y, c):
    b[y:y+200, x:x+200] = c

def draw_gradient(b, x, y, gradient):
    b[y:y+200, x:x+len(gradient)] = gradient

def draw_test_pattern(fb):
    map = fb.map(0)
    b = np.frombuffer(map, dtype=np.uint32).reshape(fb.height, fb.width)

    fill_rect(b, 2, 2, 0xff0000)
    fill_rect(b, 202, 202, 0x00ff00)
    fill_rect(b, 402, 402, 0x0000ff)

    fill_rect(b, 202, 2, 0xffff00)
    fill_rect(b, 402, 202, 0x00ffff)

    fill_rect(b, 402, 2, 0xffffff)

    gradient = np.arange(256 - 1, -1, -1, dtype=np.uint32)

    draw_gradient(b, 800, 2, gradient << 16)
    draw_gradient(b, 800, 202, gradient << 8)
    draw_gradient(b, 800, 402, gradient << 0)

    b[0::fb.height-1, :] = 0xffffff
    b[:, 0::fb.width-1] = 0xffffff

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--connector', default='')
    parser.add_argument('--dmabuf', nargs='?', const='reserved', metavar='HEAP', help='use dmabuf')
    args = parser.parse_args()

    card = kms.Card()

    res = kms.ResourceManager(card)
    conn = res.reserve_connector(args.connector)
    crtc = res.reserve_crtc(conn)
    plane = res.reserve_generic_plane(crtc)
    mode = conn.get_default_mode()
    modeb = kms.Blob(card, mode)

    fmt = kms.PixelFormats.XRGB8888
    width = mode.hdisplay
    height = mode.vdisplay

    if args.dmabuf:
        heap = DMAHeap(args.dmabuf)
        heap_buf = heap.alloc(fmt.framesize(width, height))

        fb = kms.DmabufFramebuffer(card, width, height,
                                   fmt,
                                   fds=[ heap_buf.fd ],
                                   pitches=[ fmt.stride(width) ],
                                   offsets=[ 0 ])
    else:
        fb = kms.DumbFramebuffer(card, width, height, fmt)

    ts1 = time.perf_counter()
    draw_test_pattern(fb)
    ts2 = time.perf_counter()
    print(f'Drawing took {(ts2 - ts1) * 1000:.4f} ms')

    req = kms.AtomicReq(card)

    req.add_connector(conn, crtc)
    req.add_crtc(crtc, modeb)
    req.add_plane(plane, fb, crtc, dst=(0, 0, width, height))

    req.commit_sync(allow_modeset = True)

    input('press enter to exit\n')

if __name__ == '__main__':
    sys.exit(main())
