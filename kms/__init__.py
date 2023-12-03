import kms.uapi
from kms.card import *
from kms.resource_manager import *
from kms.atomicreq import *

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
