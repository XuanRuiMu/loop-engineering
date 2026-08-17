# 任务 5：验证子代理输出摘要字段格式

## 描述
验证子代理返回摘要中的 `token_estimate`、`failure_tags`、`evidence_link` 字段符合 `references/子代理提示词模板.md` 的格式要求。

## 输入
`samples/` 下每个 `.txt` 是一个摘要示例；`verify.py` 以"文件名是否以 `valid` 开头"判定该示例应被接受还是拒绝。当前覆盖解析器全部 7 个失败分支 + 1 个有效路径：

- `samples/valid.txt`：字段齐全、格式正确的有效摘要（应通过）
- `samples/invalid_missing_token_estimate.txt`：缺少 `token_estimate`（分支：缺少 token_estimate 字段）
- `samples/invalid_empty_token_estimate.txt`：`token_estimate` 为空（分支：token_estimate 必须是非空字符串）
- `samples/invalid_missing.txt`：缺少 `failure_tags` 与 `evidence_link`（分支：缺少 failure_tags / 缺少 evidence_link）
- `samples/invalid_failure_tags_bad.txt`：`failure_tags` 取非法值（分支：failure_tags 值不在合法集合）
- `samples/invalid_typo.txt`：`evidence_link` 含拼写错误 `skidence`（分支：evidence_link 拼写错误）
- `samples/invalid_evidence_prefix.txt`：`evidence_link` 前缀非 `.agents/evidence/`（分支：evidence_link 路径前缀错误）

新增/删除 fixture 时，须保证上述 7 个失败分支仍各有至少一个样本覆盖。

## 预期输出
- `PASS: 子代理输出摘要字段格式验证通过`

## 验证命令

```bash
python task-05-subagent-output-format/verify.py
```
