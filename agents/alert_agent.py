"""
告警Agent - 负责检测异常并触发告警
"""
import logging
from typing import List, Dict
from models.report import ReportAnalysis
from models.alert import Alert
from datetime import datetime

logger = logging.getLogger(__name__)


class AlertAgent:
    """告警Agent：根据分析结果判断是否需要告警"""

    def __init__(self, config: dict):
        self.config = config
        self.alert_config = config.get("alerts", {})
        self.analysis_config = config.get("analysis", {})
        self.notification = None
        self._silenced_until: dict = {}  # alert_id -> silenced_until timestamp

    def check(self, analyses: List[ReportAnalysis]) -> List[Alert]:
        """
        检查是否需要告警
        告警触发条件：
        1. 情感分析为negative
        2. 风险等级为high
        3. 检测到风险关键词
        4. 团队整体异常（如多人同时出现negative）
        """
        alerts = []

        for analysis in analyses:
            # 单人风险检测
            if self._should_alert(analysis):
                alert = self._create_alert(analysis)
                alerts.append(alert)

        # 团队异常检测
        team_alert = self._check_team_anomaly(analyses)
        if team_alert:
            alerts.append(team_alert)

        return alerts

    def _should_alert(self, analysis: ReportAnalysis) -> bool:
        """判断单条日报是否需要告警"""
        # 高风险直接告警
        if analysis.risk_level == "high":
            return True

        # negative情感告警
        if analysis.sentiment == "negative":
            return True

        # 检测到风险关键词
        risk_keywords = self.analysis_config.get("risk_keywords", [])
        content = analysis.content
        for keyword in risk_keywords:
            if keyword in content:
                return True

        return False

    def _check_team_anomaly(self, analyses: List[ReportAnalysis]) -> Alert:
        """检测团队异常模式"""
        if len(analyses) < 3:
            return None

        negative_count = sum(1 for a in analyses if a.sentiment == "negative")
        high_risk_count = sum(1 for a in analyses if a.risk_level == "high")

        # 超过30%的人negative，或超过20%高风险
        threshold = len(analyses)

        if negative_count / threshold > 0.3 or high_risk_count / threshold > 0.2:
            return Alert(
                alert_type="team_anomaly",
                level="high",
                title="团队整体异常",
                content=f"检测到团队异常：{negative_count}人情感偏负面({round(negative_count/threshold*100, 1)}%)，{high_risk_count}人存在高风险问题({round(high_risk_count/threshold*100, 1)}%)",
                affected_members=[a.reporter for a in analyses],
                suggestions=["建议组织团队会议了解情况", "检查是否存在系统性问题"],
                alert_id=f"team_anomaly_{analyses[0].date if analyses else datetime.now().strftime('%Y%m%d')}"
            )

        return None

    def _create_alert(self, analysis: ReportAnalysis) -> Alert:
        """为单条日报创建告警"""
        level = analysis.risk_level if analysis.risk_level in ("high", "medium", "low") else "medium"

        title = f"【{analysis.reporter}】日报告警"

        content = f"""报告人：{analysis.reporter}
日期：{analysis.date}
情感：{analysis.sentiment}
风险等级：{analysis.risk_level}

日报内容：
{analysis.content}

识别风险：
{chr(10).join(f"• {r}" for r in analysis.risks) if analysis.risks else "无明显风险"}

建议措施：
{chr(10).join(f"• {s}" for s in analysis.suggestions) if analysis.suggestions else "继续保持"}"""

        return Alert(
            alert_type="individual",
            level=level,
            title=title,
            content=content,
            affected_members=[analysis.reporter],
            suggestions=analysis.suggestions,
            alert_id=f"{analysis.reporter}_{analysis.date}"
        )

    def send(self, alerts: List[Alert]):
        """发送告警通知"""
        if not self.alert_config.get("enabled", False):
            return

        if self.notification is None:
            self.notification = self._init_notification()

        for alert in alerts:
            if self._is_silenced(alert):
                logger.debug("告警 %s 处于静默期，跳过发送", alert.alert_id)
                continue
            self.notification.send(alert)
            alert.status = "acknowledged"

    def _init_notification(self):
        """初始化通知服务"""
        from services.notification import NotificationService
        return NotificationService(self.alert_config)

    def silence(self, alert_id: str, duration_hours: int = 24):
        """静默告警 - 临时屏蔽指定告警"""
        from datetime import datetime, timedelta
        until = datetime.now() + timedelta(hours=duration_hours)
        self._silenced_until[alert_id] = until
        logger.info("告警 %s 已静默至 %s", alert_id, until.strftime('%Y-%m-%d %H:%M:%S'))

    def _is_silenced(self, alert: "Alert") -> bool:
        """检查告警是否处于静默期"""
        from datetime import datetime
        until = self._silenced_until.get(alert.alert_id)
        if until is None:
            return False
        if datetime.now() > until:
            del self._silenced_until[alert.alert_id]
            return False
        return True
