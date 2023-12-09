from __future__ import annotations

from enum import Enum, auto
import ctypes
import fcntl
import io
import os

import kms.uapi
import kms.pixelformats

class Card:
    def __init__(self, dev_path='/dev/dri/card0') -> None:
        self.fio = io.FileIO(dev_path,
                             opener=lambda name,_: os.open(name, os.O_RDWR | os.O_NONBLOCK))
        self.fd = self.fio.fileno()

        self.set_defaults()
        self.get_res()
        self.get_plane_res()
        self.collect_props()

        self.event_buf = bytearray(1024)

    def __del__(self):
        self.fio = None
        self.fd = -1

    def collect_props(self):
        prop_ids = set()

        for ob in [*self.crtcs, *self.connectors, *self.planes]:
            for prop_id in ob.prop_values:
                prop_ids.add(prop_id)

        props = {}

        for prop_id in prop_ids:
            prop = kms.uapi.drm_mode_get_property(prop_id=prop_id)
            fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETPROPERTY, prop, True)
            props[prop_id] = prop.name.decode("ascii")

        self._props: dict[int, str] = props

    def find_property_id(self, obj: DrmPropObject, prop_name: str):
        # We may have duplicate names
        return next(id for id in obj.prop_values if self._props[id] == prop_name)

    def find_property_name(self, prop_id):
        return self._props[prop_id]

    def set_defaults(self):
        try:
            fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_SET_MASTER, 0, False)
        except:
            print("NOT MASTER")

        cap = kms.uapi.drm_get_cap(kms.uapi.DRM_CAP_DUMB_BUFFER)
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_GET_CAP, cap, True)
        assert(cap.value)

        client_cap = kms.uapi.drm_set_client_cap(kms.uapi.DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1)
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_SET_CLIENT_CAP, client_cap, True)
        assert(client_cap.value)

        client_cap = kms.uapi.drm_set_client_cap(kms.uapi.DRM_CLIENT_CAP_ATOMIC, 1)
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_SET_CLIENT_CAP, client_cap, True)
        assert(client_cap.value)

    # XXX deprecated
    @property
    def has_atomic(self):
        return True

    def get_version(self):
        ver = kms.uapi.drm_version()
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_VERSION, ver, True)

        ver.name = kms.uapi.String(b' ' * ver.name_len)
        ver.date = kms.uapi.String(b' ' * ver.date_len)
        ver.desc = kms.uapi.String(b' ' * ver.desc_len)

        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_VERSION, ver, True)

        print(ver.name)

        return ver

    def get_res(self):
        res = kms.uapi.drm_mode_card_res()
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETRESOURCES, res, True)

        fb_ids = (ctypes.c_uint32 * res.count_fbs)()
        res.fb_id_ptr = ctypes.addressof(fb_ids)

        crtc_ids = (ctypes.c_uint32 * res.count_crtcs)()
        res.crtc_id_ptr = ctypes.addressof(crtc_ids)

        connector_ids = (ctypes.c_uint32 * res.count_connectors)()
        res.connector_id_ptr = ctypes.addressof(connector_ids)

        encoder_ids = (ctypes.c_uint32 * res.count_encoders)()
        res.encoder_id_ptr = ctypes.addressof(encoder_ids)

        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETRESOURCES, res, True)

        self.crtcs = [Crtc(self, id, idx) for idx,id in enumerate(crtc_ids)]
        self.connectors = [Connector(self, id, idx) for idx,id in enumerate(connector_ids)]
        self.encoders = [Encoder(self, id, idx) for idx,id in enumerate(encoder_ids)]

    def get_plane_res(self):
        res = kms.uapi.drm_mode_get_plane_res()
        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETPLANERESOURCES, res, True)

        plane_ids = (ctypes.c_uint32 * res.count_planes)()
        res.plane_id_ptr = ctypes.addressof(plane_ids)

        fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETPLANERESOURCES, res, True)

        self.planes = [Plane(self, id, idx) for idx,id in enumerate(plane_ids)]

    def get_object(self, id):
        return next((ob for ob in [*self.crtcs, *self.connectors, *self.encoders] if ob.id == id))

    def get_connector(self, id):
        return next((ob for ob in self.connectors if ob.id == id))

    def get_crtc(self, id):
        return next((ob for ob in self.crtcs if ob.id == id))

    def get_encoder(self, id):
        return next((ob for ob in self.encoders if ob.id == id))

    def read_events(self) -> list[DrmEvent]:
        assert(self.fio)

        buf = self.event_buf

        l = self.fio.readinto(buf)
        if not l:
            return []

        assert (l >= ctypes.sizeof(kms.uapi.drm_event))

        events = []

        i = 0
        while i < l:
            ev = kms.uapi.drm_event.from_buffer(buf, i)

            #print(f'event type{ev.type}, len {ev.length}')

            if ev.type == kms.uapi.DRM_EVENT_VBLANK:
                raise NotImplementedError()
            elif ev.type == kms.uapi.DRM_EVENT_FLIP_COMPLETE:
                vblank = kms.uapi.drm_event_vblank.from_buffer(buf, i)
                #print(vblank.sequence, vblank.tv_sec, vblank.tv_usec, vblank.crtc_id, vblank.user_data)

                time = vblank.tv_sec + vblank.tv_usec / 1000000.0;

                events.append(DrmEvent(DrmEventType.FLIP_COMPLETE, vblank.sequence, time, vblank.user_data))

            elif ev.type == kms.uapi.DRM_EVENT_CRTC_SEQUENCE:
                raise NotImplementedError()
            else:
                raise NotImplementedError()

            i += ev.length

        return events

    # XXX Deprecated
    def disable_planes(self):
        pass

