#!/usr/bin/python3

import kms

card = kms.Card()

for ob in card.connectors:
    print(ob)

for ob in card.encoders:
    print(ob)

for ob in card.crtcs:
    print(ob)

for ob in card.planes:
    print(ob)

    for id,val in ob.prop_values.items():
        print(id, val)
