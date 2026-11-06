# 更新摘要 · Solitude 3 菜单适配（三阶段演进）

> **当前生效的是 v2**（以 FusionFix 5.1.2 官方 xml 为底座）。v1 已废弃，仅作历史记录；它的槽位映射思路被 v2 继承。

## 阶段对照

| 阶段 | 底座 | 每章改动 | 结果 | 状态 |
|---|---|---|---|---|
| **v1（首轮）** | Solitude 3 原版 xml（基于 FusionFix 4.0.5） | 改绑 39 处槽位 | 滑块能写值了，但底座是旧的：缺 5.1.2 三个新控件、借联机枚举显示滤镜、scaler 1 基错位、ScreenFilter 锁死 | **已废弃** |
| **v2（当前）** | FusionFix 5.1.2 官方 xml | 每章 1 行标签 | 保留 5.1.2 全部原生项，只把 Scren Filter 的 0 号标为 `Solitude / On` | 已装 G 盘 + Solitude 3 FIX，校验 PASS |

用户已明确否决「用 Solitude 4.0.5 原版 xml 打底」，v2 即按此拍板的方案。v2 细节见《更新摘要-FusionFix5.1.2菜单资产.md》。

## 问题：滑块写错槽

Solitude 3 随包替换了三份 `frontend_menus.xml`，写它们时 FusionFix 还停在 4.0.5。那时没有正式设置槽位，自定义滑块借用联机模式废弃的「比赛名 / 比赛等级」槽作为占位：

```
PadLookSens      -> PREF_EPISODIC_RACENAME_RACE_4
MO_SENS          -> PREF_EPISODIC_RACENAME_RACE_2
MouseAimSens     -> PREF_EPISODIC_RACENAME_RACE_3
CenterDelayFoot  -> PREF_EPISODIC_RACECLASS_RACE_4 / _5
CenterDelayVeh   -> PREF_EPISODIC_RACECLASS_RACE_1 / _2
CamTurnSpeedVeh  -> PREF_EPISODIC_RACECLASS_RACE_0 / RACENAME_RACE_5
MO_FOV           -> PREF_EPISODIC_RACECLASS_RACE_3
```

这些槽单机不用，所以拖滑块时值被写进「比赛名」，退出菜单再进，滑块从自己的槽读值 → 读到默认值 → **调整无效**。

## v1 的槽位映射（思路保留，方案不用）

| 设置 | 5.1.2 正式槽位 |
|---|---|
| 鼠标瞄准灵敏度 | `PREF_MOUSEAIMSENSITIVITY` |
| 手柄环视灵敏度 | `PREF_PADLOOKSENSITIVITY` |
| 手柄瞄准灵敏度 | `PREF_PADAIMSENSITIVITY` |
| 步行镜头回中延迟（键盘 / 手柄） | `PREF_KBCAMCENTERDELAY` / `PREF_PADCAMCENTERDELAY` |
| 载具镜头回中延迟（键盘 / 手柄） | `PREF_KBCAMCENTERDELAYVEH` / `PREF_PADCAMCENTERDELAYVEH` |
| 载具转向速度（键盘 / 手柄） | `PREF_KBCAMTURNSPEEDVEH` / `PREF_PADCAMTURNSPEEDVEH` |
| 视野 FOV | `PREF_CUSTOMFOV` |

本体 / TLAD / TBoGT 各 **13 处**，合计 **39 处**。这些串已逐串在 `GTAIV.EFLC.FusionFix.asi` 里验证存在。

这套映射没有错，但“在旧底座上打补丁”治不了另外三个问题：

1. **缺项**：Solitude 旧菜单没有 5.1.2 新增的 Stunt Jump Cam / Action Cam / Ladders Climb，也没有显示页的 `PREF_CUSTOMFOV`。
2. **借壳污染**：4.0.5 时代把滤镜控件的 `displayValue` 挑到 `MENU_DISPLAY_NETSTATS_*`（联机真技能名 / 团队 / 比分）上，连带把「按键提示方式」共用枚举写成 `0=MO_OFF / 0=Solitude / On`、把 `Xbox 360`（值 1）显示成 `Solitude / On`。
3. **枚举 1 基 + scaler 整体 +1**：`ANTIALIASING` 1=MO_OFF/2=FXAA/3=SMAA（scaler 8 vs 官方 3）、`DOF` 1..6（11 vs 6）、`SHADOWFILTER` 1..3（6 vs 3）、`BUTTONS` 1..8（13 vs 8）……套在 0 基的 5.1.2 上会显示错值或拨到越界。

所以 v2 改成：**官方 5.1.2 xml 打底，只补滤镜标签**。

## v2 的变更与校验

- 每章 1 行：`MENU_DISPLAY_TIMECYC` 的 0 号选项 `MO_DEF` → `Solitude / On`（common L294 / TLAD L443 / TBoGT L367）。
- 其余均官方原文：`Distant Lights` 仍 `MO_DEF` / `Project2DFX`，`Control Method` 仍 `MO_JOY` / `MO_KEY`，`Console Gamma` 仍 `MO_OFF` / `Xbox 360` / `PlayStation 3`。
- `Screen Filter` 的 `scaler` 保持官方 `5`，不再锁死。注意：**cfg 里写 `ScreenFilter = 0`**（不覆写色校正 = 吃 `timecyc.dat` 原值 = Solitude 调色生效）。Solitude readme 里的 `5` 在 5.1.2 同样落 `default`，效果等同，但 5 不是菜单合法档位。
- 校验（`tools/verify_ff512_base.py`）：行数不变、差异各 1 处、选项 637/840/757 条不变、`PREF_` 键 171/176/174 全等、TLAD 只剩 3 个合法的 `PREF_EPISODIC`、三控件仍在、scaler=5 → **PASS**。

## 用法（v2）

```bash
python tools/build_ff512_solitude_menu.py --src "<FusionFix>\update" --out "<输出>"
python tools/verify_ff512_base.py --ff "<FusionFix>\update" --new "<输出>\update" --expect 1
```

然后把 `update/{common,TLAD,TBoGT}/common/data/frontend_menus.xml` 覆盖到游戏根目录。

v1 的 `tools/fix_solitude_menus.py` / `verify_solitude_menus.py` 仍保留在 `tools/` 下，仅作对比研究与审查用，**不要再用它们去改 Solitude 原版 xml 当成品**。

## 维护（FusionFix 升级后）

见《维护手册-FusionFix升级流程.md》。一句话：重新跑 `verify_keys`（汉化表命中率）→ `build_ff512_solitude_menu`（重建底座）→ `verify_ff512_base`（必须 PASS）→ 8 项游戏内回归。

## 已知边界

- 只修菜单层，不改 Solitude 的画质参数（timecyc 等）。
- 6 个同名文件（`timecyc.dat`、`timecycext.dat`、`visualSettings.dat`、`coronas.wtd`、`stipple.wtd`、`gtaRainEmitter.xml`）FF 包也自带且内容不同 → **先装 FF，再装 Solitude**。
- 版本锚点：`GTAIV.EFLC.FusionFix.asi` = **5.1.2.0-cad0970**，14,526,680 字节。
