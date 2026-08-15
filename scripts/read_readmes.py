"""自动探测编码并读取 readme 文本（提取作者用）。

用法: python read_readmes.py <readme文件...>

作者字段常见表述（日文）: モデル制作 / 作った人 / モデリング / 制作 /
改変モデル / 致谢 / 作者 / 配布 / 改変元。中文: 制作 / 作者。
"""
import os
import sys

ENCS = ["utf-8", "shift_jis", "cp932", "gb18030", "utf-16-le", "utf-16"]


def decode(data):
    for e in ENCS:
        try:
            s = data.decode(e)
            return s, e
        except Exception:
            continue
    return repr(data[:100]), "?"


def main():
    if len(sys.argv) < 2:
        print("usage: python read_readmes.py <file...>")
        return
    for f in sys.argv[1:]:
        if not os.path.exists(f):
            print("MISSING:", f)
            continue
        print("=" * 70)
        print("FILE:", f)
        data = open(f, "rb").read()
        s, e = decode(data)
        print("ENC:", e)
        print(s.lstrip("﻿")[:3000])
        print()


if __name__ == "__main__":
    main()
