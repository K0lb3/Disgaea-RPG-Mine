import requests
import UnityPy
import re
import os

from lib import base_api, asset_api, ASSETS, RES, AssetBatchConverter


# init
RAW = os.path.join(ASSETS, "raw")
EXT = os.path.join(ASSETS, "extracted")
ASSET_LIST_FP = os.path.join(ASSETS, "asset_list.txt")

SYSTEM = "android"

def toDict(tuples):
    return {key:val for key,val in tuples}

def main():
    android = asset_api.get(f"/{SYSTEM}/{SYSTEM}").content

    asset_list = read_asset_list()
    asset_list_f = open(ASSET_LIST_FP, "at", encoding="utf8")

    try:
        TODO = []
        for obj in UnityPy.load(android).objects:
            if obj.type == "AssetBundleManifest":
                d = obj.read_typetree()
                names = toDict(d["AssetBundleNames"])
                infos = toDict(d["AssetBundleInfos"])
                for aid, name in names.items():
                    ahash = bytes(infos[aid]["AssetBundleHash"].values()).hex()
                    
                    if name not in asset_list or asset_list[name] != ahash:
                        TODO.append((name, ahash))
        if TODO:
            for i, (name, ahash) in enumerate(TODO):
                print(f"{i+1}/{len(TODO)} : {name}")
                data = download_asset(name, RAW)
                extract_asset(data, get_path(EXT, name))
                asset_list_f.write(f"{name}\t{ahash}\n")

                if i%10:
                    # save current progress
                    asset_list_f.close()
                    asset_list_f = open(ASSET_LIST_FP, "at", encoding="utf8")
            asset_list_f.close()
    except KeyboardInterrupt as e:
        pass
    asset_list_f.close()

def read_asset_list():
    if not os.path.exists(ASSET_LIST_FP):
        return {}
    with open(ASSET_LIST_FP, "rt", encoding="utf8") as f:
        return dict(
            line.strip().split("\t")
            for line in f
            if line.strip()
        )

def get_path(path, name):
    fp = os.path.join(path, *name.split("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def download_asset(name, dir_path : str = ""):
    # dir : if set, save file into that dir
    data = asset_api.get(f"/{SYSTEM}/{name}").content
    if dir_path:
        with open(get_path(dir_path, name), "wb") as f:
            f.write(data)
    return data

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