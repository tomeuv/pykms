import os
import fcntl
import ctypes
import kms

class Card:
    def __init__(self, dev_path='/dev/dri/card0') -> None:
        self.fd = os.open(dev_path, os.O_RDWR | os.O_NONBLOCK)
        assert(self.fd != -1)

        self.set_defaults()
        self.get_res()
        self.get_plane_res()
        self.collect_props()

    def collect_props(self):
        prop_ids = set()

        for ob in [*self.crtcs, *self.connectors, *self.planes]:
            for prop_id in ob.prop_values:
                prop_ids.add(prop_id)

        props = {}

        for prop_id in prop_ids:
            prop = kms.drm_mode_get_property(prop_id=prop_id)
            fcntl.ioctl(self.fd, kms.DRM_IOCTL_MODE_GETPROPERTY, prop, True)
            props[prop.name.decode("ascii")] = prop_id

        self.props: dict[str, int] = props


    def set_defaults(self):
        try:
            fcntl.ioctl(self.fd, kms.DRM_IOCTL_SET_MASTER, 0, False)
        except:
            print("NOT MASTER")


        cap = kms.drm_get_cap(kms.DRM_CAP_DUMB_BUFFER)
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_GET_CAP, cap, True)
        assert(cap.value)

        client_cap = kms.drm_set_client_cap(kms.DRM_CLIENT_CAP_UNIVERSAL_PLANES, 1)
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_SET_CLIENT_CAP, client_cap, True)
        assert(client_cap.value)

        client_cap = kms.drm_set_client_cap(kms.DRM_CLIENT_CAP_ATOMIC, 1)
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_SET_CLIENT_CAP, client_cap, True)
        assert(client_cap.value)

    def get_version(self):
        ver = kms.drm_version()
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_VERSION, ver, True)

        ver.name = kms.String(b' ' * ver.name_len)
        ver.date = kms.String(b' ' * ver.date_len)
        ver.desc = kms.String(b' ' * ver.desc_len)

        fcntl.ioctl(self.fd, kms.DRM_IOCTL_VERSION, ver, True)

        print(ver.name)

        return ver

    def get_res(self):
        res = kms.drm_mode_card_res()
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_MODE_GETRESOURCES, res, True)

        fb_ids = (ctypes.c_uint32 * res.count_fbs)()
        res.fb_id_ptr = ctypes.addressof(fb_ids)

        crtc_ids = (ctypes.c_uint32 * res.count_crtcs)()
        res.crtc_id_ptr = ctypes.addressof(crtc_ids)

        connector_ids = (ctypes.c_uint32 * res.count_connectors)()
        res.connector_id_ptr = ctypes.addressof(connector_ids)

        encoder_ids = (ctypes.c_uint32 * res.count_encoders)()
        res.encoder_id_ptr = ctypes.addressof(encoder_ids)

        fcntl.ioctl(self.fd, kms.DRM_IOCTL_MODE_GETRESOURCES, res, True)

        self.crtcs = [Crtc(self, id, idx) for idx,id in enumerate(crtc_ids)]
        self.connectors = [Connector(self, id, idx) for idx,id in enumerate(connector_ids)]
        self.encoders = [Encoder(self, id, idx) for idx,id in enumerate(encoder_ids)]

    def get_plane_res(self):
        res = kms.drm_mode_get_plane_res()
        fcntl.ioctl(self.fd, kms.DRM_IOCTL_MODE_GETPLANERESOURCES, res, True)

        plane_ids = (ctypes.c_uint32 * res.count_planes)()
        res.plane_id_ptr = ctypes.addressof(plane_ids)

        fcntl.ioctl(self.fd, kms.DRM_IOCTL_MODE_GETPLANERESOURCES, res, True)

        self.planes = [Plane(self, id, idx) for idx,id in enumerate(plane_ids)]


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
        props = kms.drm_mode_obj_get_properties()
        props.obj_id = self.id
        props.obj_type = self.type

        fcntl.ioctl(self.card.fd, kms.DRM_IOCTL_MODE_OBJ_GETPROPERTIES, props, True)

        prop_ids = (kms.c_uint32 * props.count_props)()
        props.props_ptr = ctypes.addressof(prop_ids)

        prop_values = (kms.c_uint64 * props.count_props)()
        props.prop_values_ptr = ctypes.addressof(prop_values)

        fcntl.ioctl(self.card.fd, kms.DRM_IOCTL_MODE_OBJ_GETPROPERTIES, props, True)

        self.prop_values = {int(prop_ids[i]): int(prop_values[i]) for i in range(props.count_props)}


