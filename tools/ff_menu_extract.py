#!/usr/bin/env python3
"""FusionFix 菜单文本提取器（用于汉化表维护）

用法:
    python ff_menu_extract.py <GTAIV.EFLC.FusionFix.asi> [输出.json]

原理:
    FusionFix 把菜单项以 "PREF_XXX\0<显示名>" 的形式存在 .rdata 里，
    菜单分组头是 "MENU_DISPLAY_*"。本脚本按顺序读出每个键后面的显示名，
    并顺带收集同区的取值词（Off/Low/High/Sharp/PC/Console...）。

    升级 FusionFix 后重跑本脚本，把输出与现有 custom_translations.json
    做键集 diff，即可知道新增/删除/改名的菜单项。
"""
import json
import re
import sys

KEY_RE = re.compile(rb"(?:PREF|MENU)_[A-Z0-9_]{3,60}")
ASCII_RE = re.compile(rb"[A-Za-z0-9 +./:_'\-]{2,48}")


def readable(b: bytes) -> bool:
    if not b:
        return False
    s = b.decode("latin-1")
    return all(32 <= ord(c) < 127 for c in s) and not s.startswith(("PREF_", "MENU_"))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "ff_menu_keys.json"

    data = open(path, "rb").read()
    items = {}
    order = []

    for m in KEY_RE.finditer(data):
        key = m.group().decode()
        # 键后面最多看 200 字节，取第一个可读串作为显示名
        tail = data[m.end():m.end() + 200]
        for piece in tail.split(b"\x00"):
            if readable(piece):
                items[key] = piece.decode("latin-1")
                order.append(key)
                break

    # 收集取值词：PREF_/MENU_ 键表附近出现的短词
    anchor_offs = [m.start() for m in KEY_RE.finditer(data)]
    values = set()
    if anchor_offs:
        lo, hi = min(anchor_offs) - 256, max(anchor_offs) + 3072
        for m in ASCII_RE.finditer(data[lo:hi]):
            s = m.group().decode("latin-1").strip()
            if 2 <= len(s) <= 22 and not s.startswith(("PREF_", "MENU_")) and " " not in s[:1]:
                values.add(s)

    result = {
        "source": path,
        "option_labels": items,
        "value_candidates": sorted(values),
        "key_order": order,
    }
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)

    print(f"PREF_/MENU_ 键: {len(items)}")
    print(f"取值候选: {len(values)}")
    print(f"已写出: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
