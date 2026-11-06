# 更新摘要 · FusionFix 5.1.2 官方底座菜单资产（v2）

## 版本锚点

| 项 | 值 |
|---|---|
| 目标 FusionFix | `GTAIV.EFLC.FusionFix.asi` = **5.1.2.0-cad0970**，14,526,680 字节 |
| 底座 | FusionFix 官方 `update\{common,TLAD,TBoGT}\common\data\frontend_menus.xml`（91,659 / 112,666 / 104,122） |
| 产物 | 91,666 / 112,673 / 104,129 字节 |
| 配套汉化 | `custom_translations.json` 87 条 / 3,076 字节（另一条分支的资产） |
| 适配 mod | Solitude 3（其自带菜单按 FusionFix **4.0.5** 写成） |

## 为什么不用 Solitude 自带菜单打底

Solitude 的 `frontend_menus.xml` 是 4.0.5 时代的产物，直接套在 5.1.2 上有三类硬伤：

1. **滑块绑错槽位**：`PadLookSens` 等每章 13 个自定义滑块绑在 `PREF_EPISODIC_RACENAME_*`（联机「比赛名」占位槽）上，拖动写进比赛名槽，退出再进读自己的槽 → 恢复默认、「调整无效」。
2. **借联机枚举显示滤镜**：把滤镜控件的 `displayValue` 挪到 `MENU_DISPLAY_NETSTATS_*` 上并改写那两行文字，污染联机菜单（G 盘曾出现 `MENU_DISPLAY_CONTROL_METHOD` = `0=MO_OFF / 0=Solitude / On`）。
3. **枚举整体 1 基 + scaler 加大**：4.0.5 的枚举从 1 起，Solitude 把 `scaler` 相应 +1，套在 0 基的 5.1.2 上会显示错值 / 拨到越界。

而 5.1.2 官方菜单本身已经正确（正式键名、0 基、scaler 正确），5.1.2 还新增了 Stunt Jump Cam / Action Cam / Ladders Climb 等 4.0.5 没有的项。因此底座必须是官方，Solitude 只贡献「滤镜标签」这一件事。

## 与官方原件的唯一差异

| 文件 | 官方字节 | 产物字节 | 改动行 | 内容 |
|---|---|---|---|---|
| `update\common\data\frontend_menus.xml` | 91,659 | 91,666 | L294 | `<options text="MO_DEF" … value="0" />` → `text="Solitude / On"` |
| `update\TLAD\common\data\frontend_menus.xml` | 112,666 | 112,673 | L443 | 同上 |
| `update\TBoGT\common\data\frontend_menus.xml` | 104,122 | 104,129 | L367 | 同上 |

即 `MENU_DISPLAY_TIMECYC`（Screen Filter）的 0 号档位标签。三章共 3 处，只动 `text`。

## 为什么 0 号 = 「Solitude 生效」

上游 `source/timecyc.ixx` 的 `timecyc_scanf`：

```
switch (ScreenFilter->get())
{
  case eOFF:   /* 用 IV2OFF / TLAD2OFF / TBOGT2OFF 表覆写 mColorCorrection* */
  case eIV:    /* 跨章换算成 IV 的色校正 */
  case eTLAD:  /* → TLAD */
  case eTBOGT: /* → TBoGT */
  default: break;   /* 什么都不改，保留 timecyc.dat 自带的值 */
}
```

- 值 **0（Default）** 落 `default` 分支 → 不覆写 → 用 `timecyc.dat` 原值 → **Solitude 的调色生效**。
- 值 1/2/3/4 才是「滤镜」（跨章换算）。
- 上游 `settings/GTAIV.EFLC.FusionFix.json` 的 `MISC.ScreenFilter` choices = `0=@MO_DEF / 1=@MO_OFF / 2=IV / 3=TLAD / 4=TBOGT`，**没有 5**。Solitude readme 写的 `ScreenFilter = 5` 在 5.1.2 同样落 `default`，效果等同 0，但不是菜单合法档位 → 建议 cfg 统一写 `0`。

## 校验结果（`tools/verify_ff512_base.py`，独立于生成路径）

| 检查项 | common | TLAD | TBoGT |
|---|---|---|---|
| 行数 | 1094 → 1094 | 1452 → 1452 | 1538 → 1538 |
| 差异行 | 1 处（options text） | 1 处 | 1 处 |
| 选项条目 | 637 → 637 | 840 → 840 | 757 → 757 |
| enum/value 全等 | True | True | True |
| `PREF_` 键集合 | 171 → 171 | 176 → 176 | 174 → 174 |
| `PREF_EPISODIC` | 0 | 3（`NOISE_FILTER` + 2×`SCORES_0`，均合法） | 0 |
| StuntJumpCam / ActionCam / Ladders Climb | 2 / 2 / 2 | 2 / 2 / 2 | 2 / 2 / 2 |
| Screen Filter scaler | 5 | 5 | 5 |
| 总判定 | **PASS** | PASS | PASS |

另外做了入库级验证：三份装进游戏目录后回读 SHA-256 与产物一致，XML 解析通过。

## 这个资产不含什么

- **不含任何 Solitude 原始文件**。Solitude 作者安装说明写明不得再分发，仓库只放脚本与说明，xml 由使用者用本地 FF 官方包现场生成。
- **不含 FusionFix 官方 xml 本体**。同上，从 FF 官方包取，跑脚本即可得到等价产物。
- **不修 Solitude 的其它文件**。`timecyc.dat`、`visualSettings.dat`、`coronas.wtd`、`stipple.wtd`、`gtaRainEmitter.xml`、`timecycext.dat` 这 6 个 FF 包也自带同名但内容不同 → **必须先装 FF，再装 Solitude**，否则 Solitude 的调色会被 FF 版覆盖。

## 已知限制

- **汉化表管不到动态句**：`custom_translations.json` 是全串精确替换，只覆盖注入菜单的显示名。简报页的运行时拼装句（如 `A thief just snatched someone's bag!`）在任何 `.gxt` 里都搜不到原文（已对 8 个 gxt 做 UTF-8/UTF-16 检索），属结构性漏译。
- **`Solitude / On` 与 `Project2DFX` 不会被译**：这两串不在 asi 二进制里，87 条表的全等匹配覆盖不到，会以英文露出。要中文需另行验证 CHS 对 xml 字面串是否也替换。
- **TLAD 的 `PREF_EPISODIC_NOISE_FILTER`**（`MO_NOISE`）是原版合法槽位，5.1.2 无对应正式键，保留为一个「点了不生效」的选项，未删。
- **Distant Lights 只有 2 档**（`MO_DEF` / `Project2DFX`）。Solitude 显示的 `Solitude/P2DFX` 是它借用 `NETSTATS_TRUESKILLNAME` 的写法，官方无此文字。

## 与 G 盘 10-29 旧版（91,965 / 113,010 / 104,466）的差别

那次覆盖带入的是官方 5.1.2 底座，但有两处被改脏：`MENU_DISPLAY_CONTROL_METHOD` 被写成 `0=MO_OFF / 0=Solitude / On`（污染「按键提示方式」共用枚举）、`MENU_DISPLAY_CONSOLE_GAMMA` 把 `Xbox 360`（值 1）显示成 `Solitude / On`。本资产不含这两处，已回到官方文字。旧版备份见 `backup/game-xml-20261107/`。