class Connector(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_CONNECTOR, idx)

        res = kms.drm_mode_get_connector(connector_id=id)

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETCONNECTOR, res, True)

        encoder_ids = (kms.c_uint32 * res.count_encoders)()
        res.encoders_ptr = ctypes.addressof(encoder_ids)

        modes = (kms.drm_mode_modeinfo * res.count_modes)()
        res.modes_ptr = ctypes.addressof(modes)

        prop_ids = (kms.c_uint32 * res.count_props)()
        res.props_ptr = ctypes.addressof(prop_ids)

        prop_values = (kms.c_uint64 * res.count_props)()
        res.prop_values_ptr = ctypes.addressof(prop_values)

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETCONNECTOR, res, True)

        self.connector_res = res
        self.encoder_ids = encoder_ids
        self.modes = modes

        print(f"connector {id}: type: {res.connector_type}, num_modes: {len(self.modes)}")

    def get_default_mode(self):
        return self.modes[0]

    def __repr__(self) -> str:
        return f'Connector({self.id})'


class Crtc(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_CRTC, idx)

        crtc = kms.drm_mode_crtc()

        crtc.crtc_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETCRTC, crtc, True)

        print(f"CRTC {id}: fb: {crtc.fb_id}")

    def __repr__(self) -> str:
        return f'Crtc({self.id})'


class Encoder(DrmObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_ENCODER, idx)

        encoder = kms.drm_mode_get_encoder()

        encoder.encoder_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETENCODER, encoder, True)

        print(f"encoder {id}: type: {encoder.encoder_type}")

    def __repr__(self) -> str:
        return f'Encoder({self.id})'


class Plane(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_PLANE, idx)

        plane = kms.drm_mode_get_plane()

        plane.plane_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETPLANE, plane, True)

        print(f"plane {id}: fb: {plane.fb_id}")

    def __repr__(self) -> str:
        return f'Plane({self.id})'


class DumbFramebuffer(DrmObject):
    def __init__(self, card: Card, width, height, fourcc) -> None:
        create_dumb = kms.drm_mode_create_dumb()
        create_dumb.width = width
        create_dumb.height = height
        create_dumb.bpp = 32 # XXX
        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_CREATE_DUMB, create_dumb, True)

        super().__init__(card, -1, kms.DRM_MODE_OBJECT_FB, -1)

        self.width = width
        self.height = height
        self.handle = create_dumb.handle

    def __repr__(self) -> str:
        return f'DumbFramebuffer({self.handle})'


class Blob(DrmObject):
    def __init__(self, card: Card, ob) -> None:
        blob = kms.drm_mode_create_blob()
        blob.data = ctypes.addressof(ob)
        blob.length = ctypes.sizeof(ob)

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_CREATEPROPBLOB, blob, True)

        super().__init__(card, blob.blob_id, kms.DRM_MODE_OBJECT_BLOB, -1)

    def __repr__(self) -> str:
        return f'Blob({self.id})'



class ResourceManager:
    def __init__(self, card: Card) -> None:
        self.card = card

    def reserve_connector(self, connector_str: str):
        return self.card.connectors[3]

    def reserve_crtc(self, connector: Connector):
        return self.card.crtcs[0]

    def reserve_generic_plane(self, crtc: Crtc):
        return self.card.planes[0]


