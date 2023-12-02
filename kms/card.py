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

        connector = kms.drm_mode_get_connector()

        connector.connector_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETCONNECTOR, connector, True)

        print(f"connector {id}: type: {connector.connector_type}")

    def get_default_mode(self):
        return VideoMode()

class Crtc(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_CRTC, idx)

        crtc = kms.drm_mode_crtc()

        crtc.crtc_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETCRTC, crtc, True)

        print(f"CRTC {id}: fb: {crtc.fb_id}")


class Encoder(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_ENCODER, idx)

        encoder = kms.drm_mode_get_encoder()

        encoder.encoder_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETENCODER, encoder, True)

        print(f"encoder {id}: type: {encoder.encoder_type}")

class Plane(DrmPropObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_PLANE, idx)

        plane = kms.drm_mode_get_plane()

        plane.plane_id = id

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_GETPLANE, plane, True)

        print(f"plane {id}: fb: {plane.fb_id}")

class VideoMode:
    def __init__(self) -> None:
        pass

    def to_blob(self):
        pass

class DumbFramebuffer(DrmObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_FB, idx)

class Blob(DrmObject):
    def __init__(self, card: Card, id, idx) -> None:
        super().__init__(card, id, kms.DRM_MODE_OBJECT_BLOB, idx)

        blob = kms.drm_mode_create_blob()
        blob.length = 0
        blob.data = 0
        blob.blob_id = 0

        fcntl.ioctl(card.fd, kms.DRM_IOCTL_MODE_CREATEPROPBLOB, blob, True)



class ResourceManager:
    def __init__(self, card: Card) -> None:
        self.card = card

    def reserve_connector(self, connector_str: str):
        return self.card.connectors[0]

    def reserve_crtc(self, connector: Connector):
        return self.card.crtcs[0]

    def reserve_generic_plane(self, crtc: Crtc):
        return self.card.planes[0]

