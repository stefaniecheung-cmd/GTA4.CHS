# GTA4 简中补丁 · FusionFix 菜单汉化（87 条）

本分支（`menu-l10n-full`）= **只做 FusionFix 菜单汉化**，不包含任何 mod 适配。

上游项目：[ckeleshi/GTA4.CHS](https://github.com/ckeleshi/GTA4.CHS)（适用于 GTA4 三合一 1.2.0.43+ 的汉化程序）。

## 资产

| 文件 | 说明 |
|---|---|
| `plugins/GTA4.CHS/custom_translations.json` | 87 条菜单汉化表（选项名 60 + 取值 27），3,076 字节，全串精确替换 |
| `tools/ff_menu_extract.py` | 从 `GTAIV.EFLC.FusionFix.asi` 抽出菜单显示名 |
| `tools/verify_keys.py` | 汉化表逐串全等搜索，输出命中率（要求 100%） |

## 版本锚点

| 项 | 值 |
|---|---|
| FusionFix | `5.1.2.0-cad0970`（14,526,680 字节） |
| 汉化表 | 87 条 / 3,076 字节 |
| 命中率 | 87/87（逐串在 asi 二进制里全等搜索） |

## 安装

把 `custom_translations.json` 覆盖到 `<游戏目录>\plugins\GTA4.CHS\`。仓库根部的同名文件是分发副本。

## 文档

- [更新摘要 · 菜单汉化](更新摘要-菜单汉化.md) — 从 asi 抽出 60 个选项名的做法、命中率验证、风险与回滚

## 装 Solitude 3 请去另一条分支

Solitude 3 自带的 `frontend_menus.xml` 是按 FusionFix 4.0.5 写的，套在 5.1.2 上会让手柄视角/瞄准灵敏度、回中延迟、车内转向、FOV 等滑块写错槽（“调了不生效”）。解决方案、生成脚本与升级流程在 **`menu-l10n-solitude`** 分支：

- 更新摘要 · FusionFix 5.1.2 官方底座菜单资产
- 维护手册 · FusionFix 升级流程（8 步 + 可维护性评估 + 回滚）

## 已知限制

- 只覆盖注入菜单的整串显示名，**管不到运行时拼装的正文句**（简报页事件提示会漏英文）。
- `Off` / `Low` / `Medium` / `High` / `Very High` 是全游戏通用词，可能连带翻译其它界面。
- 未验证 CHS 对非 asi 来源的字面串（如 mod 自带 xml 里的英文）是否也替换。

## 许可

对上游 `ckeleshi/GTA4.CHS` 的派生，沿用其许可。本项目只包含文本表与脚本，不含任何第三方二进制。
