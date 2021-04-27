import requests
import UnityPy
import re
import os

from lib import base_api, asset_api, ASSETS, RES, AssetBatchConverter


# init
RAW = os.path.join(ASSETS, "raw")
EXT = os.path.join(ASSETS, "extracted")

def main():
    TODO = [
        os.path.join(root, f)[len(RAW)+1:]
        for root, dirs, files in os.walk(RAW)
        for f in files
    ]
    for i, name in enumerate(TODO):
            print(f"{i+1}/{len(TODO)} : {name}")
            extract_asset(os.path.join(RAW, name), get_path(EXT, name))


def get_path(path, name):
    fp = os.path.join(path, *name.split("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def extract_asset(inp, path):
    env = UnityPy.load(inp)
    # make sure that Texture2Ds are at the end
    objs = sorted((obj for obj in env.objects if obj.type.name in AssetBatchConverter.TYPES), key = lambda x: 1 if x.type == "Texture2D" else 0)
    # check how the path should be handled
    if len(objs) == 2 and objs[0].type == "Sprite" and objs[1].type == "Texture2D":
        AssetBatchConverter.export_obj(objs[0], os.path.dirname(path), True)
    else:
        used = []
        for obj in objs:
            if obj.path_id not in used:
                used.extend(AssetBatchConverter.export_obj(obj, path, True))

if __name__ == "__main__":
    main()