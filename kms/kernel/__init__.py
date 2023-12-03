from .kms import *

def drm_mode_modeinfo_to_str(self: drm_mode_modeinfo):
    return f'drm_mode_modeinfo({self.hdisplay}x{self.vdisplay})'

drm_mode_modeinfo.__repr__ = drm_mode_modeinfo_to_str
