# smart_daily_report 待修复问题清单

> 审查时间：2026-04-29  
> 文件数：20 个 Python 源文件  
> 状态：**全部已修复** ✅

---

## 🔴 严重问题 (4 项) — 已修复

### 1. `analyzer.py:15` — `config["agent"]` 可能 KeyError 崩溃 ✅
**修复**: 已改为 `config.get("agent", {})`

### 2. `reporter.py:17` — 同上，`config["agent"]` KeyError ✅
**修复**: 已改为 `config.get("agent", {})`

### 3. `dashboard.py:244` — 告警日期排序方向与注释不符 ✅
**修复**: 已加 `reverse=True`，并调整优先级值

### 4. `alert_agent.py:26` — 空字典被判 False 跳过 ✅
**修复**: `main.py` 中已改为 `if insights is not None:`

---

## 🟡 中等问题 (3 项) — 已修复

### 5. `services/feishu_client.py` — 无 timeout ✅
**修复**: 所有 requests 调用已加 `timeout=10`，并增加 `try/except` 网络异常处理 + Token 缓存

### 6. `services/notification.py` — webhook 请求无 timeout ✅
**修复**: 所有 webhook 请求已加 `timeout=10`

### 7. `agents/reporter.py` — 地板除导致百分比和不等于 100% ✅
**修复**: 已改用 `round()`；`alert_agent.py` 中残留的 `//` 也已一并修复

---

## 🟢 轻微问题 (3 项) — 已修复

### 8. `agents/analyzer.py` — `level_map` 恒等映射冗余 ✅
**修复**: 已删除

### 9. `utils/__init__.py` — 未完整导出公共函数 ✅
**修复**: 已补充 `parse_date`、`get_date_range`、`truncate_text`、`setup_logging` 到导出列表

### 10. `utils/helpers.py` — `__post_init__` 可能意外覆盖显式空字符串 ✅
**修复**: 已改为 `if self.summary is None:`

---

## 🚀 附加优化 (本次新增)

| 优化项 | 涉及文件 |
|--------|---------|
| feishu_client 增加 Token 缓存 + 网络异常处理 | `services/feishu_client.py` |
| reporter 抽取 `_load_period_analyses()` / `_compute_stats()` 消除周月报重复代码 | `agents/reporter.py` |
| 全局 `print()` 替换为 `logging` 模块 | 全部 8 个模块 |
| 新增 `utils/logger.py` 统一日志配置 | `utils/logger.py` |
| 新增 `.env.example` 环境变量模板 | `.env.example` |
| `config.yaml` 新增 `logging.level` 配置项 | `config.yaml` |

---

## 📊 总结

| 优先级 | 数量 | 状态 |
|--------|------|------|
| 🔴 严重 | 4 | 全部修复 |
| 🟡 中等 | 3 | 全部修复 |
| 🟢 轻微 | 3 | 全部修复 |
| 🚀 优化 | 6 | 全部完成 |

> 注：所有已知问题已在 2026-04-29 第三轮审查中修复完毕。
