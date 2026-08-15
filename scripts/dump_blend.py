"""解析 .blend 场景结构，导出集合层级与对象名。

用法:
    blender.exe --background --python dump_blend.py -- <blend文件路径>

输出: <blend文件路径>.scene_dump.json
"""
import sys
import bpy
import json

blendfile = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=blendfile)

result = {"blendfile": blendfile, "scenes": []}


def walk_collection(coll, out_list):
    out_list.append({
        "name": coll.name,
        "objects": [o.name for o in coll.objects],
    })
    for child in coll.children:
        walk_collection(child, out_list)


for scene in bpy.data.scenes:
    scene_entry = {"name": scene.name}
    colls = []
    for coll in scene.collection.children:
        walk_collection(coll, colls)
    scene_entry["collections"] = colls
    result["scenes"].append(scene_entry)

out_path = blendfile + ".scene_dump.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print("DUMP_DONE:", out_path)
