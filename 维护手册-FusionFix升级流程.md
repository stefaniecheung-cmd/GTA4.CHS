# 维护手册 · FusionFix 升级后怎么跟

适用对象：本仓库 `menu-l10n-*` 两条分支的资产（87 条菜单汉化表 + 5.1.2 官方底座菜单）。

## 一、升级的触发与判断

FusionFix 发新版时，三个东西可能变：

| 变化 | 影响 | 怎么发现 |
|---|---|---|
| `GTAIV.EFLC.FusionFix.asi` 增大/替换 | 菜单文本表位置与内容变 → 汉化表可能失配 | 记录字节数与版本串（`5.1.2.0-cad0970` 这种），对不上就重跑提取 |
| 官方 `update\...\frontend_menus.xml` 变 | 选项增减、scaler 调整、enum 重命名 → 底座要换 | 直接拿新版 xml 与旧版做逐行 diff |
| 官方 `settings\GTAIV.EFLC.FusionFix.json` 变 | 档位 choices 变（如 ScreenFilter 多一档）→ 标签语义要重核 | diff json 的 `choices` |

只要这三样里任何一样变了，就要走下面整套流程，不要只改一处。

## 二、升级流程（8 步）

**0. 备份**

```powershell
$G = "G:\Grand Theft Auto IV"
Copy-Item -LiteralPath "$G\update"  -Destination "<备份>\update-$(Get-Date -f yyyyMMdd)"  -Recurse
Copy-Item -LiteralPath "$G\plugins" -Destination "<备份>\plugins-$(Get-Date -f yyyyMMdd)" -Recurse
```

**1. 取新版原料**

- `GTAIV.EFLC.FusionFix.asi` 放进 `plugins\`；
- 新版的 `update\` 目录整份保留（后面当底座用）；
- 记下 asi 字节数，写进更新摘要的版本锚点表。

**2. 复核汉化表命中率（关键一步，不做后面全白干）**

```bash
python tools/ff_menu_extract.py <新的 .asi> keys_new.json
python tools/verify_keys.py --asi <新的 .asi> \
    --table plugins/GTA4.CHS/custom_translations.json --baseline <旧 keys.json>
```

要求 **100% 命中**。掉下来的键有两种原因：显示名拼写变了（改表里对应键），或该项被删了（从表里删掉即可，匹配不到不会报错）。

**3. 补译新增项**

`keys_new.json` 里出现、而现有表没有的显示名，逐条译成中文加进去。新键必须与 asi 里的原串**逐字相同**（大小写、空格、`+` 号都算）。

**4. 重建菜单资产**

```bash
python tools/build_ff512_solitude_menu.py \
    --src "<新版 FusionFix>\update" --out "<输出>\ff512-solitude"
```

脚本只做 `EDITS` 列表里的事，找不到 `value=… text=…` 组合会**直接报错**而不是静默改错位置。若新版把 Screen Filter 的默认档标签从 `MO_DEF` 换掉，改 `EDITS` 里的旧文本即可。

**5. 独立校验**

```bash
python tools/verify_ff512_base.py --ff "<新版 FusionFix>\update" \
    --new "<输出>\ff512-solitude\update" --expect 1
