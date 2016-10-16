#!/usr/bin/env python

import json
import urllib2

base_image_url="https://images.joyent.com/images"

index_raw = urllib2.urlopen(base_image_url).read()

index = json.loads(index_raw)

print index