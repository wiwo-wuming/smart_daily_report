"""
通知服务 - 多渠道发送告警通知
"""
import logging
import requests
from typing import List
from models.alert import Alert

logger = logging.getLogger(__name__)


class NotificationService:
    """通知服务：支持微信、邮件、钉钉等多渠道"""

    def __init__(self, config: dict):
        self.config = config

    def send(self, alert: Alert):
        """发送告警"""
        if self.config.get("webhook_url"):
            self._send_wechat(alert)

        if self.config.get("email", {}).get("enabled"):
            self._send_email(alert)

        if self.config.get("dingtalk", {}).get("enabled"):
            self._send_dingtalk(alert)

    def _send_wechat(self, alert: Alert):
        """发送企业微信webhook告警"""
        webhook_url = self.config.get("webhook_url")
        if not webhook_url:
            return

        message = {
            "msgtype": "markdown",
            "markdown": {
                "content": f"""### {alert.title}

> 级别：{"🔴高" if alert.level == "high" else "🟡中" if alert.level == "medium" else "🟢低"}

**内容**:
{alert.content}

**建议**:
{chr(10).join(f'- {s}' for s in alert.suggestions) if alert.suggestions else '无'}

---
*来自智能日报分析系统*"""
            }
        }

        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("企业微信告警发送成功")
            else:
                logger.warning("企业微信告警发送失败: %s", result.get('errmsg'))
        except Exception as e:
            logger.error("企业微信告警发送异常: %s", e)

    def _send_email(self, alert: Alert):
        """发送邮件告警"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        email_config = self.config.get("email", {})
        if not email_config.get("enabled"):
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = alert.title
        msg["From"] = email_config.get("sender")
        recipients = email_config.get("recipients", [])
        if recipients:
            msg["To"] = ", ".join(recipients)

        html_content = f"""
        <html>
        <body>
            <h2>{alert.title}</h2>
            <pre>{alert.content}</pre>
            <h3>建议措施:</h3>
            <ul>
                {''.join(f'<li>{s}</li>' for s in alert.suggestions)}
            </ul>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port")) as server:
                server.starttls()
                server.login(email_config.get("sender"), email_config.get("password", ""))
                server.send_message(msg)
                logger.info("邮件告警发送成功")
        except Exception as e:
            logger.error("邮件告警发送异常: %s", e)

    def _send_dingtalk(self, alert: Alert):
        """发送钉钉webhook告警"""
        webhook_url = self.config.get("dingtalk", {}).get("webhook_url")
        if not webhook_url:
            return

        message = {
            "msgtype": "markdown",
            "markdown": {
                "title": alert.title,
                "content": f"""### {alert.title}

{alert.content}

**建议**:
{chr(10).join(f'- {s}' for s in alert.suggestions)}
"""
            }
        }

        try:
            response = requests.post(webhook_url, json=message, timeout=10)
            result = response.json()
            if result.get("errcode") == 0:
                logger.info("钉钉告警发送成功")
            else:
                logger.warning("钉钉告警发送失败: %s", result.get('errmsg'))
        except Exception as e:
            logger.error("钉钉告警发送异常: %s", e)
