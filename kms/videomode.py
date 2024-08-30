from __future__ import annotations

from typing import TYPE_CHECKING

import kms.uapi

if TYPE_CHECKING:
    from kms import Card

__all__ = [ 'VideoMode' ]

class VideoMode:
    def __init__(self, modeinfo: kms.uapi.drm_mode_modeinfo):
        self.modeinfo = modeinfo

    def __repr__(self):
        return f'VideoMode({self.modeinfo.hdisplay}x{self.modeinfo.vdisplay})'

    def to_blob(self, card: Card):
        return kms.Blob(card, self.modeinfo)

    @property
    def clock(self):
        return self.modeinfo.clock

    @property
    def hdisplay(self):
        return self.modeinfo.hdisplay

    @property
    def vdisplay(self):
        return self.modeinfo.vdisplay

    @property
    def htotal(self):
        return self.modeinfo.htotal

    @property
    def vtotal(self):
        return self.modeinfo.vtotal

    @property
    def interlace(self):
        return self.modeinfo.flags & kms.uapi.DRM_MODE_FLAG_INTERLACE
