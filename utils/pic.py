#!/usr/bin/python3

import kms
import argparse
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("image")
parser.add_argument("-f", "--fourcc", default="XR24")
args = parser.parse_args()

card = kms.Card()
res = kms.ResourceManager(card)
conn = res.reserve_connector()
crtc = res.reserve_crtc(conn)
mode = conn.get_default_mode()
fb = kms.DumbFramebuffer(card, mode.hdisplay, mode.vdisplay, args.fourcc)
crtc.set_mode(conn, fb, mode)

image = Image.open(args.image)
image = image.resize((mode.hdisplay, mode.vdisplay),
                     Image.Resampling.LANCZOS)
pixels = np.array(image)

map = fb.map(0)
b = np.frombuffer(map, dtype=np.uint8).reshape(fb.height, fb.width, 4)
b[:, :, :] = pixels

print("Press enter to exit")
input()

# We need to release the numpy array, as it references the mmap
b = None
