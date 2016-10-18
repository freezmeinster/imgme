#!/usr/bin/env python

import json
import urllib2
import os
import argparse
import hashlib
import shutil
from urllib import urlretrieve

import settings
from formator import indent

BASE_DIR=os.path.dirname(__file__)

def checksum_sha1(filename):
    sha1 = hashlib.sha1()
    with open(filename,'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            sha1.update(chunk)
    return sha1.hexdigest()

def update_index():
    index_raw = urllib2.urlopen(settings.BASE_IMAGES_URL).read()
    with open(os.path.join(BASE_DIR,"index.json"), "wb") as index_file :
        index_file.write(index_raw)

def update_image_list():
    html_index = os.path.join(settings.MIRROR_DEST_DIR, 'index.html')
    image_list = list()
    if os.path.isdir(settings.MIRROR_DEST_DIR) :
        image_raw = os.listdir(settings.MIRROR_DEST_DIR)
        image_raw.remove("index.html")
        for uid in image_raw :
            image = read_manifest(uid)
            image_list.append(image)
    with open(html_index, 'wb') as html_file :
        html_file.write(json.dumps(image_list))

def read_index(as_dict=False):
    index_raw = open(os.path.join(BASE_DIR,"index.json")).read()
    index = json.loads(index_raw)
    if as_dict :
        res = dict()
        for img in index :
            res[img.get("uuid")] = img
        return res
    return index

def read_uuid(uuid):    
    index = read_index(as_dict=True)
    return index.get(uuid)

def read_manifest(uuid):
    dest_dir = os.path.join(settings.MIRROR_DEST_DIR, uuid)
    manifest_path = os.path.join(dest_dir, "index.html")
    manifest = open(manifest_path ,'rb').read()
    index = json.loads(manifest)
    return index
    
def update_by_uuid(uuid):
    dest_dir = os.path.join(settings.MIRROR_DEST_DIR, uuid)
    file_path = os.path.join(dest_dir, "file")
    manifest = read_uuid(uuid)
    if not os.path.isdir(dest_dir) :
        print "Creating target directory %s" % dest_dir
        os.mkdir(dest_dir)
    uuid_manifest = open(os.path.join(dest_dir, "index.html"), 'wb')
    uuid_manifest.write(json.dumps(manifest))
    if os.path.isfile(file_path) :
        print "Image file %s apear, checksuming file" % file_path
        checksum = checksum_sha1(file_path)
        if checksum == manifest["files"][0]['sha1'] :        
            print "Image file %s already synced" % file_path
        else :
            print "Downloading file"
            url = settings.BASE_IMAGES_URL + "/" + uuid + "/file"
            urlretrieve(url,file_path)
            print "Download Done"
    else :
        print "Downloading file"
        url = settings.BASE_IMAGES_URL + "/" + uuid + "/file"
        urlretrieve(url,file_path)
        print "Download Done"
    update_image_list()
            

def verify_uuid(uuid):
    uuid_list = [ image.get("uuid") for image in read_index() ]
    if uuid in uuid_list :
        return True
    else :
        return False

def list_available():
    index = read_index()
    labels = ['UUID', 'Name', 'Type', 'OS', 'Version', 'Pub Date']
    rows = list()
    for image in index :
        uuid = image.get("uuid")
        name = image.get("name")
        ty = image.get("type")
        os = image.get("os")
        desc = image.get("version")
        pub = image.get("published_at")
        rows.append([uuid, name, ty, os, desc, pub])
    print indent([labels]+rows, hasHeader=True)
    
def list_owned():
    labels = ['UUID', 'Name', 'Type', 'OS', 'Version', 'Pub Date']
    rows = list()
    if os.path.isdir(settings.MIRROR_DEST_DIR) :
        list_uuid = os.listdir(settings.MIRROR_DEST_DIR)
        list_uuid.remove("index.html") 
        for uuid in list_uuid:
            image = read_manifest(uuid)
            uuid = image.get("uuid")
            name = image.get("name")
            ty = image.get("type")
            o_s = image.get("os")
            desc = image.get("version")
            pub = image.get("published_at")
            rows.append([uuid, name, ty, o_s, desc, pub])
        print indent([labels]+rows, hasHeader=True)
            
    else :
        print "Image target directory %s not exist, please make the directory" % settings.MIRROR_DEST_DIR 

def delete_image(uuid):
    image_dir = os.path.join(settings.MIRROR_DEST_DIR, uuid)
    print "Deleting image %s" % uuid
    if os.path.isdir(image_dir):
        shutil.rmtree(image_dir)
    update_image_list()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-u", "--update", action="store_true", help="Update index manifest")
    parser.add_argument("-ui", "--update-image-list", action="store_true", help="Update html index list")
    parser.add_argument("-la", "--list-available", action="store_true", help="List available image in index manifest")
    parser.add_argument("-lo", "--list-owned", action="store_true", help="List owned images")
    parser.add_argument("-d", "--delete", type=str, help="Delete image")
    parser.add_argument("uuid",  nargs='?', type=str, help="UUID of image")
    args = parser.parse_args()
    if args.update_image_list :
        print "Updating html index manifest"
        update_image_list()
    elif args.update :
        print "Updating index manifest"
        update_index()
        print "Done updating manifest"
    elif args.delete :
        delete_image(args.delete)
    elif args.list_available :
        list_available()
    elif args.list_owned :
        list_owned()
    elif args.uuid :
        if verify_uuid(args.uuid):
            update_by_uuid(args.uuid)
        else :
            print "UUID invalid !"