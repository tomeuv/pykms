from __future__ import annotations

from enum import Enum
import kms.uapi

class PlaneType(Enum):
    Overlay = kms.uapi.DRM_PLANE_TYPE_OVERLAY
    Primary = kms.uapi.DRM_PLANE_TYPE_PRIMARY
    Cursor = kms.uapi.DRM_PLANE_TYPE_CURSOR

class EncoderType(Enum):
    NONE = kms.uapi.DRM_MODE_ENCODER_NONE
    DAC = kms.uapi.DRM_MODE_ENCODER_DAC
    TMDS = kms.uapi.DRM_MODE_ENCODER_TMDS
    LVDS = kms.uapi.DRM_MODE_ENCODER_LVDS
    TVDAC = kms.uapi.DRM_MODE_ENCODER_TVDAC
    VIRTUAL = kms.uapi.DRM_MODE_ENCODER_VIRTUAL
    DSI = kms.uapi.DRM_MODE_ENCODER_DSI
    DPMST = kms.uapi.DRM_MODE_ENCODER_DPMST
    DPI = kms.uapi.DRM_MODE_ENCODER_DPI
