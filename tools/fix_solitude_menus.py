#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 Solitude 3 自带的 frontend_menus.xml（FusionFix 4.0.5 时代写法）改绑到 FusionFix 5.1.2 的正式槽位。

用法：
    python fix_solitude_menus.py --src "I:\\GTA 4 MOD 11.5\\Solitude 3" --check
    python fix_solitude_menus.py --src "I:\\GTA 4 MOD 11.5\\Solitude 3" --dst "C:\\out"

只改 value= 一个属性；action / label / scaler / displayValue、行序、注释块全部保持原样。
"""
import argparse, os, re, sys

FILES = {
    "common": r"to main GTAIV folder\update\common\data\frontend_menus.xml",
    "TLAD":   r"to main GTAIV folder\update\TLAD\common\data\frontend_menus.xml",
    "TBoGT":  r"to main GTAIV folder\update\TBoGT\common\data\frontend_menus.xml",
}

# (所在菜单 enum, label) -> 5.1.2 正式槽位
MAP = {
    ("SCR_KEYBOARD_OPTIONS", "MouseAimSens"):      "PREF_MOUSEAIMSENSITIVITY",
    ("SCR_KEYBOARD_OPTIONS", "CenterDelayFoot"):   "PREF_KBCAMCENTERDELAY",
    ("SCR_KEYBOARD_OPTIONS", "CenterDelayVeh"):    "PREF_KBCAMCENTERDELAYVEH",
    ("SCR_KEYBOARD_OPTIONS", "CamTurnSpeedVeh"):   "PREF_KBCAMTURNSPEEDVEH",

    ("SCR_CONTROLLER_OPTIONS", "PadLookSens"):     "PREF_PADLOOKSENSITIVITY",
    ("SCR_CONTROLLER_OPTIONS", "MO_SENS"):         "PREF_PADAIMSENSITIVITY",
    ("SCR_CONTROLLER_OPTIONS", "CenterDelayFoot"): "PREF_PADCAMCENTERDELAY",
    ("SCR_CONTROLLER_OPTIONS", "CenterDelayVeh"):  "PREF_PADCAMCENTERDELAYVEH",
    ("SCR_CONTROLLER_OPTIONS", "CamTurnSpeedVeh"): "PREF_PADCAMTURNSPEEDVEH",

    ("SCR_NETWORK_CONTROLS", "PadLookSens"):       "PREF_PADLOOKSENSITIVITY",
    ("SCR_NETWORK_CONTROLS", "MO_SENS"):           "PREF_PADAIMSENSITIVITY",

    ("*", "MO_FOV"):                               "PREF_CUSTOMFOV",
}

MENU  = re.compile(r'<menu(?:pc)?\s+[^>]*enum="([^"]+)"')
LABEL = re.compile(r'label="([^"]*)"')
VALUE = re.compile(r'value="(PREF_EPISODIC_[A-Z0-9_]+)"')


def process(path):
    raw = open(path, "rb").read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    text = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
    nl = "\r\n" if text.count("\r\n") > len(text) // 2 else "\n"
    lines = text.split(nl)

    cur, changed, unresolved = "", [], []
    for i, line in enumerate(lines):
        m = MENU.search(line)
        if m:
            cur = m.group(1)
        if not VALUE.search(line):
            continue
        lab = LABEL.search(line)
        label = lab.group(1) if lab else ""
        new = MAP.get((cur, label)) or MAP.get(("*", label))
        if not new:
            unresolved.append((i + 1, cur, label, VALUE.search(line).group(1)))
            continue
        old = VALUE.search(line).group(1)
        lines[i] = line.replace(f'value="{old}"', f'value="{new}"', 1)
        changed.append((i + 1, cur, label, old, new))

    out = nl.join(lines)
    data = (b"\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
    return data, changed, unresolved


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="Solitude 3 解压目录（含 'to main GTAIV folder'）")
    ap.add_argument("--dst", help="输出目录；省略则只检查不写文件")
    ap.add_argument("--check", action="store_true", help="只打印将发生的改动")
    a = ap.parse_args()

    total = 0
    for ep, rel in FILES.items():
        src = os.path.join(a.src, rel)
        if not os.path.exists(src):
            sys.exit("找不到: %s" % src)
        data, changed, unresolved = process(src)
        print("\n===== %s  替换 %d 处 =====" % (ep, len(changed)))
        for r in changed:
            print("  L%-5d %-24s %-16s %-34s -> %s" % r)
        for r in unresolved:
            print("  未映射（保持原样）: L%-5d %-24s %-16s %s" % r)
        total += len(changed)
        if a.dst and not a.check:
            dst = os.path.join(a.dst, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            open(dst, "wb").write(data)
            print("  已写出: %s" % dst)
    print("\n合计替换 %d 处。" % total)
    if not a.dst:
        print("（未写文件；加 --dst <目录> 才会输出）")


if __name__ == "__main__":
    main()
