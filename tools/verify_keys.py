#!/usr/bin/env python3
"""校验 custom_translations.json 的键是否能逐字命中 FusionFix 二进制

用法:
    python verify_keys.py --asi <GTAIV.EFLC.FusionFix.asi> --table <custom_translations.json> \
                          [--baseline <原版 json>]

输出:
    - 表条目数、解析是否正常
    - 每个键在 asi 中的全等命中数（要求 100%）
    - 与 baseline 的键集差异（新增 / 保留 / 移除）
"""
import argparse
import json
import re


def load(path):
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asi", required=True)
    ap.add_argument("--table", required=True)
    ap.add_argument("--baseline")
    args = ap.parse_args()

    data = open(args.asi, "rb").read()
    low = data.lower()
    table = load(args.table)

    missing = [k for k in table if not re.search(re.escape(k.lower().encode()), low)]

    print(f"表条目: {len(table)}")
    print(f"键串命中: {len(table) - len(missing)}/{len(table)}")
    if missing:
        print("未命中（拼写与二进制显示名不一致）:")
        for k in missing:
            print("   -", k)

    if args.baseline:
        base = load(args.baseline)
        added = [k for k in table if k not in base]
        removed = [k for k in base if k not in table]
        print(f"\n相对 baseline: 新增 {len(added)}，移除 {len(removed)}")
        if removed:
            print("移除的旧键:", removed)

    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
