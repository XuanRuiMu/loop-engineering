import pathlib
import re
import sys


技能根 = pathlib.Path(__file__).resolve().parents[3]
推理路径 = 技能根 / 'references' / '推理增强.md'
主流程路径 = 技能根 / 'SKILL.md'
提示词路径 = 技能根 / 'references' / '子代理提示词模板.md'
模板路径 = 技能根 / 'references' / 'PROGRESS模板.md'
预算路径 = 技能根 / 'BUDGET.md'
环境路径 = 技能根 / 'references' / 'EnvironmentEngineering.md'
专项技能 = ['方案审查', '三轴审查', 'Bug修复', '纾困复盘']
门区段 = {
    'G1 澄清门': ('## G1 澄清门', '## G2 风险门', [
        '两种以上读法', '能区分这些读法', '最强替代解释', '最多5个', '一次只问一个问题',
        '不得重复提问', '交主代理', '不重复执行',
    ]),
    'G2 风险门': ('## G2 风险门', '## G3 校准门', [
        '命中任一条件时执行', '公开接口或共享状态', '数据格式', '并发', '权限', '不可逆',
        '未收敛', '单一测试覆盖', '默认不命中', '具体条件', '反例：写出', '不变量', '迁移边界',
        '隐藏验收', '不可逆点', '不得只依赖自评', '计入派发前的轮次估算',
    ]),
    'G3 校准门': ('## G3 校准门', '## 与独立审查的分工', [
        '高、中、低三档', '写出推翻条件', '哪种回归会让该结论失效', '未验证', '不写入状态文件',
    ]),
    '分工': ('## 与独立审查的分工', '## 方法库', [
        'BlindSpot', '不替代独立审查', '不得因为已执行推理门就跳过独立审查',
    ]),
    '方法库': ('## 方法库', '## 决策卡', [
        '事前验尸', '逆向思考', '第一性原理', '约束移除', '红队对抗', '类比迁移', '隐藏验收',
    ]),
    '决策卡': ('## 决策卡', '## 禁止做法', [
        '最强替代解释', '区分观察', '反例或不变量', '迁移边界', '置信度', '推翻条件',
        '尝试序号', '禁止覆盖', '立即删除', '.agents/evidence/traces/',
    ]),
    '禁止做法': ('## 禁止做法', '## 来源', [
        '禁止只写“再想一遍”', '虚构风险', '投票', 'PROGRESS.md',
    ]),
}
G2触发词 = ['公开接口或共享状态', '数据格式', '并发', '权限', '不可逆', '未收敛', '单一测试覆盖']
卡片字段 = ['歧义', '最强替代解释', '区分观察', '反例或不变量', '迁移边界', '置信度', '推翻条件']
方法库 = ['事前验尸', '逆向思考', '第一性原理', '约束移除', '红队对抗', '类比迁移', '隐藏验收']


def 区段之间(内容, 起, 止):
    匹配 = re.search(re.escape(起) + r'(.*?)' + re.escape(止), 内容, re.S)
    return 匹配.group(1) if 匹配 else ''


def 验证方法库行(方法区):
    错误 = []
    for 方法 in 方法库:
        行 = [项 for 项 in 方法区.splitlines() if 项.startswith('|') and 方法 in 项]
        if not 行:
            错误.append(f'方法库缺少方法: {方法}')
            continue
        单元 = [项.strip() for 项 in 行[0].strip().strip('|').split('|')]
        if len(单元) < 3 or len(单元[2]) < 12:
            错误.append(f'{方法}没有可执行步骤')
    return 错误


def 验证推理契约(内容):
    错误 = []
    for 名称, (起, 止, 语义) in 门区段.items():
        区段 = 区段之间(内容, 起, 止)
        if not 区段.strip():
            错误.append(f'缺少或为空区段: {名称}')
            continue
        错误.extend(f'{名称}缺少语义: {项}' for 项 in 语义 if 项 not in 区段)
    错误.extend(验证方法库行(区段之间(内容, '## 方法库', '## 决策卡')))
    卡片区 = 区段之间(内容, '## 决策卡', '## 禁止做法')
    错误.extend(f'决策卡缺少字段: {字段}' for 字段 in 卡片字段 if 字段 not in 卡片区)
    来源区 = 内容.split('## 来源', 1)[-1] if '## 来源' in 内容 else ''
    if len(re.findall(r'https://', 来源区)) < 3:
        错误.append('来源节内的可核验链接少于3条')
    if '只在任务确实需要时读取' not in 内容 or '不要读取本文件' not in 内容:
        错误.append('缺少按需加载与跳过条件')
    if '不新增 `PROGRESS.md` 字段' not in 内容:
        错误.append('未声明不新增状态字段')
    return 错误


