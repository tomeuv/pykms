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


class Encoder(DrmPropObject):
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

        self.handle = create_dumb.handle


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

