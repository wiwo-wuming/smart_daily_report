# 📊 智能日报分析与告警系统

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

</div>

基于多 Agent 架构的智能日报分析系统，自动采集、分析日报数据，识别异常并及时告警。

## ✨ 功能特性

- 🤖 **多 Agent 协作** — Collector / Analyzer / Alert / Reporter 四 Agent 协同工作
- 📡 **多源数据采集** — 支持飞书多维表格、Excel/CSV、JSON 等多种数据源
- 🧠 **LLM 智能分析** — 关键词提取、情感分析、风险识别、团队洞察
- 🔔 **多渠道告警** — 企业微信、邮件、钉钉 Webhook 多渠道通知
- 📊 **可视化看板** — Flask Web 界面，Chart.js 趋势图表、成员对比、告警面板
- 📋 **周期报告** — 自动生成日报、周报、月报

## 🏗️ 项目结构

```
smart_daily_report/
├── main.py                  # CLI 主入口
├── config.yaml              # 配置文件
├── requirements.txt         # Python 依赖
├── dashboard.py             # Flask 可视化看板
├── test_all_modules.py      # 全量模块自检
│
├── agents/                  # Agent 模块
│   ├── collector.py         # 采集 Agent — 多数据源日报采集
│   ├── analyzer.py          # 分析 Agent — LLM 智能分析
│   ├── alert_agent.py       # 告警 Agent — 异常检测与多渠道推送
│   └── reporter.py          # 报告 Agent — 日报/周报/月报生成
│
├── services/                # 服务层
│   ├── data_source.py       # 数据源抽象基类
│   ├── feishu_client.py     # 飞书多维表格客户端
│   ├── excel_client.py      # Excel/CSV 客户端
│   ├── json_client.py       # JSON 数据客户端
│   └── notification.py      # 多渠道通知服务
│
├── models/                  # 数据模型
│   ├── report.py            # DailyReport / ReportAnalysis
│   └── alert.py             # Alert
│
├── utils/                   # 工具模块
│   ├── llm.py               # OpenAI 兼容 LLM 客户端
│   ├── helpers.py           # 日期/文本/配置辅助函数
│   └── logger.py            # 统一日志配置
│
├── data/                    # 数据目录
│   ├── sample_reports.json  # 示例日报数据
│   └── daily_reports.csv    # CSV 格式示例
│
└── reports/                 # 运行时生成的报告 (.gitignore 排除)
```

## 🚀 快速开始

### 1. 环境要求

- Python 3.9+
- DeepSeek API Key（或其他 OpenAI 兼容接口）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 填入你的 API Key
# DEEPSEEK_API_KEY=sk-your-key-here
```

### 4. 运行

```bash
# 分析今天日报
python main.py analyze --date today

# 批量分析最近 7 天
python main.py batch --days 7

# 生成周报 / 月报
python main.py report --week
python main.py report --month

# 启动可视化看板 → http://localhost:5000
python main.py dashboard

# 运行全量自检
python test_all_modules.py
```

## 📊 Agent 协作流程

```
Collector Agent                     Analyzer Agent
  ┌──────────┐                      ┌──────────────┐
  │ 飞书      │────┐                 │ 关键词提取    │
  │ Excel/CSV │────┤  日报数据  ──→  │ 情感分析      │ ──→  Alert Agent
  │ JSON      │────┘                 │ 风险识别      │       ┌──────────┐
  └──────────┘                      │ 团队洞察      │       │ 异常检测  │
                                    └──────────────┘       │ 多渠道推送│
                                           │                └──────────┘
                                           ↓
                                    Reporter Agent
                                      ┌──────────┐
                                      │ 日报/周报  │
                                      │ 月报      │
                                      │ JSON+MD   │
                                      └──────────┘
```

## 📈 实际运行示例

```
= 智能日报分析系统
分析日期: 2026-04-29

>> 采集日报数据...
>> 采集到 5 份日报
>> AI分析中...
>> 团队洞察: 团队整体积极高效，多数成员按计划推进，支付模块需关注

                  日报分析结果
┌──────┬──────────┬────────┬──────────────────────┐
│ 姓名 │ 情感     │ 风险   │ 关键词               │
├──────┼──────────┼────────┼──────────────────────┤
│ 李四 │ positive │ low    │ 订单模块, API对接     │
│ 王五 │ negative │ high   │ 支付模块, 联调测试    │
│ 赵六 │ positive │ low    │ 完成, 上线, 优化      │
└──────┴──────────┴────────┴──────────────────────┘

>> 检测到 1 个告警
>> 报告已生成: reports/report_2026-04-29.md
```

## 🔧 扩展开发

### 添加自定义数据源

继承 `DataSource` 基类：

```python
from services.data_source import DataSource
from models.report import DailyReport

class CustomDataSource(DataSource):
    def fetch_reports(self, date_str: str) -> list[DailyReport]:
        # 实现数据获取
        ...

    def submit_report(self, report: DailyReport) -> bool:
        # 实现数据提交
        ...
```

### 添加告警渠道

在 `NotificationService` 中新增 `_send_xxx()` 方法，然后在 `send()` 中调用即可。

## 📝 日志配置

在 `config.yaml` 中调整日志级别：

```yaml
logging:
  level: "INFO"   # DEBUG | INFO | WARNING | ERROR
```

## ⚠️ 注意事项

- `.env` 文件包含 API 密钥，已被 `.gitignore` 排除
- `reports/` 目录为运行时产物，不上传 Git
- 飞书数据源需具备 Bitable 读取权限
- 企业微信/钉钉告警需创建 Webhook 机器人

## 🤝 参与贡献

请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解贡献流程，[SECURITY.md](SECURITY.md) 了解安全策略。

## 📄 License

MIT © 2026 dps325799
