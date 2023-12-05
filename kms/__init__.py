import kms.uapi
from kms.card import *
from kms.resource_manager import *
from kms.atomicreq import *
from kms.pixelformats import *

# XXX compat
def drm_mode_modeinfo_to_blob(self: kms.uapi.drm_mode_modeinfo, card: kms.Card):
    return kms.Blob(card, self)

kms.uapi.drm_mode_modeinfo.to_blob = drm_mode_modeinfo_to_blob # type: ignore

def fourcc_to_str(fourcc: int):
    return ''.join((
        chr((fourcc >> 0) & 0xff),
        chr((fourcc >> 8) & 0xff),
        chr((fourcc >> 16) & 0xff),
        chr((fourcc >> 24) & 0xff)
    ))

def str_to_fourcc(s: str):
    return \
        ord(s[0]) << 0 | \
        ord(s[1]) << 8 | \
        ord(s[2]) << 16 | \
        ord(s[3]) << 24

PlaneTypeOverlay = 1 << 0
PlaneTypePrimary = 1 << 1
PlaneTypeCursor = 1 << 2

# XXX deprecated
def draw_color_bar(fb, old_xpos, new_xpos, bar_width):
    bytespp = 4

    m = fb.map(0)
    empty = bytearray(bar_width * bytespp)
    fill = bytearray([0xff] * (bar_width * bytespp))

    stride = fb.planes[0].stride

    old_xoff = old_xpos * bytespp
    new_xoff = new_xpos * bytespp

    for y in range(fb.height):
        yoff = y * stride
        m[yoff + old_xoff:yoff + old_xoff + len(empty)] = empty
        m[yoff + new_xoff:yoff + new_xoff + len(fill)] = fill

# XXX deprecated
class RGB:
    def __init__(self, a, r, g, b) -> None:
        self.a = a
        self.r = r
        self.b = b
        self.g = g

# XXX deprecated
def draw_rect(fb, x, y, w, h, color: RGB):
    bytespp = 4

    fill = bytearray([color.b, color.g, color.r, color.a] * w)

    m = fb.map(0)

    stride = fb.planes[0].stride

    xoff = x * bytespp

    for y in range(y, y + h):
        yoff = y * stride
        m[yoff + xoff:yoff + xoff + len(fill)] = fill