class DrmEventType(Enum):
    FLIP_COMPLETE = auto()

class DrmEvent:
    def __init__(self, type, seq, time, data):
        self.type = type
        self.seq = seq
        self.time = time
        self.data = data


class DrmObject:
    def __init__(self, card: Card, id, type, idx) -> None:
        self.card = card
        self.id = id
        self.type = type
        self.idx = idx


class DrmPropObject(DrmObject):
    def __init__(self, card: Card, id, type, idx) -> None:
        super().__init__(card, id, type, idx)
        self.refresh_props()

    def refresh_props(self):
        props = kms.uapi.drm_mode_obj_get_properties()
        props.obj_id = self.id
        props.obj_type = self.type

        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_OBJ_GETPROPERTIES, props, True)

        prop_ids = (kms.uapi.c_uint32 * props.count_props)()
        props.props_ptr = ctypes.addressof(prop_ids)

        prop_values = (kms.uapi.c_uint64 * props.count_props)()
        props.prop_values_ptr = ctypes.addressof(prop_values)

        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_OBJ_GETPROPERTIES, props, True)

        self.prop_values = {int(prop_ids[i]): int(prop_values[i]) for i in range(props.count_props)}

    def get_prop_value(self, prop_name: str):
        prop_id = self.card.find_property_id(self, prop_name)
        assert(prop_id in self.prop_values)
        return self.prop_values[prop_id]

    def set_prop(self, prop, value):
        import kms.atomicreq

        areq = kms.atomicreq.AtomicReq(self.card)
        areq.add(self, prop, value)
        areq.commit_sync()

    def set_props(self, map):
        import kms.atomicreq

        areq = kms.atomicreq.AtomicReq(self.card)
        areq.add_many(self, map)
        areq.commit_sync()


