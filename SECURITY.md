# 安全策略

## 报告漏洞

如果你发现安全漏洞，**请不要**在公开 Issue 中报告。

请通过以下方式私密报告：

- 邮箱: [请填写你的联系方式]
- 或通过仓库 Security Advisory 功能提交

## 敏感信息

本项目通过以下方式保护敏感信息：

- API 密钥通过 `.env` 文件管理，已加入 `.gitignore`
- 配置文件使用 `${ENV_VAR}` 环境变量占位符
- 请勿在 Issue 或 PR 中粘贴真实 API Key、Token 等凭证

## 依赖安全

- 定期检查 `requirements.txt` 中的依赖是否存在已知漏洞
- 建议使用 `pip-audit` 或 GitHub Dependabot 自动扫描
