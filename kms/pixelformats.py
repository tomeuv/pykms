from __future__ import annotations

from enum import Enum, IntEnum
from typing import NamedTuple
import kms.uapi

class PixelFormatPlaneInfo(NamedTuple):
    bitspp: int
    xsub: int
    ysub: int

class PixelFormatInfo:
    fourcc: int
    name: str
    colortype: int
    planes: list[PixelFormatPlaneInfo]

    def __init__(self, data) -> None:
        self.fourcc = data[0]
        self.name = data[1]
        self.colortype = data[2]
        self.planes = [PixelFormatPlaneInfo(*t) for t in data[3]]

    def __repr__(self) -> str:
        return f'PixelFormatInfo({self.fourcc:#8x}, {self.name}, {self.colortype}, {self.planes})'

class PixelColorType(Enum):
    RGB = 0
    YUV = 1
    RAW = 2

formats = (
    # YUV packed
    ( kms.uapi.DRM_FORMAT_UYVY, 'UYVY',
                     PixelColorType.YUV,
                     ( ( 16, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_YUYV, 'YUYV',
                     PixelColorType.YUV,
                     ( ( 16, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_YVYU, 'YVYU',
                     PixelColorType.YUV,
                     ( ( 16, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_VYUY, 'VYUY',
                     PixelColorType.YUV,
                     ( ( 16, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_Y210, 'Y210',
                     PixelColorType.YUV,
                     ( ( 32, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_Y212, 'Y212',
                     PixelColorType.YUV,
                     ( ( 32, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_Y216, 'Y216',
                     PixelColorType.YUV,
                     ( ( 32, 2, 1 ), ),
                 ),

    # YUV semi-planar
    ( kms.uapi.DRM_FORMAT_NV12, 'NV12',
                     PixelColorType.YUV,
                     ( ( 8, 1, 1 ), ( 8, 2, 2 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_NV21, 'NV21',
                     PixelColorType.YUV,
                     ( ( 8, 1, 1 ), ( 8, 2, 2 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_NV16, 'NV16',
                     PixelColorType.YUV,
                     ( ( 8, 1, 1 ), ( 8, 2, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_NV61, 'NV61',
                     PixelColorType.YUV,
                     ( ( 8, 1, 1 ), ( 8, 2, 1 ), ),
                 ),
    # YUV planar
    ( kms.uapi.DRM_FORMAT_YUV420, 'YUV420',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 2, 2 ), ( 8, 2, 2 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_YVU420, 'YVU420',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 2, 2 ), ( 8, 2, 2 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_YUV422, 'YUV422',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 2, 1 ), ( 8, 2, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_YVU422, 'YVU422',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 2, 1 ), ( 8, 2, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_YUV444, 'YUV444',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 1, 1 ), ( 8, 1, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_YVU444, 'YVU444',
                       PixelColorType.YUV,
                       ( ( 8, 1, 1 ), ( 8, 1, 1 ), ( 8, 1, 1 ), ),
                   ),
    # RGB8
    ( kms.uapi.DRM_FORMAT_RGB332, 'RGB332',
                       PixelColorType.RGB,
                       ( ( 8, 1, 1 ), ),
                   ),
    # RGB16
    ( kms.uapi.DRM_FORMAT_RGB565, 'RGB565',
                       PixelColorType.RGB,
                       ( ( 16, 1, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_BGR565, 'BGR565',
                       PixelColorType.RGB,
                       ( ( 16, 1, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_XRGB4444, 'XRGB4444',
                     PixelColorType.RGB,
                     ( ( 16, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_XRGB1555, 'XRGB1555',
                     PixelColorType.RGB,
                     ( ( 16, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_ARGB4444, 'ARGB4444',
                     PixelColorType.RGB,
                     ( ( 16, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_ARGB1555, 'ARGB1555',
                     PixelColorType.RGB,
                     ( ( 16, 1, 1 ), ),
                 ),
    # RGB24
    ( kms.uapi.DRM_FORMAT_RGB888, 'RGB888',
                       PixelColorType.RGB,
                       ( ( 24, 1, 1 ), ),
                   ),
    ( kms.uapi.DRM_FORMAT_BGR888, 'BGR888',
                       PixelColorType.RGB,
                       ( ( 24, 1, 1 ), ),
                   ),
    # RGB32
    ( kms.uapi.DRM_FORMAT_XRGB8888, 'XRGB8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_XBGR8888, 'XBGR8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_RGBX8888, 'RGBX8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_BGRX8888, 'BGRX8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),

    ( kms.uapi.DRM_FORMAT_ARGB8888, 'ARGB8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_ABGR8888, 'ABGR8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_RGBA8888, 'RGBA8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),
    ( kms.uapi.DRM_FORMAT_BGRA8888, 'BGRA8888',
                     PixelColorType.RGB,
                     ( ( 32, 1, 1 ), ),
                 ),

    ( kms.uapi.DRM_FORMAT_XRGB2101010, 'XRGB2101010',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_XBGR2101010, 'XBGR2101010',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_RGBX1010102, 'RGBX1010102',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_BGRX1010102, 'BGRX1010102',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),

    ( kms.uapi.DRM_FORMAT_ARGB2101010, 'ARGB2101010',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_ABGR2101010, 'ABGR2101010',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_RGBA1010102, 'RGBA1010102',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
    ( kms.uapi.DRM_FORMAT_BGRA1010102, 'BGRA1010102',
                        PixelColorType.RGB,
                        ( ( 32, 1, 1 ), ),
                    ),
)

def get_pixel_format_info(fourcc) -> PixelFormatInfo:
    for p in formats:
        if p[0] == fourcc:
            info = PixelFormatInfo(p)
            return info

    raise KeyError("Pixel format not found")

# To generate:
# str.join('\n', [f'    {e[11:]} = kms.uapi.{e}' for e in kms.uapi.__dir__() if e.startswith("DRM_FORMAT_")])
# We could also just have a get_format_by_name(str) function
class PixelFormat(IntEnum):
    BIG_ENDIAN = kms.uapi.DRM_FORMAT_BIG_ENDIAN
    INVALID = kms.uapi.DRM_FORMAT_INVALID
    C8 = kms.uapi.DRM_FORMAT_C8
    R8 = kms.uapi.DRM_FORMAT_R8
    R16 = kms.uapi.DRM_FORMAT_R16
    RG88 = kms.uapi.DRM_FORMAT_RG88
    GR88 = kms.uapi.DRM_FORMAT_GR88
    RG1616 = kms.uapi.DRM_FORMAT_RG1616
    GR1616 = kms.uapi.DRM_FORMAT_GR1616
    RGB332 = kms.uapi.DRM_FORMAT_RGB332
    BGR233 = kms.uapi.DRM_FORMAT_BGR233
    XRGB4444 = kms.uapi.DRM_FORMAT_XRGB4444
    XBGR4444 = kms.uapi.DRM_FORMAT_XBGR4444
    RGBX4444 = kms.uapi.DRM_FORMAT_RGBX4444
    BGRX4444 = kms.uapi.DRM_FORMAT_BGRX4444
    ARGB4444 = kms.uapi.DRM_FORMAT_ARGB4444
    ABGR4444 = kms.uapi.DRM_FORMAT_ABGR4444
    RGBA4444 = kms.uapi.DRM_FORMAT_RGBA4444
    BGRA4444 = kms.uapi.DRM_FORMAT_BGRA4444
    XRGB1555 = kms.uapi.DRM_FORMAT_XRGB1555
    XBGR1555 = kms.uapi.DRM_FORMAT_XBGR1555
    RGBX5551 = kms.uapi.DRM_FORMAT_RGBX5551
    BGRX5551 = kms.uapi.DRM_FORMAT_BGRX5551
    ARGB1555 = kms.uapi.DRM_FORMAT_ARGB1555
    ABGR1555 = kms.uapi.DRM_FORMAT_ABGR1555
    RGBA5551 = kms.uapi.DRM_FORMAT_RGBA5551
    BGRA5551 = kms.uapi.DRM_FORMAT_BGRA5551
    RGB565 = kms.uapi.DRM_FORMAT_RGB565
    BGR565 = kms.uapi.DRM_FORMAT_BGR565
    RGB888 = kms.uapi.DRM_FORMAT_RGB888
    BGR888 = kms.uapi.DRM_FORMAT_BGR888
    XRGB8888 = kms.uapi.DRM_FORMAT_XRGB8888
    XBGR8888 = kms.uapi.DRM_FORMAT_XBGR8888
    RGBX8888 = kms.uapi.DRM_FORMAT_RGBX8888
    BGRX8888 = kms.uapi.DRM_FORMAT_BGRX8888
    ARGB8888 = kms.uapi.DRM_FORMAT_ARGB8888
    ABGR8888 = kms.uapi.DRM_FORMAT_ABGR8888
    RGBA8888 = kms.uapi.DRM_FORMAT_RGBA8888
    BGRA8888 = kms.uapi.DRM_FORMAT_BGRA8888
    XRGB2101010 = kms.uapi.DRM_FORMAT_XRGB2101010
    XBGR2101010 = kms.uapi.DRM_FORMAT_XBGR2101010
    RGBX1010102 = kms.uapi.DRM_FORMAT_RGBX1010102
    BGRX1010102 = kms.uapi.DRM_FORMAT_BGRX1010102
    ARGB2101010 = kms.uapi.DRM_FORMAT_ARGB2101010
    ABGR2101010 = kms.uapi.DRM_FORMAT_ABGR2101010
    RGBA1010102 = kms.uapi.DRM_FORMAT_RGBA1010102
    BGRA1010102 = kms.uapi.DRM_FORMAT_BGRA1010102
    XRGB16161616 = kms.uapi.DRM_FORMAT_XRGB16161616
    XBGR16161616 = kms.uapi.DRM_FORMAT_XBGR16161616
    ARGB16161616 = kms.uapi.DRM_FORMAT_ARGB16161616
    ABGR16161616 = kms.uapi.DRM_FORMAT_ABGR16161616
    XRGB16161616F = kms.uapi.DRM_FORMAT_XRGB16161616F
    XBGR16161616F = kms.uapi.DRM_FORMAT_XBGR16161616F
    ARGB16161616F = kms.uapi.DRM_FORMAT_ARGB16161616F
    ABGR16161616F = kms.uapi.DRM_FORMAT_ABGR16161616F
    AXBXGXRX106106106106 = kms.uapi.DRM_FORMAT_AXBXGXRX106106106106
    YUYV = kms.uapi.DRM_FORMAT_YUYV
    YVYU = kms.uapi.DRM_FORMAT_YVYU
    UYVY = kms.uapi.DRM_FORMAT_UYVY
    VYUY = kms.uapi.DRM_FORMAT_VYUY
    AYUV = kms.uapi.DRM_FORMAT_AYUV
    XYUV8888 = kms.uapi.DRM_FORMAT_XYUV8888
    VUY888 = kms.uapi.DRM_FORMAT_VUY888
    VUY101010 = kms.uapi.DRM_FORMAT_VUY101010
    Y210 = kms.uapi.DRM_FORMAT_Y210
    Y212 = kms.uapi.DRM_FORMAT_Y212
    Y216 = kms.uapi.DRM_FORMAT_Y216
    Y410 = kms.uapi.DRM_FORMAT_Y410
    Y412 = kms.uapi.DRM_FORMAT_Y412
    Y416 = kms.uapi.DRM_FORMAT_Y416
    XVYU2101010 = kms.uapi.DRM_FORMAT_XVYU2101010
    XVYU12_16161616 = kms.uapi.DRM_FORMAT_XVYU12_16161616
    XVYU16161616 = kms.uapi.DRM_FORMAT_XVYU16161616
    Y0L0 = kms.uapi.DRM_FORMAT_Y0L0
    X0L0 = kms.uapi.DRM_FORMAT_X0L0
    Y0L2 = kms.uapi.DRM_FORMAT_Y0L2
    X0L2 = kms.uapi.DRM_FORMAT_X0L2
    YUV420_8BIT = kms.uapi.DRM_FORMAT_YUV420_8BIT
    YUV420_10BIT = kms.uapi.DRM_FORMAT_YUV420_10BIT
    XRGB8888_A8 = kms.uapi.DRM_FORMAT_XRGB8888_A8
    XBGR8888_A8 = kms.uapi.DRM_FORMAT_XBGR8888_A8
    RGBX8888_A8 = kms.uapi.DRM_FORMAT_RGBX8888_A8
    BGRX8888_A8 = kms.uapi.DRM_FORMAT_BGRX8888_A8
    RGB888_A8 = kms.uapi.DRM_FORMAT_RGB888_A8
    BGR888_A8 = kms.uapi.DRM_FORMAT_BGR888_A8
    RGB565_A8 = kms.uapi.DRM_FORMAT_RGB565_A8
    BGR565_A8 = kms.uapi.DRM_FORMAT_BGR565_A8
    NV12 = kms.uapi.DRM_FORMAT_NV12
    NV21 = kms.uapi.DRM_FORMAT_NV21
    NV16 = kms.uapi.DRM_FORMAT_NV16
    NV61 = kms.uapi.DRM_FORMAT_NV61
    NV24 = kms.uapi.DRM_FORMAT_NV24
    NV42 = kms.uapi.DRM_FORMAT_NV42
    NV15 = kms.uapi.DRM_FORMAT_NV15
    P210 = kms.uapi.DRM_FORMAT_P210
    P010 = kms.uapi.DRM_FORMAT_P010
    P012 = kms.uapi.DRM_FORMAT_P012
    P016 = kms.uapi.DRM_FORMAT_P016
    P030 = kms.uapi.DRM_FORMAT_P030
    Q410 = kms.uapi.DRM_FORMAT_Q410
    Q401 = kms.uapi.DRM_FORMAT_Q401
    YUV410 = kms.uapi.DRM_FORMAT_YUV410
    YVU410 = kms.uapi.DRM_FORMAT_YVU410
    YUV411 = kms.uapi.DRM_FORMAT_YUV411
    YVU411 = kms.uapi.DRM_FORMAT_YVU411
    YUV420 = kms.uapi.DRM_FORMAT_YUV420
    YVU420 = kms.uapi.DRM_FORMAT_YVU420
    YUV422 = kms.uapi.DRM_FORMAT_YUV422
    YVU422 = kms.uapi.DRM_FORMAT_YVU422
    YUV444 = kms.uapi.DRM_FORMAT_YUV444
    YVU444 = kms.uapi.DRM_FORMAT_YVU444

class PixelFormatMod(IntEnum):
    MOD_VENDOR_NONE = kms.uapi.DRM_FORMAT_MOD_VENDOR_NONE
    MOD_VENDOR_INTEL = kms.uapi.DRM_FORMAT_MOD_VENDOR_INTEL
    MOD_VENDOR_AMD = kms.uapi.DRM_FORMAT_MOD_VENDOR_AMD
    MOD_VENDOR_NVIDIA = kms.uapi.DRM_FORMAT_MOD_VENDOR_NVIDIA
    MOD_VENDOR_SAMSUNG = kms.uapi.DRM_FORMAT_MOD_VENDOR_SAMSUNG
    MOD_VENDOR_QCOM = kms.uapi.DRM_FORMAT_MOD_VENDOR_QCOM
    MOD_VENDOR_VIVANTE = kms.uapi.DRM_FORMAT_MOD_VENDOR_VIVANTE
    MOD_VENDOR_BROADCOM = kms.uapi.DRM_FORMAT_MOD_VENDOR_BROADCOM
    MOD_VENDOR_ARM = kms.uapi.DRM_FORMAT_MOD_VENDOR_ARM
    MOD_VENDOR_ALLWINNER = kms.uapi.DRM_FORMAT_MOD_VENDOR_ALLWINNER
    MOD_VENDOR_AMLOGIC = kms.uapi.DRM_FORMAT_MOD_VENDOR_AMLOGIC
    RESERVED = kms.uapi.DRM_FORMAT_RESERVED
    MOD_NONE = kms.uapi.DRM_FORMAT_MOD_NONE
    MOD_ARM_TYPE_AFBC = kms.uapi.DRM_FORMAT_MOD_ARM_TYPE_AFBC
    MOD_ARM_TYPE_MISC = kms.uapi.DRM_FORMAT_MOD_ARM_TYPE_MISC
    MOD_ARM_TYPE_AFRC = kms.uapi.DRM_FORMAT_MOD_ARM_TYPE_AFRC