class Connector(DrmPropObject):
    connector_names = {
        kms.uapi.DRM_MODE_CONNECTOR_Unknown: "Unknown",
        kms.uapi.DRM_MODE_CONNECTOR_VGA: "VGA",
        kms.uapi.DRM_MODE_CONNECTOR_DVII: "DVI-I",
        kms.uapi.DRM_MODE_CONNECTOR_DVID: "DVI-D",
        kms.uapi.DRM_MODE_CONNECTOR_DVIA: "DVI-A",
        kms.uapi.DRM_MODE_CONNECTOR_Composite: "Composite",
        kms.uapi.DRM_MODE_CONNECTOR_SVIDEO: "S-Video",
        kms.uapi.DRM_MODE_CONNECTOR_LVDS: "LVDS",
        kms.uapi.DRM_MODE_CONNECTOR_Component: "Component",
        kms.uapi.DRM_MODE_CONNECTOR_9PinDIN: "9-Pin-DIN",
        kms.uapi.DRM_MODE_CONNECTOR_DisplayPort: "DP",
        kms.uapi.DRM_MODE_CONNECTOR_HDMIA: "HDMI-A",
        kms.uapi.DRM_MODE_CONNECTOR_HDMIB: "HDMI-B",
        kms.uapi.DRM_MODE_CONNECTOR_TV: "TV",
        kms.uapi.DRM_MODE_CONNECTOR_eDP: "eDP",
        kms.uapi.DRM_MODE_CONNECTOR_VIRTUAL: "Virtual",
        kms.uapi.DRM_MODE_CONNECTOR_DSI: "DSI",
        kms.uapi.DRM_MODE_CONNECTOR_DPI: "DPI",
    }

    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.uapi.DRM_MODE_OBJECT_CONNECTOR, idx)

        res = kms.uapi.drm_mode_get_connector(connector_id=id)

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETCONNECTOR, res, True)

        encoder_ids = (kms.uapi.c_uint32 * res.count_encoders)()
        res.encoders_ptr = ctypes.addressof(encoder_ids)

        modes = (kms.uapi.drm_mode_modeinfo * res.count_modes)()
        res.modes_ptr = ctypes.addressof(modes)

        prop_ids = (kms.uapi.c_uint32 * res.count_props)()
        res.props_ptr = ctypes.addressof(prop_ids)

        prop_values = (kms.uapi.c_uint64 * res.count_props)()
        res.prop_values_ptr = ctypes.addressof(prop_values)

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETCONNECTOR, res, True)

        self.connector_res = res
        self.encoder_ids = encoder_ids
        self.modes = modes

        self.fullname = f'{Connector.connector_names[res.connector_type]}-{res.connector_type_id}'

        #print(f"connector {id}: type: {res.connector_type}, num_modes: {len(self.modes)}")

    @property
    def connected(self):
        return self.connector_res.connection in (kms.uapi.DRM_MODE_CONNECTED, kms.uapi.DRM_MODE_UNKNOWNCONNECTION)

    def get_default_mode(self):
        return self.modes[0]

    @property
    def current_crtc(self):
        assert(self.connector_res.encoder_id)
        enc = self.card.get_encoder(self.connector_res.encoder_id)
        return enc.crtc

    def __repr__(self) -> str:
        return f'Connector({self.id})'

    @property
    def possible_crtcs(self):
        crtcs = set()

        for encoder_id in self.encoder_ids:
            crtcs.update(self.card.get_encoder(encoder_id).possible_crtcs)

        return crtcs

    @property
    def encoders(self):
        return [self.card.get_encoder(eid) for eid in self.encoder_ids]


class Encoder(DrmObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.uapi.DRM_MODE_OBJECT_ENCODER, idx)

        res = kms.uapi.drm_mode_get_encoder()

        res.encoder_id = id

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETENCODER, res, True)

        self.encoder_res = res

        #print(f"encoder {id}: type: {res.encoder_type}")

    def __repr__(self) -> str:
        return f'Encoder({self.id})'

    @property
    def crtc(self):
        if self.encoder_res.crtc_id:
            return self.card.get_crtc(self.encoder_res.crtc_id)
        else:
            return None

    @property
    def possible_crtcs(self):
        return [crtc for crtc in self.card.crtcs if self.encoder_res.possible_crtcs & (1 << crtc.idx)]

    @property
    def encoder_type(self):
        return kms.EncoderType(self.encoder_res.encoder_type)


class Crtc(DrmPropObject):
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

    # XXX deprecated
    def set_mode(self, connector, fb, mode):
        modeb = kms.Blob(self.card, mode)
        crtc = self
        plane = crtc.get_possible_planes()[0]

        req = kms.AtomicReq(self.card)

        req.add_connector(connector, crtc)
        req.add_crtc(crtc, modeb)
        req.add_plane(plane, fb, crtc, dst=(0, 0, mode.hdisplay, mode.vdisplay))

        req.commit_sync(allow_modeset = True)

    @property
    def primary_plane(self):
        plane = next((p for p in self.get_possible_planes() if p.type == kms.PlaneType.Primary and p.crtc_id == self.id), None)
        if plane:
            return plane
        plane = next((p for p in self.get_possible_planes() if p.type == kms.PlaneType.Primary), None)
        if plane:
            return plane
        plane = next((p for p in self.get_possible_planes()), None)
        if plane:
            return plane
        raise Exception("No primary plane")


class Plane(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.uapi.DRM_MODE_OBJECT_PLANE, idx)

        plane = kms.uapi.drm_mode_get_plane()

        plane.plane_id = id

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETPLANE, plane, True)

        format_types = (kms.uapi.c_uint32 * plane.count_format_types)()
        plane.format_type_ptr = ctypes.addressof(format_types)

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_GETPLANE, plane, True)

        self.format_types = format_types
        self.res = plane

        #print(f"plane {id}: fb: {plane.fb_id}")

    def __repr__(self) -> str:
        return f'Plane({self.id})'

    def supports_crtc(self, crtc: Crtc):
        return self.res.possible_crtcs & (1 << crtc.idx)

    @property
    def plane_type(self):
        return kms.PlaneType(self.get_prop_value('type'))

    def supports_format(self, format):
        return format in self.format_types

    @property
    def crtc_id(self):
        return self.res.crtc_id

    @property
    def fb_id(self):
        return self.res.fb_id


