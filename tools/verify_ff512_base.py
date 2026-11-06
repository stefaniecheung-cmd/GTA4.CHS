# -*- coding: utf-8 -*-
"""独立校验：产物 xml 与 FusionFix 官方 xml 逐行比对。

只允许"每章 N 处 options 标签文本改动"（N 默认 1），其余一律视为失败：
行数、字节、选项条目数、菜单选项三元组的 enum/value、PREF_ 键集合、EPISODIC 槽位合法性、
Screen Filter 的 scaler、以及 5.1.2 新增控件是否还在。

用法:
    python verify_ff512_base.py --ff "<官方 update 目录>" --new "<产物 update 目录>" [--expect 1]

退出码 0 = PASS，1 = FAIL，可直接接 CI 或批处理。
"""
import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET

REL = [r"common\data\frontend_menus.xml",
       r"TLAD\common\data\frontend_menus.xml",
       r"TBoGT\common\data\frontend_menus.xml"]

# 5.1.2 新增、绝不能被 4.0.5 时代菜单覆盖掉的三项
KEEP = ["PREF_STUNTJUMPCAM", "PREF_ACTIONCAM", "PREF_AUTOCLIMBLADDERS"]

# 允许存在的联机占位槽（原版合法用法）：TLAD 的噪声滤镜 + 排行榜分值
ALLOWED_EPISODIC = ("PREF_EPISODIC_NOISE_FILTER", "PREF_EPISODIC_SCORES_0")

CH = ("item", "itempc", "options", "optionspc")


def option_triples(path):
    root = ET.parse(path).getroot()
    return [(m.get("enum"), c.get("value"), c.get("text"))
            for m in root.iter() if m.tag in ("menu", "menupc")
            for c in list(m) if c.tag in CH]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ff", required=True, help="FusionFix 官方 update 目录")
    ap.add_argument("--new", required=True, help="产物 update 目录")
    ap.add_argument("--expect", type=int, default=1, help="每章允许的标签改动条数（默认 1）")
    a = ap.parse_args()

    ok = True
    for rel in REL:
        src, dst = os.path.join(a.ff, rel), os.path.join(a.new, rel)
        print("\n===== %s =====" % rel)
        if not (os.path.exists(src) and os.path.exists(dst)):
            print("  [FAIL] 文件缺失: %s / %s" % (src, dst))
            ok = False
            continue

        la = open(src, "rb").read().split(b"\n")
        lb = open(dst, "rb").read().split(b"\n")
        print("  行数: %d -> %d | 字节: %d -> %d"
              % (len(la), len(lb), os.path.getsize(src), os.path.getsize(dst)))

        if len(la) != len(lb):
            print("  [FAIL] 行数变化")
            ok = False
            diffs = []
        else:
            diffs = [(i + 1, la[i].decode("utf-8", "replace").strip(), lb[i].decode("utf-8", "replace").strip())
                     for i in range(len(la)) if la[i] != lb[i]]

        print("  差异行 %d 处:" % len(diffs))
        for n, x, y in diffs:
            print("    L%-5d - %s" % (n, x))
            print("            + %s" % y)
        if len(diffs) != a.expect:
            print("  [FAIL] 差异行数不是 %d" % a.expect)
            ok = False
        for n, x, y in diffs:
            if not (x.startswith("<options") and y.startswith("<options") and 'text="' in x):
                print("  [FAIL] L%d 不是 options 标签文本改动" % n)
                ok = False
            if re.sub(r'text="[^"]*"', 'text=""', x) != re.sub(r'text="[^"]*"', 'text=""', y):
                print("  [FAIL] L%d 除 text 外还有别的字段被改" % n)
                ok = False

        ea, eb = option_triples(src), option_triples(dst)
        changed = [(x, y[2]) for x, y in zip(ea, eb) if x != y]
        print("  选项条目: %d 条，实际变动 %d 条 -> %s" % (len(eb), len(changed), changed))
        same_key = [(x, y[2]) for x, y in zip(ea, eb) if x[:2] != y[:2]] == []
        print("  菜单选项三元组: %d -> %d | enum/value 全等: %s" % (len(ea), len(eb), same_key))
        if len(ea) != len(eb) or not same_key:
            ok = False

        ra, rb = open(src, "rb").read(), open(dst, "rb").read()
        keys_a = set(re.findall(rb'value="(PREF_[A-Z0-9_]+)"', ra))
        keys_b = set(re.findall(rb'value="(PREF_[A-Z0-9_]+)"', rb))
        print("  PREF 键: %d -> %d | 完全一致: %s" % (len(keys_a), len(keys_b), keys_a == keys_b))
        if keys_a != keys_b:
            print("    多出:", sorted(keys_b - keys_a), " 缺少:", sorted(keys_a - keys_b))
            ok = False

        eps = sorted(set(re.findall(rb"PREF_EPISODIC_[A-Z0-9_]*", rb)))
        print("  PREF_EPISODIC 实例: %d  %s" % (rb.count(b"PREF_EPISODIC"), eps))
        bad = [e.decode() for e in eps if e.decode() not in ALLOWED_EPISODIC]
        if bad:
            print("  [FAIL] 出现不该有的联机占位槽: %s" % bad)
            ok = False
        if b"PREF_EPISODIC_RACENAME" in rb or b"PREF_EPISODIC_CAM" in rb:
            print("  [FAIL] 滑块仍绑在联机占位槽")
            ok = False

        for k in KEEP:
            n = rb.count(k.encode())
            print("  %-26s %d 次" % (k, n))
            if n == 0:
                print("  [FAIL] 5.1.2 新增控件丢了")
                ok = False

        sc = re.findall(rb'label="Screen Filter" value="PREF_TIMECYC" scaler="(\d+)"', rb)
        print("  Screen Filter 控件 scaler: %s" % sc)
        if not sc or any(x != b"5" for x in sc):
            print("  [FAIL] Screen Filter 的 scaler 不是 5（滑块会被锁死或越界）")
            ok = False

    print("\n>>> 总判定:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