class AtomicReq:
    def __init__(self, card: Card) -> None:
        self.card = card
        self.props = [] # (ob_id, prop_id, value)

    def commit(self, allow_modeset = False):

        # Sort the list by object ID, then by property ID
        props = sorted(self.props, key=lambda tuple: (tuple[0], tuple[1]))

        print(props)

        import itertools

        obj_prop_counts = {}
        for k, g in itertools.groupby(props, lambda p: p[0]):
            obj_prop_counts[k] = len(list(g))

        print(obj_prop_counts)

        num_obs = len(obj_prop_counts)
        num_props = len(props)

        atomic = kms.struct_drm_mode_atomic()

        objs = (kms.c_uint32 * num_obs)()
        count_props = (kms.c_uint32 * num_obs)()
        prop_ids = (kms.c_uint32 * num_props)()
        prop_values = (kms.c_uint64 * num_props)()

        for idx,ob_id in enumerate(sorted(obj_prop_counts)):
            objs[idx] = ob_id
            count_props[idx] = obj_prop_counts[ob_id]

        for idx,p in enumerate(props):
            prop_id = p[1]
            prop_value = p[2]

            prop_ids[idx] = prop_id
            prop_values[idx] = prop_value

        atomic.objs_ptr = ctypes.addressof(objs)
        atomic.count_props_ptr = ctypes.addressof(count_props)
        atomic.props_ptr = ctypes.addressof(prop_ids)
        atomic.prop_values_ptr = ctypes.addressof(prop_values)

        atomic.flags = kms.DRM_MODE_PAGE_FLIP_EVENT | kms.DRM_MODE_ATOMIC_NONBLOCK

        if allow_modeset:
            atomic.flags |= kms.DRM_MODE_ATOMIC_ALLOW_MODESET

        fcntl.ioctl(self.card.fd, kms.DRM_IOCTL_MODE_ATOMIC, atomic, True)

    def commit_sync(self, allow_modeset = False):
        self.commit(allow_modeset)

    def add_single(self, ob: DrmObject | int, prop: str | int, value: int):
        if type(ob) == int:
            ob_id = ob
        elif isinstance(ob, DrmObject):
            ob_id = ob.id
        else:
            raise Exception("Bad object")

        if type(prop) == int:
            prop_id = prop
        elif type(prop) == str:
            prop_id = self.card.props[prop]
        else:
            raise Exception("Bad prop")

        self.props.append((ob_id, prop_id, value))

    def add_many(self, ob: DrmObject | int, map: dict):
        for prop, value in map.items():
            self.add_single(ob, prop, value)

    def add(self, ob: DrmObject | int, *argv):
        if len(argv) == 2:
            self.add_single(ob, *argv)
        elif len(argv) == 1:
            self.add_many(ob, *argv)
        else:
            raise Exception("Bad add() call")

    def add_connector(self, connector: Connector, crtc: Crtc):
        self.add(connector.id, "CRTC_ID", crtc.id if crtc else 0)

    def add_crtc(self, crtc: Crtc, mode_blob):
        if mode_blob:
            self.add(crtc.id, {"ACTIVE": 1, "MODE_ID": mode_blob.id})
        else:
            self.add(crtc.id, {"ACTIVE": 0, "MODE_ID": 0})

    def add_plane(self, plane, fb, crtc,
                               src=None, dst=None, zpos=None,
                               params={}):
        if not src and fb:
            src = (0, 0, fb.width, fb.height)

        if not dst:
            dst = src

        m = {"FB_ID": fb.id if fb else 0,
             "CRTC_ID": crtc.id if crtc else 0}

        if src is not None:
            src_x = int(round(src[0] * 0x10000))
            src_y = int(round(src[1] * 0x10000))
            src_w = int(round(src[2] * 0x10000))
            src_h = int(round(src[3] * 0x10000))

            m["SRC_X"] = src_x
            m["SRC_Y"] = src_y
            m["SRC_W"] = src_w
            m["SRC_H"] = src_h

        if dst is not None:
            crtc_x = int(round(dst[0]))
            crtc_y = int(round(dst[1]))
            crtc_w = int(round(dst[2]))
            crtc_h = int(round(dst[3]))

            m["CRTC_X"] = crtc_x
            m["CRTC_Y"] = crtc_y
            m["CRTC_W"] = crtc_w
            m["CRTC_H"] = crtc_h

        if zpos is not None:
            m["zpos"] = zpos

        m.update(params)

        self.add(plane, m)
