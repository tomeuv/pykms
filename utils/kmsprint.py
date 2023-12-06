#!/usr/bin/python3
import time

ts1 = time.perf_counter()

import kms.uapi

ts2 = time.perf_counter()

print(ts2 - ts1)

exit(0)

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