def 验证接线契约(主流程内容, 提示词内容, 模板内容):
    错误 = []
    if 'references/推理增强.md' not in 主流程内容:
        错误.append('SKILL未在读取表中登记推理增强')
    规则区 = re.search(r'## 不可破坏的规则(.*?)(?=\n## |\Z)', 主流程内容, re.S)
    if not 规则区 or '推理门' not in 规则区.group(1):
        错误.append('SKILL核心规则缺少推理门')
    阶段一 = 区段之间(主流程内容, '### 阶段1：定义目标', '### 阶段2：拆解与初始化')
    派发区 = 区段之间(主流程内容, '#### 派发', '#### 失败、stall与补位')
    阶段四 = 区段之间(主流程内容, '### 阶段4：验证与交付', '\n## 恢复')
    if not re.search(r'执行G1澄清门', 阶段一):
        错误.append('阶段1未接入G1推理门')
    if not re.search(r'功能点命中G2触发条件时，先按', 派发区):
        错误.append('阶段3派发未接入G2推理门')
    if '推理门：无' not in 派发区 or '命中的具体条件' not in 派发区:
        错误.append('阶段3派发未要求记录命中条件或未命中标记')
    if not re.search(r'执行G3校准门', 阶段四):
        错误.append('阶段4未接入G3推理门')
    for 项 in ['置信度', '支撑证据', '推翻条件', '未验证项']:
        if 项 not in 阶段四:
            错误.append(f'阶段4交付清单缺少: {项}')
    if '推理门' in 模板内容 or '决策卡' in 模板内容:
        错误.append('PROGRESS模板被写入推理门或决策卡字段')
    if '推理门' not in 提示词内容 or 'G2' not in 提示词内容:
        错误.append('Worker提示词模板未接入推理门')
    匹配 = re.search(r'## Worker 返回格式 v2.*?```text\n(.*?)```', 提示词内容, re.S)
    返回字段 = [行.split('：', 1)[0] for 行 in 匹配.group(1).splitlines() if 行.strip()] if 匹配 else []
    if len(返回字段) != 16:
        错误.append(f'Worker返回字段数量不是16: {len(返回字段)}')
    if '推理门' in 返回字段:
        错误.append('推理门被错误地加入Worker返回字段')
    return 错误


def 验证预算与环境契约(预算内容, 环境内容, 推理内容):
    错误 = []
    估算区 = 区段之间(预算内容, '## 派发前轮次估算', '## 宿主限制与 stall')
    if '推理门产物' not in 估算区:
        错误.append('BUDGET派发前轮次估算未计入推理门产物')
    if '不得把它当作零成本步骤' not in 估算区:
        错误.append('BUDGET未禁止把推理门产物当作零成本步骤')
    if '推理门产物与实现分离' not in 估算区:
        错误.append('BUDGET常见拆法缺少推理门产物与实现分离')
    if '推理决策卡' not in 环境内容:
        错误.append('EnvironmentEngineering未登记推理决策卡')
    完成区 = 环境内容.split('## 7. 完成检查', 1)[-1] if '## 7. 完成检查' in 环境内容 else ''
    for 项 in ['推翻条件', '决策卡', '未验证']:
        if 项 not in 完成区:
            错误.append(f'EnvironmentEngineering完成检查缺少: {项}')
    卡片区 = 区段之间(推理内容, '## 决策卡', '## 禁止做法')
    if 'EnvironmentEngineering.md' not in 卡片区:
        错误.append('推理增强决策卡未声明受EnvironmentEngineering约束')
    return 错误


def 变异必须失败(原文, 变异, 说明, 错误):
    if 变异(原文) == 原文:
        错误.append(f'变异未生效: {说明}')
    elif 验证推理契约(变异(原文)) == []:
        错误.append(f'{说明} 的负例被错误接受')


