# GTA4 简中补丁 · FusionFix 菜单汉化 & Solitude 3 菜单适配

本分支（`menu-l10n-solitude`）= **FusionFix 菜单汉化（87 条）+ 5.1.2 官方底座菜单适配 Solitude 3（脚本 + 文档）**。

上游项目：[ckeleshi/GTA4.CHS](https://github.com/ckeleshi/GTA4.CHS)（适用于 GTA4 三合一 1.2.0.43+ 的汉化程序）。

## 下载成品

**[Releases · v2-ff512-solitude3](../../releases/tag/v2-ff512-solitude3)** 上有两个包，按需选：

| 附件 | 字节 | 内容 | 适合谁 |
|---|---|---|---|
| `GTA4-CN-FusionFix5.1.2-Solitude3-full-v2.zip` | 647,822 | `GTA4.CHS.asi`（已修卡死）+ 原版 asi 备份 + `plugins\GTA4.CHS\` 三个数据文件 + 三份菜单 xml + 安装说明 | 开箱即用 |
| `GTA4-CN-FusionFix5.1.2-Solitude3-menu-v2.zip` | 30,891 | 汉化表 + 三份 xml + 安装说明 | 已有自己的 asi |

full 包内容：

```
plugins/GTA4.CHS.asi                       232,960
plugins/GTA4.CHS.asi.bak                   232,448   ← 上游原版，只作回滚，不加载
plugins/GTA4.CHS/char_table.dat             14,324
plugins/GTA4.CHS/custom_translations.json    3,076
plugins/GTA4.CHS/whm_table.dat             780,676
update/common/data/frontend_menus.xml       91,666
update/TLAD/common/data/frontend_menus.xml 112,673
update/TBoGT/common/data/frontend_menus.xml 104,129
安装说明.md
```

`plugins\GTA4.CHS\` 里三个文件缺一不可：只装 `custom_translations.json` 会缺字符映射与字库，中文会异常。整目录覆盖即可。

## 两条分支怎么选

| 分支 | 内容 | 适合谁 |
|---|---|---|
| `menu-l10n-full` | 只做菜单汉化：`custom_translations.json`（87 条）+ 抽取/校验脚本 | 不装 Solitude，只要 FusionFix 菜单中文 |
| `menu-l10n-solitude` | 上面全部 + Solitude 3 菜单适配（生成脚本、校验脚本、三份文档） | 装了 Solitude 3，且遇到「滑块调了不生效」 |

两份资产分开维护、分开下载，互不干扰。

## 版本锚点

| 项 | 值 |
|---|---|
| FusionFix | `5.1.2.0-cad0970`（14,526,680 字节） |
| 汉化表 | 87 条 / 3,076 字节（选项名 60 + 取值 27） |
| 菜单产物 | `frontend_menus.xml`：91,666 / 112,673 / 104,129 字节（common / TLAD / TBoGT） |
| 汉化程序 | `GTA4.CHS.asi`：232,960 字节（上游 232,448 + 两处二进制修复） |
| 适配 mod | Solitude 3（其自带菜单按 FusionFix 4.0.5 写成） |

版本串一变，就按《维护手册》走一遍，不要只改一处。

## 文档

- [更新摘要 · 菜单汉化（87 条）](更新摘要-菜单汉化.md) — 怎么从 asi 里把 60 个选项名挖出来、命中率怎么验
- [更新摘要 · Solitude 菜单修正](更新摘要-Solitude菜单修正.md) — 滑块绑错槽位（`PREF_EPISODIC_RACENAME_*` → 正式键）的来龙去脉
- [更新摘要 · FusionFix 5.1.2 官方底座菜单资产](更新摘要-FusionFix5.1.2菜单资产.md) — 为什么用官方 xml 打底、唯一改动是什么、Screen Filter 为什么 0 = Solitude 生效
- [维护手册 · FusionFix 升级流程](维护手册-FusionFix升级流程.md) — 7 步升级流程 + 可维护性评估 + 回滚

## 安装

1. 汉化程序：`plugins\GTA4.CHS.asi` + `plugins\GTA4.CHS\` 整个目录（`custom_translations.json`、`char_table.dat`、`whm_table.dat`）

2. 菜单资产（用本地 FusionFix 官方包现场生成，仓库不存 xml 本体）：

```bash
python tools/build_ff512_solitude_menu.py --src "<FusionFix>\update" --out "<输出目录>"
```

生成后覆盖到 `update/{common,TLAD,TBoGT}/common/data/frontend_menus.xml`。

3. 运行时开关 `plugins/GTAIV.EFLC.FusionFix.cfg`：

```
ScreenFilter = 0     # 0 = 用 timecyc.dat 原值 = Solitude 调色生效
DistantLights = 1    # 需已装 Project 2DFX
```

4. 覆盖顺序：**先装 FusionFix，再装 Solitude**。`timecyc.dat`、`timecycext.dat`、`visualSettings.dat`、`coronas.wtd`、`stipple.wtd`、`gtaRainEmitter.xml` 这 6 个 FF 包自带同名但内容不同，先装 Solitude 会被 FF 盖回。

## 工具

| 脚本 | 作用 |
|---|---|
| `tools/ff_menu_extract.py` | 从 `GTAIV.EFLC.FusionFix.asi` 抽出菜单显示名 |
| `tools/verify_keys.py` | 汉化表逐串全等搜索，输出命中率（要求 100%） |
| `tools/build_ff512_solitude_menu.py` | 以官方 xml 为底座生成菜单资产（只改 Screen Filter 的 0 号标签） |
| `tools/verify_ff512_base.py` | 产物与官方逐行/逐键校验，带退出码 |
| `tools/compare_solitude_vs_ff.py` | FF 与 Solitude 逐菜单对照（查「它到底改了什么」） |

## 已知限制

- 汉化表只覆盖注入菜单的整串显示名，**管不到运行时拼装的正文句**（简报页事件提示会漏英文）。
- `Solitude / On`、`Project2DFX` 不在 asi 二进制里，87 条表的全等匹配覆盖不到，会以英文露出。
- 仓库**不包含** Solitude 与 FusionFix 的任何原始文件：Solitude 作者安装说明写明不得再分发；两者都可从官方渠道取得后本地生成。

## 许可

- `GTA4.CHS.asi` 及其 `.bak`、两份 `.dat` 版权归上游 `ckeleshi/GTA4.CHS`，本仓库只在该产物上做两处兼容性修复。
- 汉化表为对上游 `ckeleshi/GTA4.CHS` 的派生，沿用其许可。
- 菜单 xml 基于 [ThirteenAG/GTAIV.EFLC.FusionFix](https://github.com/ThirteenAG/GTAIV.EFLC.FusionFix)（**GPL-3.0**），本仓库只改三章各 1 处 options 标签文本。
