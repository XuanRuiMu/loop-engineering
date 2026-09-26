import pathlib
import re
import sys
import tempfile


技能根 = pathlib.Path(__file__).resolve().parents[3]
证据规范 = 技能根 / 'EVIDENCE.md'
类别目录 = {'traces', 'proposals', 'validations'}


def 查找项目根():
    for 候选 in [技能根, *技能根.parents]:
        if (候选 / '.agents' / 'evidence').is_dir():
            return 候选
    return None


def 验证证据路径(值, 项目根):
    if 值 == '无':
        return True
    if not isinstance(值, str) or not 值 or '\\' in 值 or ':' in 值 or '|' in 值:
        return False
    路径 = pathlib.PurePosixPath(值)
    if 路径.is_absolute() or '..' in 路径.parts or not 值.startswith('.agents/evidence/'):
        return False
    类别 = 路径.parts[2] if len(路径.parts) > 2 else ''
    if 类别 not in 类别目录:
        return False
    证据根 = (项目根 / '.agents' / 'evidence').resolve()
    目标 = (项目根 / pathlib.Path(*路径.parts)).resolve()
    try:
        目标.relative_to(证据根)
    except ValueError:
        return False
    return 目标.is_file()


def 创建结构(项目根):
    for 名称 in 类别目录:
        (项目根 / '.agents' / 'evidence' / 名称).mkdir(parents=True, exist_ok=True)


def main():
    错误列表 = []
    项目根 = 查找项目根()
    if 项目根 is not None:
        for 名称 in 类别目录:
            if not (项目根 / '.agents' / 'evidence' / 名称).is_dir():
                错误列表.append(f'真实项目缺少证据目录: {名称}')
    with tempfile.TemporaryDirectory() as 临时目录:
        模拟项目 = pathlib.Path(临时目录)
        创建结构(模拟项目)
        错误列表.extend(验证路径用例(模拟项目))

    if not 证据规范.is_file():
        错误列表.append('缺少EVIDENCE.md')
        证据内容 = ''
    else:
        证据内容 = 证据规范.read_text(encoding='utf-8')
    for 标题 in ['## 证据记录格式', '## 活跃证据']:
        if 标题 not in 证据内容:
            错误列表.append(f'EVIDENCE.md缺少标题: {标题}')
    编号列表 = re.findall(r'(?m)^\|\s*\d{4}-\d{2}-\d{2}\s*\|\s*(EV-\d{3})\s*\|', 证据内容)
    if not 编号列表:
        错误列表.append('EVIDENCE.md没有合法证据记录')
    if len(编号列表) != len(set(编号列表)):
        错误列表.append('EVIDENCE.md存在重复证据ID')

    if 错误列表:
        print('FAIL: 证据结构或路径契约不合规')
        for 错误 in 错误列表:
            print(f'  - {错误}')
        return 1
    print('PASS: 证据目录、记录、唯一编号和路径边界均有效')
    return 0


def 验证路径用例(项目根):
    错误 = []
    证据文件 = 项目根 / '.agents' / 'evidence' / 'traces' / 'fp-test.md'
    证据文件.parent.mkdir(parents=True, exist_ok=True)
    证据文件.write_text('ok', encoding='utf-8')
    if not 验证证据路径('.agents/evidence/traces/fp-test.md', 项目根):
        错误.append('真实证据路径正例未通过')
    非法值 = [
        '.agents/skidence/traces/fp-test.md',
        '.agents/evidence/../outside.md',
        str(证据文件),
        '.agents/evidence/traces',
        'https://example.invalid/evidence.md',
        '.agents/evidence/traces/missing.md',
        '.agents/evidence/references/fp-test.md',
        '.agents/evidence/traces\\fp-test.md',
    ]
    for 值 in 非法值:
        if 验证证据路径(值, 项目根):
            错误.append(f'非法证据路径被接受: {值}')
    return 错误


if __name__ == '__main__':
    sys.exit(main())
