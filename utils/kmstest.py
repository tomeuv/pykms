#!/usr/bin/python3

import kms
import kms.uapi
import argparse
import selectors
import sys
import time
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--connector", default="")
parser.add_argument("--dmabuf", action="store_true", help="use dmabuf")
args = parser.parse_args()

card = kms.Card()

res = kms.ResourceManager(card)
conn = res.reserve_connector(args.connector)
crtc = res.reserve_crtc(conn)
plane = res.reserve_generic_plane(crtc, kms.PixelFormat.XRGB8888)
mode = conn.get_default_mode()
modeb = kms.Blob(card, mode)

fbs = []
numpybufs = []
mmaps = []
for x in range(3):
    fb = kms.DumbFramebuffer(card, mode.hdisplay, mode.vdisplay, kms.PixelFormat.XRGB8888)

    fb_mmaps = fb.mmap()
    buf = fb_mmaps[0]
    buf[:] = bytearray(fb.planes[0].size)

    b = np.frombuffer(buf, dtype=np.uint32).reshape(fb.height, fb.width)

    fbs.append(fb)
    mmaps.append(fb_mmaps)
    numpybufs.append(b)


#card.disable_planes()

req = kms.AtomicReq(card)

req.add_connector(conn, crtc)
req.add_crtc(crtc, modeb)
req.add_plane(plane, fbs[2], crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

req.commit(allow_modeset = True)

current_fb = None
next_fb = 0
bar_y = 0
last_ts = time.perf_counter()
last_framenum = 0
framenum = 0
bar_step = 4

line_0 = bytes([0] * (mode.hdisplay * 4))
line_1 = bytes([0xff] * (mode.hdisplay * 4))

def handle_pageflip():
    global current_fb, next_fb, bar_y
    global last_ts, last_framenum
    global framenum

    framenum += 1

    ts = time.perf_counter()
    ts_diff = ts - last_ts

    if ts_diff > 2:
        num_frames = framenum - last_framenum

        fps = num_frames / ts_diff

        last_ts = ts
        last_framenum = framenum

        print(f'fps {fps:.2f}')

    #print("FLIP, cur", current_fb, "next", next_fb)

    old_fb = current_fb

    current_fb = next_fb

    next_fb = (current_fb + 1) % len(fbs)

    req = kms.AtomicReq(card)

    req.add_plane(plane, fbs[next_fb], crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

    req.commit(allow_modeset = False)

    old_y = bar_y - len(fbs) * bar_step
    if old_y < 0:
        old_y = mode.vdisplay + old_y

    if old_fb != None:

        ts1 = time.perf_counter()

        fb = fbs[old_fb]

        m = mmaps[old_fb][0]
        stride = fb.planes[0].stride

        m[old_y * stride:old_y * stride + fb.width * 4] = line_0
        m[bar_y * stride:bar_y * stride + fb.width * 4] = line_1

        #b = numpybufs[old_fb]
        #b[old_y, :] = 0
        #b[bar_y, :] = 0xffffff

        ts2 = time.perf_counter()

        print((ts2 - ts1) * 1000)

        bar_y += bar_step
        if bar_y >= mode.vdisplay:
            bar_y = 0


def readdrm():
    for ev in card.read_events():
        if ev.type == kms.DrmEventType.FLIP_COMPLETE:
            handle_pageflip()

def readkey():
    print("Done")
    sys.stdin.readline()
    sys.exit(0)

sel = selectors.DefaultSelector()
sel.register(sys.stdin, selectors.EVENT_READ, readkey)
sel.register(card.fd, selectors.EVENT_READ, readdrm)

while True:
    events = sel.select()
    for key, mask in events:
        callback = key.data
        callback()
