from enum import Enum
import kms.uapi

class PlaneType(Enum):
    Overlay = kms.uapi.DRM_PLANE_TYPE_OVERLAY
    Primary = kms.uapi.DRM_PLANE_TYPE_PRIMARY
    Cursor = kms.uapi.DRM_PLANE_TYPE_CURSOR
