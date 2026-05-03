"""
日报相关数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class DailyReport:
    """原始日报"""
    reporter: str           # 报告人
    date: str              # 日期 YYYY-MM-DD
    content: str            # 日报内容
    source: str = "unknown" # 数据来源
    record_id: str = ""     # 记录ID（用于关联）

@dataclass
class ReportAnalysis:
    """日报分析结果"""
    reporter: str
    date: str
    content: str
    keywords: List[str] = field(default_factory=list)
    sentiment: str = "neutral"  # positive, neutral, negative
    risk_level: str = "low"     # high, medium, low
    risks: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    achievements: List[str] = field(default_factory=list)
    summary: str = ""
    raw_analysis: Dict = field(default_factory=dict)

    def __post_init__(self):
        if self.summary is None:
            self.summary = self.raw_analysis.get("summary", "")
