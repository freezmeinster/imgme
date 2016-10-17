#!/usr/bin/env python

import json
import urllib2
import os
import settings

BASE_DIR=os.path.dirname(__file__)

def update_index():
    index_raw = urllib2.urlopen(settings.BASE_IMAGES_URL).read()
    with open(os.path.join(BASE_DIR,"index.json"), "wb") as index_file :
        index_file.write(index_raw)

def read_index():
    index_raw = open(os.path.join(BASE_DIR,"index.json")).read()
    index = json.loads(index_raw)
    return index
    
if __name__ == '__main__':
    update_index()