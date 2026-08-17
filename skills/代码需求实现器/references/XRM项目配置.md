# XRM插件项目配置

## 基本信息

- **项目名**：XRM（暮澜纪元 MMORPG 核心插件）
- **项目路径**：`D:\XiTongWenJianJia\ZhuoMian\燃烧之陨我的世界服务端\暮澜纪元我的世界MMORPG服务端\plugins\玄锐暮插件\XRM`
- **语言**：Java 25
- **构建工具**：Gradle Kotlin DSL
- **主包**：`暮澜纪元`（中文包名）

## 目录结构

| 类型     | 路径                                                           |
| -------- | -------------------------------------------------------------- |
| 源码根   | `src/main/java/`                                               |
| 测试根   | `src/test/java/`                                               |
| 翻译文件 | `src/main/resources/文本消息/`（三层镜像结构，跳过暮澜纪元层） |
| 配置文件 | `src/main/resources/config.yml`                                |
| 插件描述 | `src/main/resources/plugin.yml`                                |

## 构建命令

| 操作     | 命令                                      |
| -------- | ----------------------------------------- |
| 编译     | `gradle compileJava`                      |
| 运行测试 | `gradle runTests`（需 `-PrunTests=true`） |
| 构建JAR  | `gradle build`                            |
| 编译测试 | `gradle compileTestJava`                  |

## 测试框架

- JUnit Jupiter 6.1.0 + Mockito 5.23.0
- 测试类名格式：实现类名 + "测试"（如 `修饰器测试.java`）
- 测试文件路径完全镜像实现文件路径

## 哈希清单

- **脚本路径**：`D:\XiTongWenJianJia\ZhuoMian\燃烧之陨我的世界服务端\暮澜纪元我的世界MMORPG服务端\plugins\玄锐暮插件\XRM\sync_manifest.py`
- **清单文件**：`.sync-manifest.json`（位于XRM根目录）

### 命令

| 命令             | 用法                                                                           | 说明                                 |
| ---------------- | ------------------------------------------------------------------------------ | ------------------------------------ |
| scan             | `python sync_manifest.py scan --base-dir <XRM路径>`                            | 全量扫描生成清单                     |
| check            | `python sync_manifest.py check --base-dir <XRM路径>`                           | 检测变更文件（对比清单）             |
| update           | `python sync_manifest.py update --base-dir <XRM路径> --source-file <相对路径>` | 更新指定文件的清单状态               |
| generate-reports | `python sync_manifest.py generate-reports --base-dir <XRM路径> [--force]`      | 为缺失测试报告的条目自动生成报告模板 |

### 强制规则

1. **开发前**：运行 `python sync_manifest.py check` 检测哪些源文件发生了变更
2. **修改代码后**：运行 `python sync_manifest.py update --source-file <路径>` 更新清单状态
3. **测试完成后**：运行 `python sync_manifest.py generate-reports` 生成测试报告
4. **交付前**：运行 `python sync_manifest.py check` 确认所有条目为 synced
5. **翻译修改后**：运行 `python sync_manifest.py scan` 重新生成清单

## 翻译文件规范

### 三层镜像结构

翻译文件按Java类的包路径镜像，**跳过`暮澜纪元/`这一层**：

| Java类路径                                  | 翻译文件路径                                  |
| ------------------------------------------- | --------------------------------------------- |
| `暮澜纪元/战斗/伤害服务.java`               | `文本消息/战斗/伤害服务/zh.yml`               |
| `暮澜纪元/命令/管理员指令.java`             | `文本消息/命令/管理员指令/zh.yml`             |
| `暮澜纪元/技能/法术/奥能法师/奥术冲击.java` | `文本消息/技能/法术/奥能法师/奥术冲击/zh.yml` |

### 规则

- 每个Java类对应一个翻译文件目录，目录下按语言代码命名（zh.yml, en.yml等）
- YAML顶级键为类名，翻译键路径包含类名前缀
- 必须用UTF-8编码加载
- 玩家可见输出测试必须验证最终中文文本
- 翻译API使用 `获取类翻译(类.class, "类名.键", 发送者)` 和 `发送类翻译(发送者, 类.class, "类名.键", 参数)`
- 禁止使用旧的功能分类翻译API（`获取翻译("功能分类", "键")`、`发送(玩家, "功能分类", "键")`等已删除）

## 依赖

- Purpur API 26.1.2
- ProtocolLib（数据包监听）
- Citizens（NPC交互）
- EliteMobs（精英怪）

## 编码规范

- 变量/方法/类名优先中文
- 用户可见文本必须使用翻译文件
- 数值/名称/路径必须可配置
- 输入验证用白名单
- 错误消息不暴露内部实现