class DumbFramebuffer(DrmObject):
    class DumbFramebufferPlane:
        def __init__(self, handle: int, stride: int, size: int) -> None:
            self.handle = handle
            self.stride = stride
            self.size = size
            self.prime_fd = -1
            self.offset = 0
            self.map = 0

    def __init__(self, card: Card, width, height, fourcc: str | int) -> None:
        self._deleted = True

        if type(fourcc) is str:
            fourcc = kms.str_to_fourcc(fourcc)

        self.width = width
        self.height = height
        self.format = fourcc
        self.planes = []

        format_info = kms.pixelformats.get_pixel_format_info(fourcc)

        for pi in format_info.planes:
            creq = kms.uapi.drm_mode_create_dumb()
            creq.width = width
            creq.height = height // pi.ysub

            # For fully planar YUV buffers, the chroma planes don't combine
            # U and V components, their width must thus be divided by the
            # horizontal subsampling factor.

            if format_info.colortype == kms.pixelformats.PixelColorType.YUV and len(format_info.planes) == 3:
                creq.width //= pi.xsub
            creq.bpp = pi.bitspp

            fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_CREATE_DUMB, creq, True)

            plane = DumbFramebuffer.DumbFramebufferPlane(handle=creq.handle,
                                                         stride=creq.pitch,
                                                         size=creq.height * creq.pitch)

            self.planes.append(plane)

        fb2 = kms.uapi.struct_drm_mode_fb_cmd2()
        fb2.width = width
        fb2.height = height
        fb2.pixel_format = fourcc
        fb2.handles = (ctypes.c_uint * 4)(*[p.handle for p in self.planes])
        fb2.pitches = (ctypes.c_uint * 4)(*[p.stride for p in self.planes])
        fb2.offsets = (ctypes.c_uint * 4)(*[p.offset for p in self.planes])

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_ADDFB2, fb2, True)

        super().__init__(card, fb2.fb_id, kms.uapi.DRM_MODE_OBJECT_FB, -1)

        self._deleted = False

    def __del__(self):
        if self._deleted or self.card.fd == -1:
            return

        for p in self.planes:
            if p.prime_fd != -1:
                os.close(p.prime_fd)

            if p.map:
                p.map.close()

        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_RMFB, ctypes.c_uint32(self.id), False)

        for p in self.planes:
            dumb = kms.uapi.drm_mode_destroy_dumb()
            dumb.handle = p.handle
            fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_DESTROY_DUMB, dumb, True)

        self._deleted = True

    def __repr__(self) -> str:
        return f'DumbFramebuffer({self.id})'

    def mmap(self):
        return [self.map(pidx) for pidx in range(len(self.planes))]

    def map(self, plane_idx):
        import mmap

        p = self.planes[plane_idx]

        if p.offset == 0:
            map_dumb = kms.uapi.struct_drm_mode_map_dumb()
            map_dumb.handle = p.handle
            fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_MAP_DUMB, map_dumb, True)
            p.offset = map_dumb.offset

        if p.map == 0:
            p.map = mmap.mmap(self.card.fd, p.size,
                              mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE,
                              offset=p.offset)

        return p.map

    def size(self, plane_idx):
        return self.planes[plane_idx].size

    def fd(self, plane_idx):
        p = self.planes[plane_idx]

        if p.prime_fd != -1:
            return p.prime_fd

        args = kms.uapi.drm_prime_handle()
        args.handle = self.planes[plane_idx].handle
        args.fd = -1
        args.flags = os.O_CLOEXEC | os.O_RDWR
        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_PRIME_HANDLE_TO_FD, args, True)

        p.prime_fd = args.fd

        return p.prime_fd


class Blob(DrmObject):
    def __init__(self, card: Card, data) -> None:
        blob = kms.uapi.drm_mode_create_blob()
        blob.data = ctypes.addressof(data)
        blob.length = ctypes.sizeof(data)

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_CREATEPROPBLOB, blob, True)

        super().__init__(card, blob.blob_id, kms.uapi.DRM_MODE_OBJECT_BLOB, -1)

    def __del__(self):
        if self.card.fd == -1 or self.id is None:
            return

        blob = kms.uapi.drm_mode_destroy_blob()
        blob.blob_id = self.id
        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_DESTROYPROPBLOB, blob, True)
        self.id = None

    def __repr__(self) -> str:
        return f'Blob({self.id})'
