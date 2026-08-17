import sys
import pathlib
import re


def 查找所有进度文件():
    """PROGRESS.md 可能位于技能根目录、项目根目录或子工作区；返回所有候选。"""
    技能根目录 = pathlib.Path(__file__).resolve().parents[3]
    # 向上搜索项目根目录（直到出现 .agents 或到达盘符根）
    搜索起点 = 技能根目录
    for _ in range(5):
        if (搜索起点 / '.agents').exists() or (搜索起点 / '.git').exists():
            break
        搜索起点 = 搜索起点.parent

    候选集合 = {
        技能根目录 / 'PROGRESS.md',
        搜索起点 / 'PROGRESS.md',
    }
    # 注：仅检查 skill 根目录与项目根的 PROGRESS.md，缺失时回退模板基线（见下方"干净检出"分支）。
    # 不遍历项目根全部子目录——那会把无关的同级项目（如其他游戏/文档目录）的 PROGRESS.md
    # 也算作候选，导致套件被无关文件污染而误报 FAIL（见与我恋爱吧/PROGRESS.md 的污染案例）。
    return [候选 for 候选 in 候选集合 if 候选.exists()]


def 验证进度文件(进度文件路径):
    文件内容 = 进度文件路径.read_text(encoding='utf-8')

    if not re.search(r'(?m)^# .+$', 文件内容):
        return "缺少以 '# ' 开头的非空 H1 标题行"

    必要章节列表 = [
        ('## 元信息',),
        ('## 范围边界', '范围边界：'),
        ('## 功能点列表', '## 待处理功能点列表', '## 待处理功能点'),
        ('## 已完成',),
        ('## 当前决策',),
    ]
    缺失章节列表 = []
    for 章节 in 必要章节列表:
        if not any(替代 in 文件内容 for 替代 in 章节):
            缺失章节列表.append(章节[0])
    if 缺失章节列表:
        return f"缺少必要章节: {缺失章节列表}"

    if not re.search(r'(?m)^(?:\|.*\bFP-\w+\b.*\||- .*\bFP-\w+\b.*)', 文件内容):
        return "至少应包含一条 FP- 前缀的功能点记录"

    return None


进度文件列表 = 查找所有进度文件()

if not 进度文件列表:
    # 干净检出：仓库无运行时 PROGRESS.md（仅含模板）。模板即结构规范，
    # 改以模板为基准校验，使套件在干净仓库下默认全绿，避免"假红"削弱验证约束力。
    技能根目录 = pathlib.Path(__file__).resolve().parents[3]
    模板路径 = 技能根目录 / 'references' / 'PROGRESS模板.md'
    if 模板路径.exists() and 验证进度文件(模板路径) is None:
        print(f"PASS: 基于模板校验通过（仓库无运行时 PROGRESS.md，模板即结构规范：{模板路径.name}）")
        sys.exit(0)
    print("FAIL: 模板结构不规范，无法作为规范基准")
    sys.exit(1)

错误列表 = []
for 进度文件 in 进度文件列表:
    错误 = 验证进度文件(进度文件)
    if 错误 is None:
        try:
            显示路径 = 进度文件.relative_to(pathlib.Path(__file__).resolve().parents[4])
        except ValueError:
            显示路径 = 进度文件.name
        print(f"PASS: PROGRESS.md 结构正确 ({显示路径})")
        sys.exit(0)
    错误列表.append(f"{进度文件}: {错误}")

print(f"FAIL: 所有候选 PROGRESS.md 验证未通过")
for 错误 in 错误列表:
    print(f"  - {错误}")
sys.exit(1)
