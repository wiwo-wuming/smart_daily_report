"""
分析Agent - 负责分析日报内容，提取关键信息
"""
import logging
from typing import List, Dict
from models.report import DailyReport, ReportAnalysis
from utils.llm import LLMClient
import json
import re

logger = logging.getLogger(__name__)


class AnalyzerAgent:
    """分析Agent：使用LLM分析日报内容"""

    def __init__(self, config: dict):
        self.config = config
        self.llm = LLMClient(config.get("agent", {}))
        self.analysis_config = config.get("analysis", {})

    def _safe_json_parse(self, text: str) -> dict:
        """安全解析 JSON，兼容 LLM 返回的 markdown 代码块格式"""
        text = text.strip()

        # 先尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试提取 ```json ... ``` 或 ``` ... ``` 中的内容（取第一个完整代码块）
        match = re.search(r'```(?:json)?\s*\n(.*?)\n\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 尝试提取第一个 { ... } 对象（使用贪婪匹配最后一个 }）
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        # 全部失败，返回空字典
        logger.warning("JSON 解析失败，原始响应: %s...", text[:200])
        return {}

    def analyze(self, report: DailyReport) -> ReportAnalysis:
        """
        分析单条日报
        1. 关键词提取
        2. 情感分析
        3. 风险识别
        4. 建议生成
        """
        prompt = self._build_analysis_prompt(report)

        response = self.llm.chat_safe(prompt)
        result = self._safe_json_parse(response)

        return ReportAnalysis(
            reporter=report.reporter,
            date=report.date,
            content=report.content,
            keywords=result.get("keywords", []),
            sentiment=result.get("sentiment", "neutral"),
            risk_level=result.get("risk_level", "low"),
            risks=result.get("risks", []),
            suggestions=result.get("suggestions", []),
            achievements=result.get("achievements", []),
            raw_analysis=result
        )

    def batch_analyze(self, reports: List[DailyReport]) -> List[ReportAnalysis]:
        """批量分析日报"""
        return [self.analyze(r) for r in reports]

    def _build_analysis_prompt(self, report: DailyReport) -> str:
        """构建分析提示词"""
        risk_kw = ", ".join(self.analysis_config.get("risk_keywords", []))
        positive_kw = ", ".join(self.analysis_config.get("positive_keywords", []))

        prompt = f"""你是一个专业的技术团队日报分析助手。请分析以下日报，提取关键信息。

日报内容：
- 报告人：{report.reporter}
- 日期：{report.date}
- 内容：{report.content}

请以JSON格式返回分析结果，包含以下字段：
{{
    "keywords": ["关键词1", "关键词2", ...],  // 工作相关关键词，最多5个
    "sentiment": "positive/neutral/negative",  // 整体情感倾向
    "risk_level": "high/medium/low",  // 风险等级
    "risks": ["风险描述1", "风险描述2"],  // 识别出的风险点
    "suggestions": ["建议1", "建议2"],  // 给报告人的建议
    "achievements": ["成果1", "成果2"],  // 识别出的工作成果
    "summary": "一句话总结"  // 日报摘要
}}

风险关键词参考：{risk_kw}
积极关键词参考：{positive_kw}

只返回JSON，不要有其他内容。"""
        return prompt

    def generate_insights(self, analyses: List[ReportAnalysis]) -> Dict:
        """基于多份日报分析生成团队洞察"""
        report_summaries = "\n".join([
            f"- {a.reporter} ({a.date}): {a.summary if a.summary else a.content[:50]}..."
            for a in analyses[:10]
        ])
        prompt = f"""你是一个技术团队管理者。请分析以下团队成员的日报总结，生成团队层面的洞察。

{report_summaries}

请生成JSON格式的团队洞察：
{{
    "team_mood": "团队整体氛围描述",
    "main_progress": ["主要进展1", "主要进展2"],
    "blockers": ["阻塞问题1", "阻塞问题2"],
    "recommendations": ["团队改进建议1", "建议2"],
    "highlight_members": ["表现出色的成员1", "成员2"],
    "needs_attention": ["需要关注的成员1", "成员2"]
}}

只返回JSON。"""
        response = self.llm.chat_safe(prompt)
        return self._safe_json_parse(response)
