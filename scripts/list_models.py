"""从 .scene_dump.json 中提取实际用到的模型名（候选）。

只分析主 Collection（名为 "Collection" 的顶层集合），跳过刚体/关节/骨骼/
灯光等噪声。用法: python list_models.py <dump.json 或通配符>

示例: python list_models.py "D:\\工程\\*.scene_dump.json"
"""
import json
import glob
import re
import sys

SKIP_EXACT = {
    "rigidbodies", "joints", "temporary", ".placeholder", ".dummy_armature",
    "Light", "Camera", "点光", "面光", "聚光", "体积", "立方体",
}
# 灯光等带数字后缀的也跳过（面光.001 ... 聚光.002）
SKIP_PREFIX = ("面光", "聚光", "点光", "temporary")


def candidates(names):
    out = set()
    for n in names:
        if n.startswith("RIG-") or n.startswith(SKIP_PREFIX):   # 绑定副本 / 灯光噪声
            continue
        if n.endswith("_arm") or n.endswith("_mesh"):
            out.add(n)
    for n in names:
        if n.startswith("RIG-") or n.startswith(SKIP_PREFIX):
            continue
        if re.match(r"^\d+_", n):            # 刚体部件编号
            continue
        if n.startswith("J."):                # 关节
            continue
        if n.startswith("ncc") or n.startswith("mmd_bonetrack"):
            continue
        if n in SKIP_EXACT:
            continue
        # 含日文/中文 或 形如 ver\d 的，视为模型名
        if re.search(r"[぀-ヿ一-鿿]", n) or re.search(r"ver\d", n, re.I):
            out.add(n)
    return out


def main():
    if len(sys.argv) < 2:
        print("usage: python list_models.py <dump.json...>")
        return
    files = []
    for a in sys.argv[1:]:
        files += glob.glob(a)
    for fp in sorted(set(files)):
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        print("=" * 60)
        print("FILE:", data["blendfile"])
        for scene in data["scenes"]:
            for coll in scene["collections"]:
                if coll["name"] != "Collection":
                    continue
                c = candidates(coll["objects"])
                print(f"  候选模型 ({len(c)}):")
                for n in sorted(c):
                    print("   ", n)


if __name__ == "__main__":
    main()
