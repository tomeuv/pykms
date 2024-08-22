
import ctypes

import os
import fcntl

class struct_dma_heap_allocation_data(ctypes.Structure):
    __slots__ = ['len', 'fd', 'fd_flags', 'heap_flags']
    _fields_ = [('len', ctypes.c_uint64),
                ('fd', ctypes.c_uint32),
                ('fd_flags', ctypes.c_uint32),
                ('heap_flags', ctypes.c_uint64)]

DMA_HEAP_IOC_MAGIC = 'H'

_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = (_IOC_NRSHIFT + _IOC_NRBITS)
_IOC_SIZESHIFT = (_IOC_TYPESHIFT + _IOC_TYPEBITS)
_IOC_DIRSHIFT = (_IOC_SIZESHIFT + _IOC_SIZEBITS)

_IOC_NONE = 0
_IOC_WRITE = 1
_IOC_READ = 2

def _IOC(dir, type, nr, size):
    return ((((dir << _IOC_DIRSHIFT) | (ord(type) << _IOC_TYPESHIFT)) | (nr << _IOC_NRSHIFT)) | (size << _IOC_SIZESHIFT))

def _IOC_TYPECHECK(t):
    return ctypes.sizeof(t)

def _IOWR(type, nr, size):
    return (_IOC ((_IOC_READ | _IOC_WRITE), type, nr, (_IOC_TYPECHECK (size))))

DMA_HEAP_IOCTL_ALLOC = _IOWR(DMA_HEAP_IOC_MAGIC, 0x0, struct_dma_heap_allocation_data)

def dma_heap_alloc(len: int, heap_name: str):
    fd = os.open('/dev/dma_heap/' + heap_name, os.O_CLOEXEC | os.O_RDWR)

    try:
        buf_data = struct_dma_heap_allocation_data()
        buf_data.len = len
        buf_data.fd_flags = os.O_CLOEXEC | os.O_RDWR
        fcntl.ioctl(fd, DMA_HEAP_IOCTL_ALLOC, buf_data, True)
    finally:
        os.close(fd)

    return buf_data.fd
