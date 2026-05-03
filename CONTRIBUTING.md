# 贡献指南

感谢你对智能日报分析与告警系统的关注！

## 如何贡献

### 报告 Bug

1. 在 [Issues](../../issues) 中搜索是否已有相同问题
2. 创建新 Issue，选择 "Bug Report" 模板
3. 描述复现步骤、预期行为和实际行为

### 提交功能请求

1. 在 [Issues](../../issues) 中搜索是否已有类似请求
2. 创建新 Issue，选择 "Feature Request" 模板
3. 说明使用场景和期望效果

### 提交代码

1. Fork 本仓库
2. 创建特性分支: `git checkout -b feature/your-feature`
3. 编写代码并确保通过测试: `python test_all_modules.py`
4. 提交变更: `git commit -m "feat: 添加 xxx 功能"`
5. 推送到分支: `git push origin feature/your-feature`
6. 创建 Pull Request 到 `main` 分支

### Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具变更

### 代码风格

- Python 3.9+
- 遵循 PEP 8 规范
- 新增模块需在 `test_all_modules.py` 中添加自检项
