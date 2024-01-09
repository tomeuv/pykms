#!/usr/bin/python3

import argparse
import sys
import kms
import kms.drawing

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--connector", default="")
args = parser.parse_args()

card = kms.Card()

res = kms.ResourceManager(card)
conn = res.reserve_connector(args.connector)
crtc = res.reserve_crtc(conn)
plane = res.reserve_plane(crtc, kms.PixelFormat.XRGB8888)
mode = conn.get_default_mode()
modeb = kms.Blob(card, mode)

fb = kms.DumbFramebuffer(card, mode.hdisplay, mode.vdisplay, kms.PixelFormat.XRGB8888)
kms.drawing.fill_rect(fb, 10, 10, 100, 100, kms.drawing.RGB(255, 255, 0, 0))

req = kms.AtomicReq(card)

req.add_connector(conn, crtc)
req.add_crtc(crtc, modeb)
req.add_plane(plane, fb, crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

req.commit(allow_modeset = True)

sys.stdin.readline()
