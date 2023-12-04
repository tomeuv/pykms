from __future__ import annotations

import ctypes
import fcntl
import io
import os

import kms.uapi

class Card:
    def __init__(self, dev_path='/dev/dri/card0') -> None:
        self.fio = io.FileIO(dev_path,
                             opener=lambda name,f: os.open(name, os.O_RDWR | os.O_NONBLOCK))
        self.fd = self.fio.fileno()

        self.set_defaults()
        self.get_res()
        self.get_plane_res()
        self.collect_props()

        self.event_buf = bytearray(1024)

    def collect_props(self):
        prop_ids = set()

        for ob in [*self.crtcs, *self.connectors, *self.planes]:
            for prop_id in ob.prop_values:
                prop_ids.add(prop_id)

        props = {}

        for prop_id in prop_ids:
            prop = kms.uapi.drm_mode_get_property(prop_id=prop_id)
            fcntl.ioctl(self.fd, kms.uapi.DRM_IOCTL_MODE_GETPROPERTY, prop, True)
            props[prop.name.decode("ascii")] = prop_id

        self.props: dict[str, int] = props

    def find_property_id(self, prop_name):
        return self.props[prop_name]

    def find_property_name(self, prop_id):
        return next(n for n in self.props if self.props[n] == prop_id)

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

                events.append(DrmEvent(ev.type, vblank))

            elif ev.type == kms.uapi.DRM_EVENT_CRTC_SEQUENCE:
                raise NotImplementedError()
            else:
                raise NotImplementedError()

            i += ev.length

        return events

class DrmEvent:
    DRM_EVENT_FLIP_COMPLETE = kms.uapi.DRM_EVENT_FLIP_COMPLETE

    def __init__(self, type, data) -> None:
        self.type = type
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
        assert(prop_name in self.card.props)
        prop_id = self.card.props[prop_name]
        assert(prop_id in self.prop_values)
        return self.prop_values[prop_id]


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

    def get_current_crtc(self):
        assert(self.connector_res.encoder_id)
        enc = self.card.get_encoder(self.connector_res.encoder_id)
        return enc.get_crtc()

    def __repr__(self) -> str:
        return f'Connector({self.id})'


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

    def get_crtc(self):
        assert(self.encoder_res.crtc_id)
        crtc = self.card.get_crtc(self.encoder_res.crtc_id)
        return crtc


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
        return self.get_prop_value('type')

    def supports_format(self, format):
        return format in self.format_types


class DumbFramebuffer(DrmObject):
    def __init__(self, card: Card, width, height, fourcc: str | int) -> None:
        bitspp = 32 # XXX

        if type(fourcc) is str:
            fourcc = kms.str_to_fourcc(fourcc)

        create_dumb = kms.uapi.drm_mode_create_dumb()
        create_dumb.width = width
        create_dumb.height = height
        create_dumb.bpp = bitspp # XXX
        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_CREATE_DUMB, create_dumb, True)

        self.width = width
        self.height = height
        self.handle = create_dumb.handle

        self.size = width * bitspp // 8 * height

        fb2 = kms.uapi.struct_drm_mode_fb_cmd2()
        fb2.width = width
        fb2.height = height
        fb2.pixel_format = fourcc
        fb2.handles[0] = self.handle
        fb2.pitches[0] = width * bitspp // 8

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_ADDFB2, fb2, True)

        super().__init__(card, fb2.fb_id, kms.uapi.DRM_MODE_OBJECT_FB, -1)

    def __repr__(self) -> str:
        return f'DumbFramebuffer({self.handle})'

    def mmap(self):
        import mmap

        map_dumb = kms.uapi.struct_drm_mode_map_dumb()
        map_dumb.handle = self.handle

        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_MAP_DUMB, map_dumb, True)

        return mmap.mmap(self.card.fd, self.size, mmap.MAP_SHARED, mmap.PROT_READ | mmap.PROT_WRITE, offset=map_dumb.offset)



class Blob(DrmObject):
    def __init__(self, card: Card, ob) -> None:
        blob = kms.uapi.drm_mode_create_blob()
        blob.data = ctypes.addressof(ob)
        blob.length = ctypes.sizeof(ob)

        fcntl.ioctl(card.fd, kms.uapi.DRM_IOCTL_MODE_CREATEPROPBLOB, blob, True)

        super().__init__(card, blob.blob_id, kms.uapi.DRM_MODE_OBJECT_BLOB, -1)

    def __repr__(self) -> str:
        return f'Blob({self.id})'
