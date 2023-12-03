from kms.kernel import *
from kms.card import *

# XXX compat
def drm_mode_modeinfo_to_blob(self: drm_mode_modeinfo, card: kms.Card):
    return kms.Blob(card, self)

drm_mode_modeinfo.to_blob = drm_mode_modeinfo_to_blob

DRM_MODE_CONNECTED         = 1
DRM_MODE_DISCONNECTED      = 2
DRM_MODE_UNKNOWNCONNECTION = 3

DRM_PLANE_TYPE_OVERLAY = 0
DRM_PLANE_TYPE_PRIMARY = 1
DRM_PLANE_TYPE_CURSOR  = 2

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
