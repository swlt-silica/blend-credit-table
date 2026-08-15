"""从 PMX 文件提取模型名 / 注释，找作者线索（适用于模型文件夹没有 readme 的情况）。

用法: python pmx_author.py <model.pmx...>

原理: 不依赖完整 PMX 解析。PMX 头部是 length-prefixed 的 UTF-16LE 字符串
（模型名、英文名、注释），作者常写在注释里（如「ろくご式蓬莱山輝夜」
「作った人：Miy」）。本脚本在文件头部搜索所有「4字节长度 + 可读字符串」
的组合来精确定位这些字符串。
"""
import sys
import os


def is_readable(ch):
    o = ord(ch)
    return (0x20 <= o <= 0x7e) or (0x3000 <= o <= 0x9fff) or (0xff01 <= o <= 0xff60)


def find_strings(data, head_len=4096):
    found = []
    for i in range(min(head_len, len(data)) - 6):
        n = int.from_bytes(data[i:i + 4], "little", signed=True)
        if not (0 < n < 4000):
            continue
        chunk = data[i + 4:i + 4 + n]
        if len(chunk) != n:
            continue
        try:
            s = chunk.decode("utf-16-le")
        except Exception:
            continue
        if len(s) < 2:
            continue
        good = sum(1 for ch in s if is_readable(ch))
        if good / len(s) > 0.7:
            found.append((i, s))
    return found


def main():
    if len(sys.argv) < 2:
        print("usage: python pmx_author.py <model.pmx...>")
        return
    for p in sys.argv[1:]:
        if not os.path.exists(p):
            print("MISSING:", p)
            continue
        data = open(p, "rb").read()
        print("=" * 70)
        print("FILE:", p)
        if data[:4] != b"PMX ":
            print("  不是 PMX 文件")
            continue
        found = find_strings(data)
        seen = set()
        print("  头部字符串（前几条通常是模型名，含『式/作者/制作/作成』的是注释线索）:")
        for off, s in found:
            if s in seen:
                continue
            seen.add(s)
            print(f"   [{off}] {s}")


if __name__ == "__main__":
    main()
