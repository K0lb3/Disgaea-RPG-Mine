import os
import struct
import json
import types
import re
from jellyfish import jaro_winkler_similarity
import array

ROOT = os.path.dirname(os.path.realpath(__file__))
# path to the decrypted xd master files - can be found in internal/Android/com.boltrend.disgaea.en/files/Boltrend/XDMaster
xdmaster_path = os.path.join(ROOT, "Boltrend", "XDMaster")
# same as in generate_structs
struct_path = os.path.join(ROOT, "structs")
# path to dump the decoded files into
dst = os.path.join(ROOT, "master_data")


def read(stream, t, size):
    return struct.unpack(t, stream.read(size))[0]


def read_varint(r):
    # https://github.com/fmoo/python-varint/blob/master/varint.py
    shift = 0
    result = 0
    while True:
        i = read(r, "<B", 1)
        result |= (i & 0x7F) << shift
        shift += 7
        if not (i & 0x80):
            break
    return result


READ = {
    "Byte": lambda r: read(r, "<B", 1),
    "Int32": lambda r: read(r, "<i", 4),
    "UInt32": lambda r: read(r, "<I", 4),
    "Int64": lambda r: read(r, "<q", 8),
    "UInt64": lambda r: read(r, "<Q", 8),
    "Single": lambda r: read(r, "<f", 4),
    "String": lambda r: r.read(read_varint(r)).decode("utf8"),
    "Boolean": lambda r: read(r, "?", 1),
    "int": lambda r: read(r, "<i", 4),
    "uint": lambda r: read(r, "<I", 4),
    "long": lambda r: read(r, "<q", 8),
    "ulong": lambda r: read(r, "<Q", 8),
    "float": lambda r: read(r, "<f", 4),
    "DateTime": lambda r: None,
}


def parser_from_struct(struct):
    property_names = [key.lower() for key in struct["properties"].keys()]
    parser = [
        (key, get_parse_function(typ))
        for key, typ in struct["fields"].items()
        if any(
            jaro_winkler_similarity(x, key.replace("_", "")) > 0.90
            or key.replace("_", "") in x
            or x in key.replace("_", "")
            for x in property_names
        )
    ]
    return parser


def read_nothing(r) -> None:
    return None


def get_parse_function(typ):
    if typ[-2:] == "[]":
        func = get_parse_function(typ[:-2])
        if func == read_nothing:  # sub class
            return read_nothing
            # return lambda r: parse(r, func)
        else:
            return lambda r: [func(r) for _ in range(READ["int"](r))]
    elif typ in READ:
        return READ[typ]
    elif typ.lower() in structs:
        return read_nothing
        # return structs[typ.lower()]
    else:
        print(typ)
        # might be an enum, todo for later
        return READ["Int32"]


def parse(reader, struct):
    parser = parser_from_struct(struct)

    count = READ["int"](reader)  # uint for normal, int for internal?
    # debug version
    # data = []
    # for _ in range(count):
    #     item = {}
    #     for key,f in parser:
    #         # print(key, reader.tell())
    #         item[key] = f(reader)
    #     data.append(item)
    # return data

    return [{key: f(reader) for key, f in parser} for _ in range(count)]


# read structs
structs = {
    f[:-5].lower(): json.load(open(os.path.join(struct_path, f), "rt", encoding="utf8"))
    for f in os.listdir(struct_path)
}

worked = 0
failed = 0

for f in os.listdir(xdmaster_path):
    # filter flist and mver
    if f in ["flist", "mver"]:
        continue
    fp = os.path.join(xdmaster_path, f)
    dfp = os.path.join(dst, f"{f[:-4]}.json")

    # generate struct name from the file name
    skey = re.match(r"(\w+?)(_\d+)?.bin", f)[1]
    if skey[0] == "B":
        skey = f"Boltrend{skey[1:]}Data"
    elif skey[0] == "M":
        skey = f"Master{skey[1:]}Data"
    else:
        print("Don't know how to handle:", f)
        continue

    if skey.lower() not in structs and skey.endswith("BonusData"):
        skey = f"{skey[:-4]}esData"

    # try to parse and save the data
    try:
        x = parse(open(fp, "rb"), structs[skey.lower()])
        with open(dfp, "wt", encoding="utf8") as f:
            json.dump(x, f, ensure_ascii=False, indent=4)
        worked += 1
    except Exception as e:
        print("Failed to decode:", f, skey)
        print(e)
        failed += 1
