"""
告警相关数据模型
"""
from dataclasses import dataclass, field
from typing import List
from datetime import datetime

@dataclass
class Alert:
    """告警模型"""
    alert_type: str         # alert_type: individual, team_anomaly
    level: str              # high, medium, low
    title: str              # 告警标题
    content: str            # 告警内容
    affected_members: List[str] = field(default_factory=list)  # 受影响成员
    suggestions: List[str] = field(default_factory=list)         # 建议措施
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    alert_id: str = ""      # 告警ID
    status: str = "pending" # pending, acknowledged, resolved, silenced
