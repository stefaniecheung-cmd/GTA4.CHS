# GTA4 简中补丁 · FusionFix 菜单汉化 + Solitude 3 菜单适配

本仓库是 [ckeleshi/GTA4.CHS](https://github.com/ckeleshi/GTA4.CHS) 的 fork（适用于 GTA4 三合一 1.2.0.43+），在上游基础上追加两块内容：

1. **FusionFix 5.1.2 菜单汉化**：`custom_translations.json` 从 12 条扩到 87 条，逐串在 asi 二进制里全等搜索 87/87 命中。
2. **Solitude 3 菜单适配**：用 FusionFix 5.1.2 官方 `frontend_menus.xml` 重做底座，修掉「滑块调了不生效」，同时不丢 5.1.2 的新功能。

> 新增内容**不在 `master`**，都在下面两条分支上。首页只看得到上游原文。

## 两条分支

| 分支 | 内容 | 适合谁 |
|---|---|---|
| [`menu-l10n-full`](../../tree/menu-l10n-full) | 只做菜单汉化：`custom_translations.json`（87 条）+ 抽取/校验脚本 | 不装 Solitude，只要 FusionFix 菜单中文 |
| [`menu-l10n-solitude`](../../tree/menu-l10n-solitude) | 上面全部 + Solitude 3 菜单适配（生成脚本、校验脚本、4 份文档） | 装了 Solitude 3，且遇到「手柄视角灵敏度 / 瞄准灵敏度 / FOV 调了不生效」 |

## 怎么拿到成品

| 要什么 | 怎么拿 |
|---|---|
| 汉化表 | 在 `menu-l10n-full` 或 `menu-l10n-solitude` 分支里取 `plugins/GTA4.CHS/custom_translations.json`（3,076 字节），覆盖到 `<游戏目录>\plugins\GTA4.CHS\` |
| 菜单 xml | **本仓库不分发 xml 本体**。取 FusionFix 5.1.2 官方包里的 `update\`，跑一条命令生成（下节） |
| 说明书 | [`维护手册-FusionFix升级流程.md`](../../blob/menu-l10n-solitude/维护手册-FusionFix升级流程.md) |

生成菜单资产（得到 91,666 / 112,673 / 104,129 字节三份）：

```bash
python tools/build_ff512_solitude_menu.py --src "<FusionFix>\update" --out "<输出>"
python tools/verify_ff512_base.py --ff "<FusionFix>\update" --new "<输出>\update" --expect 1   # 必须 PASS
```

然后把 `update/{common,TLAD,TBoGT}/common/data/frontend_menus.xml` 覆盖到游戏根目录。

## 文档导航（看哪份）

| 文档 | 状态 |
|---|---|
| [更新摘要 · 5.1.2 官方底座菜单资产](../../blob/menu-l10n-solitude/更新摘要-FusionFix5.1.2菜单资产.md) | **当前权威**：最终方案、唯一改动、Screen Filter 为何 0 = Solitude 生效 |
| [维护手册 · FusionFix 升级流程](../../blob/menu-l10n-solitude/维护手册-FusionFix升级流程.md) | **当前权威**：8 步升级、可维护性评估、回滚 |
| [更新摘要 · Solitude 菜单修正](../../blob/menu-l10n-solitude/更新摘要-Solitude菜单修正.md) | 三阶段演进（v1 已废弃 → v2 当前） |
| [更新摘要 · 菜单汉化](../../blob/menu-l10n-solitude/更新摘要-菜单汉化.md) | 对应 `custom_translations.json`，仍然有效 |

## 为什么仓库里没有 xml / 没有 Release

- Solitude 作者安装说明明确要求不得再分发其文件；FusionFix 官方 xml 也可从官方渠道自行取得。
- 产物 = 官方 xml + 1 行标签，因此仓库只维护「脚本 + 文档」，用本地官方包现场生成，差异可逐行校验。
- 整包（zip）请在本地按维护手册打包；仓库以文本资产为准，保证可审计、可 diff。

## 上游说明

适用于GTA4三合一版本(1.2.0.43及以上)的汉化程序 · [汉化项目网站](https://b9348.pages.dev/)

依赖库：VC-LTL / Vcpkg / zlib / utfcpp / fmt / nlohmann-json / spdlog。
