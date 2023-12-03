from __future__ import annotations

import kms
import kms.uapi

class ResourceManager:
    from kms.card import Card, Connector, Crtc

    def __init__(self, card: Card) -> None:
        self.card = card
        self.reserved_connectors = set()
        self.reserved_crtcs = set()
        self.reserved_planes = set()

    def find_connector(self):
        for c in self.card.connectors:
            if not c.connected:
                continue

            if c in self.reserved_connectors:
                continue

            return c

        raise Exception("Available connector not found")

    def resolve_connector(self, name: str):
        if name.startswith('@'):
            id = int(name[1:])
            conn = self.card.get_connector(id)

            if conn in self.reserved_connectors:
                raise Exception("Connector already reserved")

            return conn

        try:
            idx = int(name)

            if idx >= len(self.card.connectors):
                raise Exception("Connector idx too high")

            conn = self.card.connectors[idx]

            if conn in self.reserved_connectors:
                raise Exception("Connector already reserved")

            return conn
        except:
            pass

        name = name.lower()

        for c in self.card.connectors:
            if name not in c.fullname.lower():
                continue

            if c in self.reserved_connectors:
                raise Exception("Connector already reserved")

            return c

        raise Exception("Connector not found")

    def reserve_connector(self, name: str):
        if not name:
            conn = self.find_connector()
        else:
            conn = self.resolve_connector(name)

        self.reserved_connectors.add(conn)

        return conn

    def reserve_crtc(self, connector: Connector):
        crtc = connector.get_current_crtc()

        if crtc in self.reserved_crtcs:
            raise Exception("Crtc not found")

        self.reserved_crtcs.add(crtc)

        return crtc

    def reserve_generic_plane(self, crtc: Crtc, format=None):
        if format and type(format) == str:
            format = kms.str_to_fourcc(format)

        for plane in crtc.get_possible_planes():
            if plane in self.reserved_planes:
                continue

            if plane.plane_type == kms.uapi.DRM_PLANE_TYPE_CURSOR:
                continue

            if format and not plane.supports_format(format):
                continue;

            self.reserved_planes.add(plane)

            return plane

        raise Exception("Plane not found")
