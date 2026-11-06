#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验 fix_solitude_menus.py 的改写结果。

用法:
    python verify_solitude_menus.py --src <原 Solitude 目录> --dst <改写后目录>

检查项：结构解析、变动行数、残留占位槽、新槽位出现次数、注释块是否被误改。
"""
import argparse
import os
import re
import xml.etree.ElementTree as ET

FILES = {
    "common": r"to main GTAIV folder\update\common\data\frontend_menus.xml",
    "TLAD":   r"to main GTAIV folder\update\TLAD\common\data\frontend_menus.xml",
    "TBoGT":  r"to main GTAIV folder\update\TBoGT\common\data\frontend_menus.xml",
}
NEW_KEYS = {"PREF_MOUSEAIMSENSITIVITY", "PREF_PADLOOKSENSITIVITY", "PREF_PADAIMSENSITIVITY",
            "PREF_KBCAMCENTERDELAY", "PREF_PADCAMCENTERDELAY",
            "PREF_KBCAMCENTERDELAYVEH", "PREF_PADCAMCENTERDELAYVEH",
            "PREF_KBCAMTURNSPEEDVEH", "PREF_PADCAMTURNSPEEDVEH", "PREF_CUSTOMFOV"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    a = ap.parse_args()

    for ep, rel in FILES.items():
        src = os.path.join(a.src, rel)
        dst = os.path.join(a.dst, rel)
        A = open(src, "rb").read()
        B = open(dst, "rb").read()
        print("\n===== %s =====" % ep)
        print("大小: %d -> %d (%+d)" % (len(A), len(B), len(B) - len(A)))
        la, lb = A.split(b"\n"), B.split(b"\n")
        diffs = [(i, la[i].strip(), lb[i].strip()) for i in range(min(len(la), len(lb)) if len(la) == len(lb) else 0) if la[i] != lb[i]]
        print("变动行数: %d（行数 %d/%d）" % (len(diffs), len(la), len(lb)))
        for i, x, y in diffs:
            ra = re.search(rb'value="([^"]*)"', x)
            rb2 = re.search(rb'value="([^"]*)"', y)
            print("  L%-5d %-34s -> %s" % (i + 1, ra.group(1).decode() if ra else "?", rb2.group(1).decode() if rb2 else "?"))
        try:
            ET.fromstring(B)
            print("XML 解析: OK")
        except Exception as e:
            print("XML 解析失败:", e)
        left = sorted(set(re.findall(rb'value="(PREF_EPISODIC_[A-Z0-9_]+)"', B)))
        print("仍保留的 EPISODIC 槽:", [x.decode() for x in left])
        cnt = {k.encode(): B.count(k.encode()) for k in NEW_KEYS}
        print("新槽位出现次数:", {k.decode(): v for k, v in cnt.items() if v})


if __name__ == "__main__":
    main()