def main():
    错误 = []
    for 路径 in [推理路径, 主流程路径, 提示词路径, 模板路径, 预算路径, 环境路径]:
        if not 路径.is_file():
            print(f'FAIL: 缺少文件 {路径.name}')
            return 1

    推理内容 = 推理路径.read_text(encoding='utf-8')
    主流程内容 = 主流程路径.read_text(encoding='utf-8')
    提示词内容 = 提示词路径.read_text(encoding='utf-8')
    模板内容 = 模板路径.read_text(encoding='utf-8')
    预算内容 = 预算路径.read_text(encoding='utf-8')
    环境内容 = 环境路径.read_text(encoding='utf-8')
    错误.extend(验证推理契约(推理内容))
    错误.extend(验证接线契约(主流程内容, 提示词内容, 模板内容))
    错误.extend(验证预算与环境契约(预算内容, 环境内容, 推理内容))

    门变异 = [
        (lambda 文: 文.replace('命中任一条件时执行', '命中任一条件时跳过'), 'G2执行条件被反转为跳过'),
        (lambda 文: 文.replace(区段之间(文, '命中任一条件时执行', '## G3 校准门'), ''), 'G2全部执行步骤被删除'),
        (lambda 文: 文.replace(区段之间(文, '## G3 校准门', '## 与独立审查的分工'), ''), 'G3全部校准步骤被删除'),
        (lambda 文: 文.replace(区段之间(文, '## G1 澄清门', '## G2 风险门'), ''), 'G1全部澄清步骤被删除'),
        (lambda 文: '\n'.join(行 for 行 in 文.splitlines() if '最强替代解释' not in 行), '最强替代解释步骤被删除'),
        (lambda 文: 文.replace('反例：写出', '反例：可写出'), 'G2反例要求被降级为可选'),
        (lambda 文: 文.replace('写出推翻条件：出现什么观察', '可选：出现什么观察'), 'G3推翻条件被降级为可选'),
        (lambda 文: 文.replace('|事前验尸|假设交付后已经失败|写下失败时间点和用户会看到的现象；沿现象倒推最近的一个技术原因；重复到可拦截的决策点；标出最早能拦住它的一步|', '|事前验尸|假设交付后已经失败|失败原因链|'), '方法库步骤退化为空话'),
    ]
    for 变异, 说明 in 门变异:
        变异必须失败(推理内容, 变异, 说明, 错误)

    接线变异 = [
        (lambda 文: 文.replace('执行G1澄清门', '已于上次会话执行'), '阶段1停用G1'),
        (lambda 文: 文.replace('功能点命中G2触发条件时，先按', '功能点按需判断，参考'), '阶段3停用G2'),
        (lambda 文: 文.replace('执行G3校准门', '按需决定是否执行'), '阶段4停用G3'),
        (lambda 文: 文.replace('推理门：无', ''), '派发未命中标记被删除'),
    ]
    for 变异, 说明 in 接线变异:
        变异后 = 变异(主流程内容)
        if 变异后 == 主流程内容:
            错误.append(f'变异未生效: {说明}')
        elif 验证接线契约(变异后, 提示词内容, 模板内容) == []:
            错误.append(f'{说明} 的负例被错误接受')

    预算变异 = [
        (lambda 文: 文.replace('推理门产物', '附加工作'), 'BUDGET移除推理门产物品项'),
        (lambda 文: 文.replace('不得把它当作零成本步骤', '可按需省略'), 'BUDGET允许省略推理门成本'),
    ]
    for 变异, 说明 in 预算变异:
        变异后 = 变异(预算内容)
        if 变异后 == 预算内容:
            错误.append(f'变异未生效: {说明}')
        elif 验证预算与环境契约(变异后, 环境内容, 推理内容) == []:
            错误.append(f'{说明} 的负例被错误接受')
    if 验证预算与环境契约(预算内容, 环境内容.replace('## 7. 完成检查', '## 7. 收尾'), 推理内容) == []:
        错误.append('EnvironmentEngineering完成检查被删除后仍被接受')
    if 验证预算与环境契约(预算内容, 环境内容, 推理内容.replace('EnvironmentEngineering.md', '其他文件')) == []:
        错误.append('决策卡脱离EnvironmentEngineering约束后仍被接受')

    if 验证接线契约(主流程内容, 提示词内容, '推理门：x\n决策卡 y\n') == []:
        错误.append('PROGRESS模板被污染的负例被错误接受')
    if 验证接线契约(主流程内容, 提示词内容.replace('推理门', 'XX'), 模板内容) == []:
        错误.append('Worker提示词移除推理门后仍被接受')

    for 技能名 in 专项技能:
        路径 = 技能根.parent / 技能名 / 'SKILL.md'
        if not 路径.is_file():
            错误.append(f'缺少专项Skill: {技能名}')
            continue
        内容 = 路径.read_text(encoding='utf-8')
        if 技能名 == '方案审查' and ('## 澄清门' not in 内容 or '唯一区分观察' not in 内容):
            错误.append('方案审查缺少澄清门或区分观察')
        if 技能名 == '三轴审查' and ('不变量' not in 内容 or '迁移边界' not in 内容):
            错误.append('三轴审查缺少反例或不变量、迁移边界')
        if 技能名 == 'Bug修复' and ('最强替代解释' not in 内容 or '区分观察' not in 内容 or '迁移边界' not in 内容):
            错误.append('Bug修复缺少最强替代解释、区分观察或迁移边界')
        if 技能名 == '纾困复盘' and ('区分观察' not in 内容 or '推翻条件' not in 内容):
            错误.append('纾困复盘缺少区分观察或推翻条件')

    if 错误:
        print('FAIL: 推理增强契约不合规')
        for 项 in 错误:
            print(f'  - {项}')
        return 1
    print('PASS: 推理增强三门语义、方法库步骤、决策卡、接线、预算与环境接线及18个负例均有效')
    return 0


if __name__ == '__main__':
    sys.exit(main())
