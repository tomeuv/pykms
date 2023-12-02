#!/usr/bin/python3

import kms
import argparse

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
modeb = mode.to_blob(card)

print("Using", conn, crtc, plane, mode, modeb)

origfb = kms.DumbFramebuffer(card, mode.hdisplay, mode.vdisplay, "XR24");

#if args.dmabuf:
#        fb = kms.DmabufFramebuffer(card, origfb.width, origfb.height, origfb.format,
#		[origfb.fd(0)], [origfb.stride(0)], [origfb.offset(0)])
#else:
fb = origfb

#kms.draw_test_pattern(fb);

#card.disable_planes()

req = kms.AtomicReq(card)

req.add_connector(conn, crtc)
req.add_crtc(crtc, modeb)
req.add_plane(plane, fb, crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

req.commit_sync(allow_modeset = True)

input("press enter to exit\n")
