#!/usr/bin/env python

import json
import urllib2
import os

BASE_DIR=os.path.dirname(__file__)

base_image_url="https://images.joyent.com/images"

# index_raw = urllib2.urlopen(base_image_url).read()

index_raw = open(os.path.join(BASE_DIR,"index.json")).read()

index = json.loads(index_raw)

print index[0]