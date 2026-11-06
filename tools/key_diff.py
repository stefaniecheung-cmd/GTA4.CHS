#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对比 frontend_menus.xml 用到的 PREF_ 槽位与 FusionFix asi 内真实键集。

用法:
    python key_diff.py --asi <GTAIV.EFLC.FusionFix.asi> --xml <frontend_menus.xml> [...]

输出里“asi 中不存在”的槽位分两类：
  - 游戏本体自带的 PREF_ 槽（正常，与本 mod 无关）
  - FusionFix 旧版本遗留的占位槽（PREF_EPISODIC_* 这类），**这才是需要重新映射的**
"""
import argparse
import re


def asi_keys(path):
    raw = open(path, "rb").read()
    return set(m.group().decode() for m in re.finditer(rb"PREF_[A-Z0-9_]{3,48}", raw))


def xml_keys(path):
    txt = open(path, encoding="utf-8", errors="replace").read()
    return sorted(set(re.findall(r'value="(PREF_[A-Z0-9_]+)"', txt)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asi", required=True)
    ap.add_argument("--xml", nargs="+", required=True)
    a = ap.parse_args()

    keys = asi_keys(a.asi)
    print("asi 中 PREF_ 串: %d" % len(keys))
    for p in a.xml:
        xs = xml_keys(p)
        missing = [k for k in xs if k not in keys]
        episodic = [k for k in missing if k.startswith("PREF_EPISODIC_")]
        print("\n%s: xml 用到 %d 个 PREF，asi 里没有 %d 个" % (p, len(xs), len(missing)))
        print("  其中 PREF_EPISODIC_ 占位槽 %d 个（需要重新映射）:" % len(episodic))
        for k in episodic:
            print("    ", k)


if __name__ == "__main__":
    main()
