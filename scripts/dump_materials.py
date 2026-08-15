"""导出 .blend 中所有骨架模型的材质贴图名，用于区分同名不同作者的模型。

用法:
    blender.exe --background --python dump_materials.py -- <blend文件路径>

输出: <blend文件路径>.materials.json
结构: { 骨架对象名: [ {mesh, materials:[{mat, images:[...]}]} ] }
"""
import sys
import bpy
import json

blendfile = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.open_mainfile(filepath=blendfile)

result = {}
meshes = [o for o in bpy.data.objects if o.type == "MESH" and o.parent and o.parent.type == "ARMATURE"]
for m in meshes:
    mats = []
    for slot in m.material_slots:
        mat = slot.material
        if mat is None:
            continue
        entry = {"mat": mat.name}
        imgs = []
        if mat.node_tree:
            for node in mat.node_tree.nodes:
                if node.type == "TEX_IMAGE" and node.image:
                    imgs.append(node.image.name)
        entry["images"] = imgs
        mats.append(entry)
    result.setdefault(m.parent.name, []).append({"mesh": m.name, "materials": mats})

out = blendfile + ".materials.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
print("MATS_DONE:", out)
print("arms:", list(result.keys()))
