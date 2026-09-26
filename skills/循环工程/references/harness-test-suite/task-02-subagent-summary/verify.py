import json
import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]
模板路径 = 技能根 / 'references' / '子代理提示词模板.md'
有效样本 = pathlib.Path(__file__).resolve().parents[1] / 'task-05-subagent-output-format' / 'samples' / 'valid.txt'
旧格式样本 = pathlib.Path(__file__).parent / 'fixture.json'
预期字段 = [
    '摘要版本', '功能点', '状态', '结果', '失败标签', '证据', '验证', '计数',
    '修改文件', '树状态', '后台任务', '审查', '遗留', '前提证伪', '契约变更', '下一步',
]


def 提取模板字段(内容):
    匹配 = re.search(r'## Worker 返回格式 v2.*?```text\s*(.*?)\s*```', 内容, re.S)
    if not 匹配:
        return []
    return [行.split('：', 1)[0] for 行 in 匹配.group(1).splitlines() if '：' in 行]


def 解析摘要(内容):
    字段 = []
    值 = {}
    for 行 in 内容.splitlines():
        if not 行.strip():
            continue
        if '：' not in 行:
            return None
        名称, 内容值 = 行.split('：', 1)
        字段.append(名称)
        值[名称] = 内容值.strip()
    return 字段, 值


def 验证摘要(内容):
    解析结果 = 解析摘要(内容)
    if 解析结果 is None:
        return ['包含无法解析的行']
    字段, 值 = 解析结果
    错误 = []
    if 字段 != 预期字段:
        错误.append(f'字段顺序或集合错误: {字段}')
    if 值.get('摘要版本') != '2':
        错误.append('摘要版本必须为2')
    for 名称 in 预期字段:
        if not 值.get(名称):
            错误.append(f'字段为空: {名称}')
    return 错误


def main():
    if not 模板路径.is_file() or not 有效样本.is_file() or not 旧格式样本.is_file():
        print('FAIL: 摘要模板、有效样本或旧格式样本缺失')
        return 1
    模板字段 = 提取模板字段(模板路径.read_text(encoding='utf-8'))
    if 模板字段 != 预期字段:
        print(f'FAIL: 权威模板字段错误: {模板字段}')
        return 1

    有效内容 = 有效样本.read_text(encoding='utf-8')
    错误 = 验证摘要(有效内容)
    if 错误:
        print('FAIL: 完整摘要正例无效')
        for 项 in 错误:
            print(f'  - {项}')
        return 1

    for 字段 in 预期字段:
        缺失内容 = '\n'.join(行 for 行 in 有效内容.splitlines() if not 行.startswith(f'{字段}：'))
        if not 验证摘要(缺失内容):
            print(f'FAIL: 删除字段{字段}后仍被接受')
            return 1

    旧数据 = json.loads(旧格式样本.read_text(encoding='utf-8'))
    if not 验证摘要('\n'.join(f'{键}：{值}' for 键, 值 in 旧数据.items())):
        print('FAIL: 旧JSON字段被错误接受')
        return 1

    print('PASS: Worker摘要v2字段完整，旧JSON契约已拒绝')
    return 0


if __name__ == '__main__':
    sys.exit(main())
