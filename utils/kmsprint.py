#!/usr/bin/python3

import kms
import kms.uapi # XXX remove
import sys

# Connector 0 (40) DP-1 (connected)
#   Encoder 0 (39) NONE
#     Crtc 0 (38) 2560x1440@59.95 241.500 2560/48/32/80/+ 1440/3/5/33/- 60 (59.95) P|D
#       Plane 0 (31) fb-id: 65 (crtcs: 0 1) 0,0 2560x1440 -> 0,0 2560x1440 (AR12 AB12 RA12 RG16 BG16 AR15 AB15 AR24 AB24 RA24 BA24 RG24 BG24 AR30 AB30 XR12 XB12 RX12 XR15 XB15 XR24 XB24 RX24 BX24 XR30 XB30 YUYV UYVY NV12)
#         FB 65 2560x1440 XR24
# Connector 1 (50) HDMI-A-1 (disconnected)
#   Encoder 1 (49) NONE
#     Crtc 1 (48) 1920x1080@59.72 138.000 1920/48/32/80/+ 1080/3/5/23/- 60 (59.72) P|D


def print_connector(c: kms.Connector):
    print(f'Connector {c.idx} ({c.id}) {c.fullname} ({"connected" if c.connected else "disconnected"})')

def print_encoder(e: kms.Encoder):
    print(f'  Encoder {e.idx} ({e.id}) {e.encoder_type.name}')

def print_crtc(crtc: kms.Crtc):
    m = crtc.mode

    refresh = (m.clock * 1000.0) / (m.htotal * m.vtotal) * (2 if (m.flags & kms.uapi.DRM_MODE_FLAG_INTERLACE) else 1)
    refresh = round(refresh, 2)

    print(f'    Crtc {crtc.idx} ({crtc.id}) {m.hdisplay}x{m.vdisplay}@{refresh} {m.clock / 1000:.3f}')

def print_plane(p: kms.Plane):
    src_x = p.get_prop_value("SRC_X") >> 16
    src_y = p.get_prop_value("SRC_Y") >> 16
    src_w = p.get_prop_value("SRC_W") >> 16
    src_h = p.get_prop_value("SRC_H") >> 16

    crtc_x = p.get_prop_value("CRTC_X")
    crtc_y = p.get_prop_value("CRTC_Y")
    crtc_w = p.get_prop_value("CRTC_W")
    crtc_h = p.get_prop_value("CRTC_H")

    print(f'      Plane {p.idx} ({p.id}) fb-id {p.fb_id} ' +
          f'{src_x},{src_y} {src_w}x{src_h} -> {crtc_x},{crtc_y} {crtc_w}x{crtc_h} ')

def main():
    card = kms.Card()

    for c in card.connectors:
        print_connector(c)

        for e in c.encoders:
            print_encoder(e)

            crtc = e.crtc

            if not crtc:
                continue

            print_crtc(crtc)

            for p in card.planes:
                if p.crtc_id != crtc.id:
                    continue

                print_plane(p)


if __name__ == '__main__':
    sys.exit(main())
