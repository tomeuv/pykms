from enum import Enum
import kms.uapi
from typing import NamedTuple

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

    raise Exception("Pixel format not found")

# XXX create PixelFormat "enum" dynamically
# Do we need this? Create a static list?
PixelFormat = type("PixelFormat", (object, ),
                   {p[1]:p[0] for p in formats})