```

必须 `PASS` 且退出码 0。它检查：差异行数、是否只动 `text`、选项条目数、enum/value 全等、`PREF_` 键集合、EPISODIC 槽位合法性、5.1.2 新增控件还在、Screen Filter 的 `scaler` 仍是 5。**`--expect` 跟着 `EDITS` 的条数改。**

**6. 装机 + 回读**

```powershell
foreach ($r in @("common","TLAD","TBoGT")) {
  Copy-Item -LiteralPath "<输出>\ff512-solitude\update\$r\common\data\frontend_menus.xml" `
            -Destination "$G\update\$r\common\data\frontend_menus.xml" -Force
}
```

装完必须**重新读哈希**并与产物比，XML 解析一遍；只看「复制成功」不算数。

**7. 游戏内回归（人工，8 项）**

| # | 检查点 | 期望 |
|---|---|---|
| 1 | 显示 → 屏幕滤镜 | 首档显示 `Solitude / On`，5 档可拨，拨完退出再进不回默认 |
| 2 | 显示 → 远景灯 | `MO_DEF` / `Project2DFX` 两档 |
| 3 | 控制 → 手柄：视角灵敏度 | 拖动后退出再进仍保留（写进 `PREF_PADLOOKSENSITIVITY`） |
| 4 | 控制 → 手柄：瞄准灵敏度 / 回中延迟（步行、车内）/ 车内转向速度 | 同上，全部保留 |
| 5 | 控制 → 相机：Stunt Jump Cam / Action Cam / Ladders Climb | 三项都在（这是「没被 4.0.5 菜单顶掉」的证据） |
| 6 | 显示 → 主机版 Gamma | `MO_OFF` / `Xbox 360` / `PlayStation 3`，不是 `Solitude / On` |
| 7 | 显示 → 泛光/体积雾/太阳光束/色调映射 | 关 / 开，不是 `Solitude / On` |
| 8 | 菜单文字 | FusionFix 注入项是中文；`Solitude / On`、`Project2DFX` 允许英文 |

第 1、3、4 项是这次修的核心，缺一不可。

**8. 更新摘要与版本锚点**

改 `更新摘要-FusionFix5.1.2菜单资产.md` 的版本表（asi 版本串、三份 xml 字节、`--expect` 值），再提交。锚点不更新 = 下次维护失去基准。

## 三、可维护性评估

| 环节 | 自动化程度 | 人工判断点 | 失效模式 |
|---|---|---|---|
| 汉化表命中校验 | 全自动（`verify_keys.py`） | 判断「掉命中」是改动还是删除 | 显示名只有一两个字符变化时容易漏看 |
| 菜单底座生成 | 全自动（`build_ff512_solitude_menu.py`） | 维护 `EDITS` 列表 | 旧文本被官方改掉 → 脚本报错（这是设计好的，不会静默） |
| 产物校验 | 全自动 + 退出码（`verify_ff512_base.py`） | 按 `EDITS` 条数调 `--expect` | `--expect` 忘了改 → 误报 FAIL；改大 → 放过真实改动 |
| 装机核对 | 半自动（拷贝 + 哈希回读） | 无 | 只 `Copy-Item` 不比对 = 假完成 |
| 游戏内回归 | 纯人工 | 全部 | 最容易漏第 3、4 项（滑块写错槽正是它们） |
| 滤镜语义 | 需人读源码 | `source/timecyc.ixx` 的 switch 分支 | 上游若给 `eMO_DEF` 加 case，值 0 不再是「原味」 |

**结论：中等偏高可维护。** 文本层（汉化表 + 菜单标签）已完全脚本化、可复跑、可断言；真正的维护成本不在代码，在两处**语义判断**：

1. 官方把某个 enum/scaler 改了以后，「这个标签还挂在原来语义上吗」必须人读源码确认（Screen Filter 就是典型：`0` 的含义来自 `default: break`）。
2. Solitude 侧没有版本号可锚，只能靠「菜单里有 `Solitude / On` 字样 + `scaler="0"` 锁死」这些特征识别新版本，判断成本高于 FF。

**风险最高的三件事（按危害排序）：**

1. 拿 Solitude 的 xml 当底座 → 滑块绑回联机占位槽，所有自定义设置「调了不生效」，且联机菜单文字被污染。**永远不要**。
2. `scaler` 被改小/改大 → 拨不到值或越界写值。
3. TLAD 的 `PREF_EPISODIC_NOISE_FILTER` / `PREF_EPISODIC_SCORES_0` 被当成「违规槽位」清掉 → TLAD 少功能。它们是原版合法用法，`verify_ff512_base.py` 的白名单里已写明。

## 四、回滚

| 想回滚到 | 做法 |
|---|---|
| 官方原味菜单 | 直接用 FF 官方包里的三份 xml 覆盖（会失去 `Solitude / On` 标签，其余功能不受影响） |
| 10-29 的旧版 | `backup/game-xml-20261107/` 三份（91,965 / 113,010 / 104,466） |
| 旧汉化表 | 上游仓库 `master` 根的 `custom_translations.json` |

## 五、文件对照

| 路径 | 作用 |
|---|---|
| `plugins/GTA4.CHS/custom_translations.json` | 87 条菜单汉化（全串精确替换） |
| `update/{common,TLAD,TBoGT}/common/data/frontend_menus.xml` | 5.1.2 官方底座 + 1 处滤镜标签 |
| `plugins/GTAIV.EFLC.FusionFix.cfg` | `ScreenFilter = 0`、`DistantLights = 1` 等运行时开关 |
| `tools/ff_menu_extract.py` | 从 asi 抽显示名 |
| `tools/verify_keys.py` | 汉化表命中率校验 |
| `tools/build_ff512_solitude_menu.py` | 生成菜单资产 |
| `tools/verify_ff512_base.py` | 产物与官方逐行/逐键校验 |
| `tools/compare_solitude_vs_ff.py` | FF 与 Solitude 逐菜单对照（排查「它到底改了什么」） |
