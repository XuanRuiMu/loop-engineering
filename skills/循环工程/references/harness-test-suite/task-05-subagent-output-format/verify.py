import re
import sys
import pathlib


样本目录 = pathlib.Path(__file__).parent / 'samples'
合法失败标签集合 = {'鉴权', '网络', '数据', '逻辑', '依赖', '未知', '无'}
证据路径前缀 = '.agents/evidence/'


def 解析字段(文件路径):
    内容 = 文件路径.read_text(encoding='utf-8')
    字段映射 = {}
    for 行 in 内容.splitlines():
        匹配 = re.match(r'^(token_estimate|failure_tags|evidence_link)\s*[:：]\s*(.*)$', 行)
        if 匹配:
            字段映射[匹配.group(1)] = 匹配.group(2).strip()
    return 字段映射


def 验证摘要字段(字段映射):
    错误列表 = []

    if 'token_estimate' not in 字段映射:
        错误列表.append('缺少 token_estimate 字段')
    elif not isinstance(字段映射['token_estimate'], str) or not 字段映射['token_estimate']:
        错误列表.append('token_estimate 必须是非空字符串')

    if 'failure_tags' not in 字段映射:
        错误列表.append('缺少 failure_tags 字段')
    elif 字段映射['failure_tags'] not in 合法失败标签集合:
        错误列表.append(f"failure_tags 值 {字段映射['failure_tags']!r} 不在合法集合 {合法失败标签集合} 中")

    if 'evidence_link' not in 字段映射:
        错误列表.append('缺少 evidence_link 字段')
    else:
        链接值 = 字段映射['evidence_link']
        if 'skidence' in 链接值:
            错误列表.append(f"evidence_link 存在拼写错误：{链接值!r}")
        elif not 链接值.startswith(证据路径前缀):
            错误列表.append(f"evidence_link 路径前缀错误：{链接值!r}")

    return 错误列表


def main():
    if not 样本目录.exists():
        print("FAIL: samples 目录不存在")
        sys.exit(1)

    样本文件列表 = sorted(样本目录.glob('*.txt'))
    if not 样本文件列表:
        print("FAIL: samples 目录下没有样本文件")
        sys.exit(1)

    全部通过 = True
    for 样本文件 in 样本文件列表:
        字段映射 = 解析字段(样本文件)
        错误列表 = 验证摘要字段(字段映射)
        样本名 = 样本文件.name
        是否应通过 = 样本名.startswith('valid')
        实际通过 = len(错误列表) == 0

        if 是否应通过 and not 实际通过:
            print(f"FAIL: {样本名} 是有效样本但未通过验证: {'; '.join(错误列表)}")
            全部通过 = False
        elif not 是否应通过 and 实际通过:
            print(f"FAIL: {样本名} 是无效样本但通过了验证")
            全部通过 = False

    if 全部通过:
        print("PASS: 子代理输出摘要字段格式验证通过")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
