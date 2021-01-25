import requests
import UnityPy
import re
import os

from lib.api import base_api, asset_api, ASSETS, RES


# init
RAW = os.path.join(ASSETS, "raw")
EXT = os.path.join(ASSETS, "extracted")
ASSET_LIST_FP = os.path.join(ASSETS, "asset_list.txt")

SYSTEM = "android"

def main():
    android = asset_api.get(f"/{SYSTEM}/{SYSTEM}").content

    asset_list = read_asset_list()
    asset_list_f = open(ASSET_LIST_FP, "at", encoding="utf8")

    try:
        for obj in UnityPy.load(android).objects:
            if obj.type == "AssetBundleManifest":
                d = obj.read()
                for aid, name in d.AssetBundleNames.items():
                    ahash = bytes(d.AssetBundleInfos[aid].AssetBundleHash.values()).hex()
                    
                    if name not in asset_list or asset_list[name] != ahash:
                        data = download_asset(name, RAW)
                        #extract_asset(data, get_path(EXT, name))
                        asset_list_f.write(f"{name}\t{ahash}\n")
                        print(name)
    except KeyboardInterrupt(e):
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

def get_path(dir, name):
    fp = os.path.join(dir, *name.split("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    return fp

def download_asset(name, dir : str = ""):
    # dir : if set, save file into that dir
    data = asset_api.get(f"/{SYSTEM}/{name}").content
    if dir:
        with open(get_path(dir, name), "wb") as f:
            f.write(data)
    return data

def extract_asset(inp, dir):
    # inp can be bytes or a file path
    # dir - path to save the assets into
    env = UnityPy.load(inp)
    for obj in env.objects:
        data = obj.read()
        fp, extension = os.path.splitext(data.name)
        fp = get_path(dir, fp)

        if obj.type == 'TextAsset':
            if not extension:
                extension = '.txt'
            with open(f"{fp}{extension}", 'wb') as f:
                f.write(data.script)

        elif obj.type == "Sprite":
            extension = ".png"
            data.image.save(f"{fp}{extension}")

            return [obj.path_id, data.m_RD.texture.path_id, getattr(data.m_RD.alphaTexture, 'path_id', None)]

        elif obj.type == "Texture2D":
            extension = ".png"
            fp = f"{fp}{extension}"
            if not os.path.exists(fp):
                try:
                    data.image.save(fp)
                except EOFError:
                    pass
        
        elif obj.type == "AudioClip":
            for sample in data.samples:
                print()


if __name__ == "__main__":
    main()