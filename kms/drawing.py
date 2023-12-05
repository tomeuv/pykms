
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
