# 翻译管道Bug模式 — 经验教训

> 从XRM插件4轮修复中提取的通用Bug模式和预防策略

---

## 一、核心问题：MiniMessage与Legacy格式的双轨制

### 1.1 背景

项目使用两种颜色格式：

- **MiniMessage** (`<red>`, `<gold><bold>`): Paper 1.21+ 聊天栏支持，
  通过 `sendRichMessage()` 发送
- **Legacy §** (`§c`, `§6§l`): BossBar、计分板(FastBoard)、动作栏、GUI物品名使用

### 1.2 5种输出目标的格式要求

| 输出目标 | 格式 | API |
| ---------- | ------ | ----- |
| 聊天栏 | MiniMessage | `sendRichMessage(String)` |
| 动作栏 | Legacy § | `sendActionBar(Component)` |
| BossBar | Legacy § | `setTitle(String)` |
| 计分板 | Legacy § | FastBoard API |
| 标题 | Legacy § | `sendTitle(Component)` |

### 1.3 根本矛盾

`[关键词]` 占位符在翻译YAML文件中使用，但 `获取类翻译()` 会根据 `输出目标`
参数将关键词解析为 **MiniMessage** 或 **Legacy §** 格式。一旦目标参数错误，
整个输出管道都会出错。

---

## 二、已发现的Bug模式清单

### 模式A：输出目标MiniMessage标志错误

**症状**: BossBar显示 `<yellow>`、`<red>` 等原始MiniMessage标签

**根因**: `输出目标.BossBar` 被设为 `true`（MiniMessage），但 `BossBar.setTitle()` 是 Legacy API

**修复**: 将 `BossBar(true)` 改为 `BossBar(false)`

**检测方法**:

```java
// 测试：BossBar不应使用MiniMessage
assertFalse(输出目标.BossBar.是否MiniMessage());
```

### 模式B：获取类翻译3参数版不解析关键词

**症状**: `/sx` 命令输出显示 `[暴击]======`、`[躲闪]几率` 等原始占位符

**根因**: `获取类翻译(Class, String, CommandSender)` 只做翻译，不做 `关键词解析器.解析()`

**修复**: 基方法增加关键词解析步骤

**检测方法**:

```java
// 测试：3参数版应解析关键词
String 结果 = 获取类翻译(class, key, player);
assertTrue(结果.contains("关键词颜色"));  // 应包含解析后的颜色标签
```

### 模式C：LegacyComponentSerializer收到MiniMessage字符串

**症状**: GUI菜单标题/物品名显示 `<gold><bold>任务面板`

**根因**: `Component.text(MiniMessage字符串)` 不解析MiniMessage标签；应用
`LegacyComponentSerializer.legacySection().deserialize(§字符串)` 但收到了
MiniMessage 字符串

**修复**: 使用 `MiniMessage.miniMessage().deserialize(字符串)` 或确保传入 Legacy 格式

**检测方法**: 检查所有 `LegacyComponentSerializer.legacySection().deserialize()` 调用点，确认传入字符串的来源和格式

### 模式D：sendMessage(String)收到MiniMessage字符串

**症状**: 聊天栏显示 `<red>[战斗日志]</red> 伤害数值`

**根因**: `sendMessage(String)` 是 Legacy API，但收到了 MiniMessage 格式的翻译结果

**修复**: 改为 `sendRichMessage(String)`

**检测方法**: 搜索所有 `player.sendMessage(翻译结果)` 并改为 `player.sendRichMessage(翻译结果)`

### 模式E：[关键词]后紧跟相同文字导致重复

**症状**: 战斗日志显示"蓄力蓄力0.5秒后"、"打断蓄力被打断"

**根因**: 模板 `[蓄力]蓄力[秒数:{0}]秒后` → 关键词输出"蓄力"(着色) + 模板文字"蓄力" = 重复

**修复**: 改为 `[蓄力:蓄力][秒数:{0}]秒后`（冒号+参数格式，关键词内容 = 显示文本）

**检测方法**:

```regex
\[([^\]:]+)\]\1    # 匹配 [keyword]keyword 重复模式
```

### 模式F：[关键词]无参数时关键词名称泄露为文本

**症状**: 计分板标题显示"计分板标题暮澜纪元MMORPG"

**根因**: `[计分板标题]暮澜纪元MMORPG` → 关键词名"计分板标题"作为显示文本

**修复**: 改为 `[计分板标题:暮澜纪元MMORPG]`（冒号+参数=显示文本）

**检测方法**: 检查所有 `[keyword]text` 模式，确认 `text` 是否以 `keyword` 的文字内容开头。若是，则可能重复

---

## 三、防御策略（新增代码时）

### 3.1 翻译文件编写规则

```text
✅ 正确: "[计分板标题:暮澜纪元MMORPG]"     # keyword:display_text
✅ 正确: "[蓄力:蓄力][秒数:{0}]秒后"        # keyword:keyword_content
✅ 正确: "[暴击]{0}"                        # {0} 是动态参数
❌ 错误: "[蓄力]蓄力..."                    # 关键词文字+模板文字重复
❌ 错误: "[计分板标题]暮澜纪元MMORPG"       # 关键词名会泄露
```

### 3.2 输出目标选择规则

```text
聊天消息   → explicit 输出目标.聊天栏 或 sendRichMessage()
BossBar    → explicit 输出目标.BossBar 或 LegacyComponentSerializer
计分板     → explicit 输出目标.计分板 或 FastBoard(§格式)
GUI物品名  → MiniMessage.miniMessage().deserialize() 或 LegacyComponentSerializer
动作栏     → explicit 输出目标.动作栏
```

### 3.3 发送消息规则

```text
Player 接收 → sendRichMessage(String)  // MiniMessage
Console 接收 → sendMessage(String)     // 纯文本（MiniMessage标签在控制台无害）
Component 接收 → MiniMessage.miniMessage().deserialize(String) 或 Component.text()
```

### 3.4 代码审查检查清单

- [ ] 所有 `获取类翻译()` 调用是否指定了 `输出目标`？
- [ ] 所有 `sendMessage(String)` 是否应改为 `sendRichMessage(String)`？
- [ ] 所有 `Component.text()` 是否收到了 MiniMessage 字符串？
- [ ] 所有 `LegacyComponentSerializer.legacySection().deserialize()`
  是否收到了 Legacy § 字符串？
- [ ] 翻译YAML中是否有 `[keyword]keyword_text` 重复模式？

---

## 四、为什么这些Bug测试没有发现

### 4.1 问题本质

这些都是**输出格式Bug**，不是**逻辑Bug**：

- 代码不抛异常、不崩溃
- 方法调用成功、返回非null值
- 但输出的颜色/格式是错误的

### 4.2 现有测试的盲区

现有测试只验证"方法存在"（反射检查），不验证"方法产生正确输出"。例如：

```java
// 现有测试（无效）：
assertTrue(类.getMethod("获取类翻译") != null);

// 需要的测试（有效）：
String 结果 = 获取类翻译(class, key, player, 输出目标.BossBar);
assertFalse(结果.contains("<red>"), "BossBar不应有MiniMessage标签");
```

### 4.3 修复后的测试策略

1. **翻译管道测试**: 对每个 `输出目标`，验证关键词输出格式
2. **格式守卫测试**: 验证每个输出目标的 `是否MiniMessage()` 标志
3. **模板格式测试**: 直接解析YAML翻译文件，检查模板格式
4. **端到端测试**: 模拟完整的"翻译→关键词解析→格式化→输出"管道
