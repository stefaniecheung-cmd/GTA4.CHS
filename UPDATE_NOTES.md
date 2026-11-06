# 更新摘要：文本管线越界修复（掌机卡顿 / 崩溃）

> 分支：`fix/font-token-bounds` ｜ 基于上游 `ckeleshi/GTA4.CHS` @ `5ddcfb1`（优化游戏版本支持说明）
> 适用：GTA IV Complete Edition 1.2.0.59 + FusionFix

## 问题现象

- ROG Xbox Ally X（890M 核显掌机）上，暂停菜单、简报页等**中文文本密集的界面**周期性卡死：帧间隔恒定 2.7~8.1 秒/帧，持续数十秒后恢复或死亡
- 用户事件日志中有 `GTA4.CHS.asi` 引发的 `0xC0000005` 崩溃记录
- PC（高性能独显）上同 mod 同配置无感——问题被硬件性能差异掩盖

## 定位过程（证据链）

1. ProceduralFixes 卡死看门狗（HangWatchdog）抓到完整 minidump（2.4GB）
2. 手写栈回溯 + 反汇编：渲染线程是唯一在执行的线程，EIP 停在 CJK 字符扫描循环，调用栈深处夹有 `GTA4.CHS.asi` 的 3 个返回地址（+0x6319 / +0x633B / +0x6585）
3. 全部辅助线程（SISCO / scripthook / Vulkan / .NET）空闲——无锁竞争、无网络、无文件 I/O
4. 反汇编 CHS.asi 确认两个 bug 的机器码位置，并与源码一一对应

## 修复内容（2 处，均在 `plugin/font.cpp`）

### Fix 1 — `GetStringWidthRemake` token 跳过循环越界（崩溃 + 卡顿主因）

```cpp
// 修复前
while (*str != '~')
// 修复后
while (*str != '~' && *str != 0)
```

字符串里最后一个 `~` 后没有第二个 token 时，循环冲出字符串结尾、扫进后续内存：扫几 MB 就是每帧几秒的卡顿，扫到未映射页就是 `0xC0000005`。**同时补上循环后的前进守卫**：因 NUL 退出时不再执行 `++str`，避免越过字符串末尾后继续被下游函数扫描。

### Fix 2 — `SkipWord` 词首 `~` 不前进导致死循环

```cpp
if (chr == ' ' || chr == '~' || chr == 0)
{
    // 新增：仅词首且是 '~' 时前进一格；NUL 不前进
    if (chr == '~' && current == begin)
    {
        ++current;
    }
    break;
}
```

`GetMaxWordWidth` 的 `while (*text != 0)` 循环在词首为 `~` 时会原地打转。原代码只在"非汉字"分支有前进保证（`if (current == begin) ++current;`），`'~'` 分支漏了。语义为：**词中 `~` 行为与原版完全一致（不前进），仅词首前进**——不对 token 边界引入任何偏移。

## 实测结果

- 掌机（890M）补丁后暂停菜单/简报不再卡死，连续游玩验证通过
- 颜色码（`~r~` / `~g~` / `~w~`）渲染精准无吞码、无错位
- 两处修复均通过逐字节反汇编验证（跳转目标全部落在指令边界）

## 附带产物

- `bin/GTA4.CHS.asi`：已打补丁的成品（B2 方案 = 源码修复的等价二进制 + PE 校验和修正），可直接覆盖 `plugins/GTA4.CHS.asi`
  - MD5：`1974283be80a83c90180410feb05b944`（版本指纹）
  - 说明：B2 二进制采用"跳板 + 扩展 .reloc 节"实现（节属性已置 EXECUTE、清除 DISCARDABLE）；标准 ASI Loader（LoadLibrary 系）验证可用；若换用手动映射型注入器，建议先用最小化 3 字节原地补丁方案对照
- 最小化替代方案（3 字节原地补丁，与 Fix 1/2 等价但词中 `~` 会前进一格）：
  - `mov edx, 0x807e` → `mov edx, 0`（token 循环 NUL 兜底）
  - `SkipWord` 中 `je break` → `je advance`（词首前进保证）

## 兼容性

- 不修改游戏本体（GTAIV.exe）；与 FusionFix / DLSS-IV / SISCO / ProceduralFixes 无地址依赖
- CHS 的 hook 走 AOB 特征码，游戏版本不变则无需重新适配

## 验证清单（回归测试项）

- [ ] 暂停菜单快速连切 20 次不卡死
- [ ] 简报/地图/统计页滚动正常
- [ ] 任务短信、剧情字幕颜色码完整
- [ ] 按键图标提示前后文字正确
- [ ] 长时间游玩无 `0xC0000005` 崩溃
