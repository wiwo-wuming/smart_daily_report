"""
报告Agent - 负责生成分析报告
"""
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import json

from models.report import ReportAnalysis
from utils.llm import LLMClient

logger = logging.getLogger(__name__)


class ReporterAgent:
    """报告Agent：生成日报分析报告"""

    def __init__(self, config: dict):
        self.config = config
        self.llm = LLMClient(config.get("agent", {}))
        self.output_dir = Path(__file__).parent.parent / "reports"
        self.output_dir.mkdir(exist_ok=True)

    # ============================================================
    # 公共方法
    # ============================================================

    def _load_period_analyses(self, days: int) -> Tuple[List[dict], datetime]:
        """加载最近 N 天的所有 JSON 分析数据

        Returns:
            (analyses_list, end_date)
        """
        end_date = datetime.now()
        all_analyses = []
        for i in range(days):
            date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
            json_path = self.output_dir / f"report_{date_str}.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for a in data.get("analyses", []):
                        all_analyses.append(a)
        return all_analyses, end_date

    def _compute_stats(self, analyses: List[dict]) -> Dict:
        """计算汇总统计数据"""
        total = len(analyses)
        pos = sum(1 for a in analyses if a.get("sentiment") == "positive")
        neg = sum(1 for a in analyses if a.get("sentiment") == "negative")
        high = sum(1 for a in analyses if a.get("risk_level") == "high")
        med = sum(1 for a in analyses if a.get("risk_level") == "medium")

        member_reports = defaultdict(list)
        for a in analyses:
            member_reports[a.get("reporter", "?")].append(a)

        return {
            "total": total,
            "positive": pos,
            "negative": neg,
            "high_risk": high,
            "medium_risk": med,
            "member_reports": member_reports,
            "member_count": len(member_reports),
            "positive_pct": round(pos / total * 100, 1) if total else 0,
            "negative_pct": round(neg / total * 100, 1) if total else 0,
        }

    def _write_report(self, filename: str, content: str) -> str:
        """写入报告文件"""
        report_path = self.output_dir / filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.debug("报告已写入: %s", report_path)
        return str(report_path)

    # ============================================================
    # 日报
    # ============================================================

    def generate(self, analyses: List[ReportAnalysis], date_str: str) -> str:
        """生成单日分析报告"""
        sorted_analyses = sorted(analyses, key=lambda x: (
            0 if x.risk_level == "high" else 1 if x.risk_level == "medium" else 2
        ))

        content = self._build_report(sorted_analyses, date_str)

        report_path = self.output_dir / f"report_{date_str}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 同时生成JSON格式
        json_path = self.output_dir / f"report_{date_str}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "date": date_str,
                "total_reports": len(analyses),
                "analyses": [
                    {
                        "reporter": a.reporter,
                        "date": a.date,
                        "sentiment": a.sentiment,
                        "risk_level": a.risk_level,
                        "keywords": a.keywords,
                        "risks": a.risks,
                        "suggestions": a.suggestions,
                        "achievements": a.achievements
                    }
                    for a in sorted_analyses
                ]
            }, f, ensure_ascii=False, indent=2)

        logger.info("日报生成完成: %s", report_path)
        return str(report_path)

    # ============================================================
    # 周报
    # ============================================================

    def generate_weekly(self) -> str:
        """生成周报 - 汇总最近7天分析结果"""
        all_analyses, end_date = self._load_period_analyses(7)

        if not all_analyses:
            content = (f"# 📊 周报\n\n**日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n"
                       "暂无历史数据。请先运行 `python main.py batch --days 7` 生成每日分析。\n")
            return self._write_report("report_weekly.md", content)

        stats = self._compute_stats(all_analyses)
        start_date = (end_date - timedelta(days=6)).strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 构建报告内容
        content = f"""# 📊 周报分析

**时间范围**: {start_date} ~ {end_str}
**生成时间**: {now_str}

---

## 📈 数据概览

| 指标 | 数值 |
|------|------|
| 日报总数 | {stats['total']} 份 |
| 涉及成员 | {stats['member_count']} 人 |
| 正面情感 | {stats['positive']} ({stats['positive_pct']}%) |
| 负面情感 | {stats['negative']} ({stats['negative_pct']}%) |
| 高风险 | {stats['high_risk']} |
| 中风险 | {stats['medium_risk']} |

---

## 🔴 风险汇总

"""
        all_risks = [a for a in all_analyses if a.get("risk_level") in ("high", "medium")]
        if all_risks:
            for a in sorted(all_risks, key=lambda x: 0 if x.get("risk_level") == "high" else 1):
                content += f"- **{a.get('reporter')}** [{a.get('risk_level')}风险] {a.get('date','')}:\n"
                for risk in (a.get("risks") or []):
                    content += f"  - {risk}\n"
                content += "\n"
        else:
            content += "✅ 本周无中高风险事项\n\n"

        content += "\n## 👥 成员工作概览\n\n"
        for name, reports in sorted(stats['member_reports'].items()):
            submits = len(reports)
            kw_set = set()
            for r in reports:
                for kw in (r.get("keywords") or []):
                    kw_set.add(kw)
            content += f"### {name}\n"
            content += f"- 提交日报: {submits} 次\n"
            content += f"- 涉及关键词: {', '.join(sorted(kw_set)[:10])}\n\n"

        content += "\n---\n\n*由智能日报分析系统生成*"
        logger.info("周报生成完成")
        return self._write_report("report_weekly.md", content)

    # ============================================================
    # 月报
    # ============================================================

    def generate_monthly(self) -> str:
        """生成月报 - 汇总最近30天分析结果"""
        all_analyses, end_date = self._load_period_analyses(30)

        if not all_analyses:
            content = f"# 📊 月报\n\n**日期**: {datetime.now().strftime('%Y-%m-%d')}\n\n暂无历史数据。\n"
            return self._write_report("report_monthly.md", content)

        stats = self._compute_stats(all_analyses)
        start_date = (end_date - timedelta(days=29)).strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content = f"""# 📊 月报分析

**时间范围**: {start_date} ~ {end_str}
**生成时间**: {now_str}

---

## 📈 月度数据概览

| 指标 | 数值 |
|------|------|
| 日报总数 | {stats['total']} 份 |
| 正面情感率 | {stats['positive_pct']}% |
| 负面情感率 | {stats['negative_pct']}% |
| 高风险事项 | {stats['high_risk']} |

---

## 👥 成员活跃度

| 排名 | 成员 | 日报数 |
|------|------|--------|
"""
        sorted_members = sorted(stats['member_reports'].items(),
                                key=lambda x: len(x[1]), reverse=True)
        for i, (name, reports) in enumerate(sorted_members, 1):
            content += f"| {i} | {name} | {len(reports)} |\n"

        content += """

---

## 🔴 高风险事项

"""
        high_risks = [a for a in all_analyses if a.get("risk_level") == "high"]
        if high_risks:
            for a in high_risks:
                content += f"- **{a.get('reporter')}** ({a.get('date','')}): {'; '.join(a.get('risks', []))}\n"
        else:
            content += "✅ 本月无高风险事项\n"

        content += "\n---\n\n*由智能日报分析系统生成*"
        logger.info("月报生成完成")
        return self._write_report("report_monthly.md", content)

    # ============================================================
    # 私有方法
    # ============================================================

    def _build_report(self, analyses: List[ReportAnalysis], date_str: str) -> str:
        """构建报告内容"""
        # 统计信息
        total = len(analyses)
        if total == 0:
            return f"""# 📊 日报分析报告

**日期**: {date_str}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

暂无日报数据。

---
*由智能日报分析系统生成*
"""

        positive = sum(1 for a in analyses if a.sentiment == "positive")
        neutral = sum(1 for a in analyses if a.sentiment == "neutral")
        negative = sum(1 for a in analyses if a.sentiment == "negative")
        high_risk = sum(1 for a in analyses if a.risk_level == "high")
        medium_risk = sum(1 for a in analyses if a.risk_level == "medium")

        # 风险日报
        risk_reports = [a for a in analyses if a.risk_level in ("high", "medium")]

        content = f"""# 📊 日报分析报告

**日期**: {date_str}
**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📈 整体概览

| 指标 | 数值 |
|------|------|
| 提交日报 | {total} 份 |
| 正面情感 | {positive} ({round(positive/total*100, 1)}%) |
| 中性情感 | {neutral} ({round(neutral/total*100, 1)}%) |
| 负面情感 | {negative} ({round(negative/total*100, 1)}%) |
| 高风险 | {high_risk} |
| 中风险 | {medium_risk} |

---

## 🔴 需要关注的日报

"""

        if risk_reports:
            for report in risk_reports:
                content += f"""### {report.reporter}

**情感**: {report.sentiment} | **风险等级**: {report.risk_level}

**日报内容**:
>{report.content}

**识别风险**:
"""
                for risk in report.risks:
                    content += f"- {risk}\n"

                if report.suggestions:
                    content += "\n**建议措施**:\n"
                    for suggestion in report.suggestions:
                        content += f"- {suggestion}\n"

                content += "\n---\n\n"
        else:
            content += "暂无高风险日报，团队状态良好！✅\n\n"

        content += """---

## ✅ 正常日报

"""
        normal_reports = [a for a in analyses if a.risk_level == "low"]
        for report in normal_reports:
            content += f"- **{report.reporter}**: {report.keywords[:3] if report.keywords else '无关键词'}\n"

        content += f"""

---

## 📝 报告说明

本报告由智能日报分析系统自动生成，使用AI分析日报内容，识别风险和异常。

**分析维度**:
- 情感分析 (正面/中性/负面)
- 风险检测 (高/中/低)
- 关键词提取
- 智能建议

---
*由智能日报分析系统生成*
"""

        return content
