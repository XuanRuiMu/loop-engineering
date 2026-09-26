#!/usr/bin/env python3
"""仓库结构门禁：Skill 完整性、文本编码完整性与文档相对链接有效性。

与 harness-test-suite 的分工：harness 逐条验证「循环工程」这一个 Skill 的行为契约
（10 项任务，SHA-256 锁定）；本脚本只做全仓库横向体检，管三件 harness 不管的事：

1. 每个 skills/ 下的 Skill 目录都必须有 SKILL.md（漏建目录或漏传文件当场判红）；
2. 所有文本文件必须是严格 UTF-8 且不含 U+FFFD 替换字符
   （Skill 目录名与正文大量使用中文，一旦被按 GBK/ANSI 写过就会静默变成乱码，
    Git 本身不校验编码，这类损坏只能靠门禁拦）；
3. 文档里的相对链接必须指向真实存在的文件或目录
   （http/https/mailto/纯锚点不属本门禁管辖）。

退出码 0 表示全过，1 表示存在违例。
"""

import pathlib
import re
import sys
import urllib.parse

仓库根 = pathlib.Path(__file__).resolve().parents[1]
技能根 = 仓库根 / 'skills'

# 只校验这些后缀的文本文件；二进制资源（glb/png/woff2 等）不在编码门禁范围内。
文本后缀 = {
    '.md', '.json', '.py', '.ps1', '.sh', '.bat', '.txt', '.yml', '.yaml', '.cfg', '.toml',
}

# Markdown 行内链接与图片：![alt](target) / [text](target "<title>")
链接正则 = re.compile(r'!?\[[^\]]*\]\(\s*([^)\s]+)(?:\s+"[^"]*")?\s*\)')

# 这些 scheme 不做文件存在性校验
外部前缀 = ('http://', 'https://', 'mailto:', 'tel:', 'data:', '#')


def 收集文本文件(根: pathlib.Path):
    """跳过 .git 与二进制目录，返回全部需校验的文本文件。"""
    for 路径 in 根.rglob('*'):
        if not 路径.is_file():
            continue
        相对 = 路径.relative_to(仓库根)
        if 相对.parts and 相对.parts[0] == '.git':
            continue
        if 路径.suffix.lower() in 文本后缀:
            yield 路径


def 校验Skill完整性(错误: list) -> int:
    """每个 Skill 目录必须有 SKILL.md，且 SKILL.md 必须带 name/description 前置元数据。"""
    数量 = 0
    if not 技能根.is_dir():
        错误.append(f'缺少技能根目录: {技能根.relative_to(仓库根)}')
        return 数量
    目录集 = sorted(项 for 项 in 技能根.iterdir() if 项.is_dir())
    if not 目录集:
        错误.append('skills/ 下没有任何 Skill 目录')
        return 数量
    for 目录 in 目录集:
        数量 += 1
        位置 = 目录 / 'SKILL.md'
        if not 位置.is_file():
            错误.append(f'Skill 缺少 SKILL.md: {目录.relative_to(仓库根)}')
            continue
        try:
            正文 = 位置.read_text(encoding='utf-8')
        except UnicodeDecodeError as exc:
            错误.append(f'SKILL.md 不是合法 UTF-8: {位置.relative_to(仓库根)}（{exc}）')
            continue
        if not 正文.startswith('---'):
            错误.append(f'SKILL.md 缺少 YAML 前置元数据: {位置.relative_to(仓库根)}')
            continue
        头 = 正文.split('---', 2)
        头部 = 头[1] if len(头) > 2 else ''
        for 字段 in ('name:', 'description:'):
            if 字段 not in 头部:
                错误.append(f'SKILL.md 前置元数据缺 {字段} {位置.relative_to(仓库根)}')
    return 数量


def 校验编码完整性(错误: list) -> int:
    """严格 UTF-8 解码 + 拒绝 U+FFFD。返回校验文件数。"""
    数量 = 0
    for 路径 in 收集文本文件(仓库根):
        数量 += 1
        相对 = 路径.relative_to(仓库根)
        原始 = 路径.read_bytes()
        if 原始.startswith(b'\xef\xbb\xbf'):
            错误.append(f'文件带 UTF-8 BOM，需改存为无 BOM 的 UTF-8: {相对}')
        try:
            正文 = 原始.decode('utf-8')
        except UnicodeDecodeError as exc:
            错误.append(f'不是合法 UTF-8（疑似曾被按其他编码写坏）: {相对}（{exc}）')
            continue
        if '\ufffd' in 正文:
            错误.append(f'含 U+FFFD 替换字符，正文已损坏: {相对}')
    return 数量


def 校验相对链接(错误: list) -> tuple:
    """文档内的相对链接必须指向真实存在的路径。返回 (链接总数, 相对链接数)。"""
    总数 = 0
    相对数 = 0
    for 路径 in 收集文本文件(仓库根):
        if 路径.suffix.lower() != '.md':
            continue
        try:
            正文 = 路径.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            continue  # 编码问题已由校验编码完整性 单独报出
        for 目标 in 链接正则.findall(正文):
            总数 += 1
            裸 = 目标.strip()
            if 裸.startswith(外部前缀) or not 裸:
                continue
            相对数 += 1
            # 去掉查询串与锚点；中文文件名常被写成百分号编码，需先解码再判断存在性
            无锚 = 裸.split('#', 1)[0].split('?', 1)[0]
            if not 无锚:
                continue
            if '%' in 无锚:
                无锚 = urllib.parse.unquote(无锚)
            候选 = (路径.parent / 无锚).resolve()
            if not 候选.exists():
                错误.append(
                    f'文档相对链接指向不存在的路径: {路径.relative_to(仓库根)} -> {裸}'
                )
    return 总数, 相对数


def main() -> int:
    错误: list = []
    技能数 = 校验Skill完整性(错误)
    文本数 = 校验编码完整性(错误)
    链接总数, 相对链接数 = 校验相对链接(错误)

    print(f'Skill 目录: {技能数}')
    print(f'文本文件: {文本数}')
    print(f'Markdown 链接: {链接总数}（其中相对链接 {相对链接数}）')
    if 错误:
        print(f'\n结构门禁失败，共 {len(错误)} 项：')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('\n结构门禁通过：Skill 齐备、编码完好、相对链接有效')
    return 0


if __name__ == '__main__':
    sys.exit(main())
