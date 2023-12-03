from __future__ import annotations

import ctypes
import fcntl
import itertools
import kms
import kms.uapi

class AtomicReq:
    def __init__(self, card: kms.Card) -> None:
        self.card = card
        self.props = [] # (ob_id, prop_id, value)

    def commit(self, allow_modeset = False):

        # Sort the list by object ID, then by property ID
        props = sorted(self.props, key=lambda tuple: (tuple[0], tuple[1]))

        print(props)

        obj_prop_counts = {}
        for k, g in itertools.groupby(props, lambda p: p[0]):
            obj_prop_counts[k] = len(list(g))

        print(obj_prop_counts)

        num_obs = len(obj_prop_counts)
        num_props = len(props)

        atomic = kms.uapi.struct_drm_mode_atomic()

        objs = (kms.uapi.c_uint32 * num_obs)()
        count_props = (kms.uapi.c_uint32 * num_obs)()
        prop_ids = (kms.uapi.c_uint32 * num_props)()
        prop_values = (kms.uapi.c_uint64 * num_props)()

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

        atomic.flags = kms.uapi.DRM_MODE_PAGE_FLIP_EVENT | kms.uapi.DRM_MODE_ATOMIC_NONBLOCK

        if allow_modeset:
            atomic.flags |= kms.uapi.DRM_MODE_ATOMIC_ALLOW_MODESET

        pidx = 0
        for oidx in range(len(objs)):
            oid = objs[oidx]
            prop_count = count_props[oidx]

            print(f"== {oid}, {prop_count}")

            for _ in range(prop_count):
                prop_id = prop_ids[pidx]
                prop_value = prop_values[pidx]

                print(f"  {self.card.find_property_name(prop_id)} = {prop_value}")

                pidx += 1



        fcntl.ioctl(self.card.fd, kms.uapi.DRM_IOCTL_MODE_ATOMIC, atomic, True)

    def commit_sync(self, allow_modeset = False):
        self.commit(allow_modeset)

    def add_single(self, ob: kms.DrmObject | int, prop: str | int, value: int):
        if type(ob) == int:
            ob_id = ob
        elif isinstance(ob, kms.DrmObject):
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

    def add_many(self, ob: kms.DrmObject | int, map: dict):
        for prop, value in map.items():
            self.add_single(ob, prop, value)

    def add(self, ob: kms.DrmObject | int, *argv):
        if len(argv) == 2:
            self.add_single(ob, *argv)
        elif len(argv) == 1:
            self.add_many(ob, *argv)
        else:
            raise Exception("Bad add() call")

    def add_connector(self, connector: kms.Connector, crtc: kms.Crtc):
        self.add(connector.id, "CRTC_ID", crtc.id if crtc else 0)

    def add_crtc(self, crtc: kms.Crtc, mode_blob):
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
