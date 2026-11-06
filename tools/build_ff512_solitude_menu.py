#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""以 FusionFix 5.1.2 官方 frontend_menus.xml 为底座，补进 Solitude 需要的滤镜标签。

用法:
    python build_ff512_solitude_menu.py --src "<FusionFix 的 update 目录>" --out "<输出目录>"

改动只有 1 处标签文本（每章 1 处，三章共 3 处），不碰任何 PREF 键、scaler、displayValue：
  1. Screen Filter（PREF_TIMECYC）的 0 号选项  MO_DEF -> "Solitude / On"
     FF 源码 source/timecyc.ixx 的 timecyc_scanf 里，只有 eOFF/eIV/eTLAD/eTBOGT
     四个 case 会覆写 mColorCorrection*，default: break 什么都不改，即直接吃 timecyc.dat
     自带的值 = Solitude 的调色。所以值 0 就是"Solitude 生效"。Solitude readme 写的 5
     在 5.1.2 里同样落到 default，效果等同，但不是菜单合法档位（上游 json 的
     MISC.ScreenFilter choices 只有 0..4）。
  2. Distant Lights 保持官方原文（0=MO_DEF / 1=Project2DFX），不做改动。
     Solitude 4.0.5 时代没有该枚举，是借 MENU_DISPLAY_NETSTATS_TRUESKILLNAME 显示的
     "Solitude/P2DFX"；5.1.2 官方已有正式枚举，不需要跟。
"""
import argparse
import os
import xml.etree.ElementTree as ET

FILES = [("common", r"common\data\frontend_menus.xml"),
         ("TLAD",   r"TLAD\common\data\frontend_menus.xml"),
         ("TBoGT",  r"TBoGT\common\data\frontend_menus.xml")]

# (menu enum, option 的 value, 原 text, 新 text)
EDITS = [
    ("MENU_DISPLAY_TIMECYC", "0", "MO_DEF", "Solitude / On"),
]


def block_span(lines, enum):
    """返回 <menupc/menu enum=...> 块的行区间（含首尾）。块内不嵌套同名标签。"""
    start = None
    for i, ln in enumerate(lines):
        if start is None and ("enum=\"%s\"" % enum) in ln and ("<menu" in ln):
            start = i
        elif start is not None and "</menu" in ln:
            return start, i
    raise RuntimeError("找不到菜单块: %s" % enum)


def patch_file(src, dst):
    raw = open(src, "rb").read()
    bom = raw[:3] == b"\xef\xbb\xbf"
    text = raw[3:].decode("utf-8") if bom else raw.decode("utf-8")
    nl = "\r\n" if text.count("\r\n") > text.count("\n") / 2 else "\n"
    lines = text.split(nl)
    applied = []

    for enum, value, old_text, new_text in EDITS:
        s, e = block_span(lines, enum)
        hit = False
        for i in range(s, e + 1):
            ln = lines[i]
            if 'value="%s"' % value in ln and 'text="%s"' % old_text in ln:
                lines[i] = ln.replace('text="%s"' % old_text, 'text="%s"' % new_text, 1)
                applied.append((enum, i + 1, old_text, new_text))
                hit = True
                break
        if not hit:
            raise RuntimeError("%s 的 value=%s/text=%s 没有找到" % (enum, value, old_text))

    out = nl.join(lines)
    data = (b"\xef\xbb\xbf" + out.encode("utf-8")) if bom else out.encode("utf-8")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as fh:
        fh.write(data)
    return applied, len(raw), len(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="FusionFix 的 update 目录")
    ap.add_argument("--out", required=True, help="输出目录（会生成 update\\... 结构）")
    a = ap.parse_args()

    total = 0
    for ep, rel in FILES:
        src = os.path.join(a.src, rel)
        dst = os.path.join(a.out, "update", rel)
        applied, n0, n1 = patch_file(src, dst)
        ET.parse(dst)
        print("\n===== %s =====" % ep)
        print("  %s -> %s  (%d -> %d 字节, %+d)" % (src, dst, n0, n1, n1 - n0))
        for enum, line, old, new in applied:
            print("  L%-5d %-30s %-18s -> %s" % (line, enum, old, new))
        total += len(applied)
    print("\n合计改动 %d 处（每章 %d 处）。" % (total, len(EDITS)))


if __name__ == "__main__":
    main()
