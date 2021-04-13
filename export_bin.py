import os
import struct
import json

ROOT = os.path.dirname(os.path.realpath(__file__))
# path to the decrypted xd master files - can be found in internal/Android/com.boltrend.disgaea.en/files/Boltrend/XDMaster
xdmaster_path = r"D:\Datamine\DRPG global\typetre_test\com.boltrend.disgaea.en\files\Boltrend\XDMaster"
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
        result |= (i & 0x7f) << shift
        shift += 7
        if not (i & 0x80):
            break
    return result


READ = {
    "byte": lambda r: read(r, "<B", 1),
    "int": lambda r: read(r, "<i", 4),
    "uint": lambda r: read(r, "<I", 4),
    "long": lambda r: read(r, "<q", 8),
    "ulong": lambda r: read(r, "<Q", 8),
    "float": lambda r: read(r, "<f", 4),
    "string": lambda r: r.read(read_varint(r)).decode("utf8"),
    "bool": lambda r: read(r, "?", 1),
    "int[]": lambda r: [READ["int"](r) for _ in range(READ["int"](r))],
    "uint[]": lambda r: [READ["uint"](r) for _ in range(READ["int"](r))],
    "long[]": lambda r: [READ["long"](r) for _ in range(READ["int"](r))],
    "ulong[]": lambda r: [READ["ulong"](r) for _ in range(READ["int"](r))],
    "float[]": lambda r: [READ["float"](r) for _ in range(READ["int"](r))],
}


def parse(reader, struct):
    parser = [
        (v['name'], READ[v['type']])
        for v in struct
    ]

    count = READ["uint"](reader)
    # debug version
    # data = []
    # for _ in range(count):
    #     item = {}
    #     for key,f in parser:
    #         item[key] = f(reader)
    #     data.append(item)
    # return data

    return [
        {
            key: f(reader)
            for key, f in parser
        }
        for i in range(count)
    ]


# read structs
structs = {
    f[:-5].lower(): json.load(open(os.path.join(struct_path, f), "rt", encoding="utf8"))
    for f in os.listdir(struct_path)
}

for f in os.listdir(xdmaster_path):
    # filter flist and mver
    if f in ["flist", "mver"]:
        continue
    fp = os.path.join(xdmaster_path, f)
    dfp = os.path.join(dst, f"{f[:-4]}.json")

    # generate struct name from the file name
    skey = f[:-6]
    if skey[0] == "B":
        skey = f"Boltrend{skey[1:]}Data"
    elif skey[0] == "M":
        skey = f"Master{skey[1:]}Data"
    else:
        print("Don't know how to handle:", f)
        continue

    # try to parse and save the data
    try:
        x = parse(open(fp, "rb"), structs[skey.lower()])
        with open(dfp, "wt", encoding="utf8") as f:
            json.dump(x, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Failed to decode:", f, skey)
        print(e)
