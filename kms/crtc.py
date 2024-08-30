from __future__ import annotations

import fcntl

from typing import TYPE_CHECKING

import kms
import kms.uapi

if TYPE_CHECKING:
    from kms import Card

__all__ = [ 'Crtc', ]

class Crtc(kms.DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.uapi.DRM_MODE_OBJECT_CRTC, idx)

        res = kms.uapi.drm_mode_crtc()

        res.crtc_id = id

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETCRTC, res, True)
        self.crtc_res = res

        #print(f"CRTC {id}: fb: {res.fb_id}")

    def __repr__(self) -> str:
        return f'Crtc({self.id})'

    def get_possible_planes(self):
        return [p for p in self.card.planes if p.supports_crtc(self)]

    # XXX create our own mode class
    @property
    def mode(self) -> kms.uapi.drm_mode_modeinfo:
        return self.crtc_res.mode

    @property
    def primary_plane(self):
        plane = next((p for p in self.get_possible_planes() if p.type == kms.PlaneType.PRIMARY and p.crtc_id == self.id), None)
        if plane:
            return plane
        plane = next((p for p in self.get_possible_planes() if p.type == kms.PlaneType.PRIMARY), None)
        if plane:
            return plane
        plane = next((p for p in self.get_possible_planes()), None)
        if plane:
            return plane
        raise RuntimeError("No primary plane")
