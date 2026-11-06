# 更新摘要 · Solitude 3 菜单文件适配 FusionFix 5.1.2

本分支 = `menu-l10n-full`（汉化 87 条）+ Solitude 3 菜单槽位修正。

## 问题

Solitude 3 随包替换了游戏的三份 `frontend_menus.xml`（本体 / TLAD / TBoGT），基于 **FusionFix 4.0.5**。
那时 FusionFix 没有正式设置槽位，把自定义滑块借用了联机模式废弃的“比赛名/比赛等级”槽当占位符：

```
PadLookSens      -> PREF_EPISODIC_RACENAME_RACE_4
MO_SENS          -> PREF_EPISODIC_RACENAME_RACE_2
MouseAimSens     -> PREF_EPISODIC_RACENAME_RACE_3
CenterDelayFoot  -> PREF_EPISODIC_RACECLASS_RACE_4 / _5
CenterDelayVeh   -> PREF_EPISODIC_RACECLASS_RACE_1 / _2
CamTurnSpeedVeh  -> PREF_EPISODIC_RACECLASS_RACE_0 / RACENAME_RACE_5
MO_FOV           -> PREF_EPISODIC_RACECLASS_RACE_3
```

这些槽单机不用，所以拖滑块时值被写进“比赛名”，退出菜单再进来，滑块从自己的槽读值 → 读到默认值 → **调整无效**。

## 修法

一律改绑 FusionFix 5.1.2 的正式槽位（这些串直接从 `GTAIV.EFLC.FusionFix.asi` 里逐串验证过存在）：

| 设置 | 5.1.2 槽位 |
|---|---|
| 鼠标瞄准灵敏度 | `PREF_MOUSEAIMSENSITIVITY` |
| 手柄环视灵敏度 | `PREF_PADLOOKSENSITIVITY` |
| 手柄瞄准灵敏度 | `PREF_PADAIMSENSITIVITY` |
| 步行镜头回中延迟（键盘 / 手柄） | `PREF_KBCAMCENTERDELAY` / `PREF_PADCAMCENTERDELAY` |
| 载具镜头回中延迟（键盘 / 手柄） | `PREF_KBCAMCENTERDELAYVEH` / `PREF_PADCAMCENTERDELAYVEH` |
| 载具转向速度（键盘 / 手柄） | `PREF_KBCAMTURNSPEEDVEH` / `PREF_PADCAMTURNSPEEDVEH` |
| 视野 FOV | `PREF_CUSTOMFOV` |

本体 / TLAD / TBoGT 各 **13 处**，合计 **39 处**；只改 `value=` 一个属性，
`action` / `label` / `scaler` / `displayValue`、行序、注释块全部保持原样。

## 校验

| 项 | 结果 |
|---|---|
| 每章变动行数 | 13 / 13 / 13 |
| XML 结构解析 | 三份全部通过 |
| 残留占位槽 | 本体 0、TBoGT 0；TLAD 保留 `PREF_EPISODIC_NOISE_FILTER`（噪声滤镜，5.1.2 无对应项）与 `PREF_EPISODIC_SCORES_0`（联机比分，原版槽位），均非本次目标 |
| 注释块 | 未被误改 |
| 滑块步进 | `scaler` 保持 21 / 10 / 8；取值范围由 ini 的 `GamepadLookSensitivityRange = 0.1, 2.0` 等三项决定，与步数无关 |

## 用法

本仓库**不分发 Solitude 的 xml 本体**（作者明确要求不得再分发），改用改写脚本，在你自己的副本上原地改：

```bash
python tools/fix_solitude_menus.py --src "<Solitude 3 解压目录>" --check          # 先看会改哪些
python tools/fix_solitude_menus.py --src "<Solitude 3 解压目录>" --dst "<输出目录>"  # 再写出
python tools/verify_solitude_menus.py --src "<Solitude 3 解压目录>" --dst "<输出目录>"
```

然后把输出目录里的三份 `frontend_menus.xml` 覆盖到游戏根目录同名位置。

## 维护（FusionFix 升级后）

```bash
python tools/key_diff.py --asi <新的 GTAIV.EFLC.FusionFix.asi> --xml <三份 xml>
```

输出里 `PREF_EPISODIC_` 那一段就是需要重新映射的占位槽。若槽位改名，更新
`tools/fix_solitude_menus.py` 里的 `MAP` 表后重跑，再用 `verify_solitude_menus.py` 复核。

## 已知边界

- 只修槽位绑定，不改 Solitude 的画质参数（timecyc 等）。
- `ScreenFilter` 按 Solitude 要求锁在 `5`（Solitude 滤镜）；画面异常时按 mod 说明处理。
- 版本锚点：`GTAIV.EFLC.FusionFix.asi` = **5.1.2.0-cad0970**。
