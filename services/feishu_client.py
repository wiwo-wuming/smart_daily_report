"""
飞书客户端 - 从飞书多维表格采集日报
"""
import time
import logging
from typing import List, Optional
import requests
from models.report import DailyReport
from services.data_source import DataSource

logger = logging.getLogger(__name__)


class FeishuClient(DataSource):
    """飞书客户端"""

    def __init__(self, config: dict):
        self.app_id = config.get("app_id")
        self.app_secret = config.get("app_secret")
        self.app_token = config.get("app_token")
        self.table_id = config.get("table_id")
        self.base_url = "https://open.feishu.cn/open-apis"
        self._cached_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    def _get_access_token(self) -> str:
        """获取 tenant_access_token（带缓存，有效期约2小时）"""
        # Token 未过期则复用（提前5分钟刷新）
        if self._cached_token and time.time() < self._token_expires_at - 300:
            return self._cached_token

        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"飞书获取 access_token 网络异常: {e}")

        data = response.json()
        if data.get("code") != 0:
            raise Exception(f"飞书获取 access_token 失败: {data.get('msg', 'unknown')}")
        token = data.get("tenant_access_token", "")
        if not token:
            raise Exception("飞书 access_token 为空")

        # 缓存 token，默认有效期 7200 秒
        expire = data.get("expire", 7200)
        self._cached_token = token
        self._token_expires_at = time.time() + expire
        logger.info("飞书 access_token 刷新成功 (有效期 %ds)", expire)
        return token

    def fetch_reports(self, date_str: str) -> List[DailyReport]:
        """从飞书多维表格获取日报"""
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"
        params = {"page_size": 100}

        reports = []
        has_more = True

        while has_more:
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error("飞书获取表格记录网络异常: %s", e)
                break

            data = response.json()

            if data.get("code") != 0:
                logger.warning("飞书 API 返回错误: %s", data.get("msg", "unknown"))
                break

            items = data.get("data", {}).get("items", [])

            for item in items:
                fields = item.get("fields", {})
                report_date = str(fields.get("日期", ""))

                if date_str in report_date:
                    reports.append(DailyReport(
                        reporter=fields.get("姓名", "未知"),
                        date=report_date,
                        content=fields.get("日报内容", ""),
                        source="feishu",
                        record_id=item.get("record_id")
                    ))

            has_more = data.get("data", {}).get("has_more", False)
            if has_more:
                params["page_token"] = data.get("data", {}).get("page_token")

        return reports

    def submit_report(self, report: DailyReport) -> bool:
        """提交日报到飞书"""
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        url = f"{self.base_url}/bitable/v1/apps/{self.app_token}/tables/{self.table_id}/records"

        payload = {
            "fields": {
                "姓名": report.reporter,
                "日期": report.date,
                "日报内容": report.content
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return response.json().get("code") == 0
        except requests.exceptions.RequestException as e:
            logger.error("飞书提交日报网络异常: %s", e)
            return False
