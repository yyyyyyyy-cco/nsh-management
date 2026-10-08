# 安全政策

> 面向**使用者与安全研究者**：如何报告漏洞、我们如何处理、以及哪些风险已被明确接受。
> 本文件不复制安全结论——**权威源是 [`memory-bank/security-review.md`](memory-bank/security-review.md)**。

## 支持的版本

| 版本 | 安全更新 |
|------|----------|
| 最新发布标签（当前 `v1.2.0`）及其后的 `main` | ✅ 支持 |
| 更早的历史标签（`v1.1.0` / `v1.0.0`） | ❌ 不支持，请升级到最新标签 |

本项目为私有部署的帮会管理系统（非 SaaS），安全修复随新标签发布。

## 报告漏洞

**请勿使用公开 Issue 披露安全漏洞细节，也不要在公开渠道粘贴真实密钥、Token 或玩家个人信息。**

**首选渠道（私有，仅维护者可见）**：GitHub「Report a vulnerability」

- 入口：<https://github.com/yyyyyyyy-cco/nsh-management/security/advisories/new>
- 该渠道支持在私密环境中讨论、验证与协同修复，并可在修复后发布安全公告（GHSA）。

**备用渠道（邮件）**：`<待填写：维护者安全联系邮箱>`

- 该占位符需由维护者填写后生效；**在填写之前请使用上方 GitHub 私有渠道**。

### 报告中请包含

1. 受影响版本/标签与部署形态（Docker Compose 拓扑、是否置于反向代理之后）；
2. **最小化复现步骤**；必要时附请求样例与相关日志片段（请先脱敏）；
3. 影响评估：可读取或修改哪些数据、是否需要已登录、是否需要 admin/developer 身份；
4. 若该问题属于已记录的**已知接受风险**，请注明（见下节）。

## 我们如何处理

| 阶段 | 目标时间（尽力而为，非法律承诺） |
|------|----------------------------------|
| 确认收到并回复初判 | 7 天内 |
| 给出修复或缓解方案 | 30 天内（高危优先） |
| 公开披露细节 | 修复发布之后；如需署名请在报告中说明 |

如你已公开披露，我们会同步评估影响并尽快修复。

## 安全边界与已知接受风险

- 已实施措施（JWT + 角色权限、登录限流、bcrypt、上传限制、Nginx 限流、异常脱敏、Token 版本吊销等）
  与**已知接受风险**（`plain_password` 明文列仅开发者可见、Token 存于 localStorage、帮众共享账号等）
  均记录在 [`memory-bank/security-review.md`](memory-bank/security-review.md)——**以该文件为准**。
- 生产环境使用弱 `SECRET_KEY` 时应用会**拒绝启动**（启动门禁）；门禁说明与排查命令见
  [`DEPLOY.md`](DEPLOY.md) §六 与常见问题 Q6。
- 部署侧的 TLS、限流、密钥管理与对外暴露面见 [`DEPLOY.md`](DEPLOY.md)。

## 合规标准口径

本项目的安全评估依据与合规整改路线（OWASP ASVS 5.0、OWASP Top 10:2025、SLSA v1.2、
CIS Docker Benchmark、12-Factor 等）见
[`.agent/plans/compliance-remediation-plan.md`](.agent/plans/compliance-remediation-plan.md) §2；
逐项整改进度见 [`memory-bank/progress.md`](memory-bank/progress.md)。