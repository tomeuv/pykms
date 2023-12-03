from .kms import *

def drm_mode_modeinfo_to_str(self: drm_mode_modeinfo):
    return f'drm_mode_modeinfo({self.hdisplay}x{self.vdisplay})'

drm_mode_modeinfo.__repr__ = drm_mode_modeinfo_to_str

DRM_MODE_CONNECTED         = 1
DRM_MODE_DISCONNECTED      = 2
DRM_MODE_UNKNOWNCONNECTION = 3

DRM_PLANE_TYPE_OVERLAY = 0
DRM_PLANE_TYPE_PRIMARY = 1
DRM_PLANE_TYPE_CURSOR  = 2
