"""
采集Agent - 负责从各个数据源采集日报数据
"""
import logging
from typing import List
from datetime import datetime, timedelta
from models.report import DailyReport
from services.feishu_client import FeishuClient
from services.excel_client import ExcelClient
from services.json_client import JSONClient

logger = logging.getLogger(__name__)


class CollectorAgent:
    """采集Agent：从多数据源收集日报数据"""

    def __init__(self, config: dict):
        self.config = config
        self.data_sources = config.get("data_sources", {})

    def collect(self, date_str: str) -> List[DailyReport]:
        """
        采集指定日期的日报
        支持多种数据源并行采集，单个数据源异常不影响其他数据源
        """
        reports = []

        # 飞书采集
        if self.data_sources.get("feishu", {}).get("enabled"):
            try:
                client = FeishuClient(self.data_sources["feishu"])
                feishu_reports = client.fetch_reports(date_str)
                reports.extend(feishu_reports)
            except Exception as e:
                logger.warning("飞书数据源采集失败: %s", e)

        # Excel采集
        if self.data_sources.get("excel", {}).get("enabled"):
            try:
                client = ExcelClient(self.data_sources["excel"]["path"])
                excel_reports = client.fetch_reports(date_str)
                reports.extend(excel_reports)
            except Exception as e:
                logger.warning("Excel数据源采集失败: %s", e)

        # JSON采集（测试用）
        if self.data_sources.get("json", {}).get("enabled"):
            try:
                client = JSONClient(self.data_sources["json"]["path"])
                json_reports = client.fetch_reports(date_str)
                reports.extend(json_reports)
            except Exception as e:
                logger.warning("JSON数据源采集失败: %s", e)

        return reports

    def collect_range(self, start_date: str, end_date: str) -> List[DailyReport]:
        """采集日期范围内的所有日报"""
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        all_reports = []
        current = start

        while current <= end:
            date_str = current.strftime("%Y-%m-%d")
            reports = self.collect(date_str)
            all_reports.extend(reports)
            current += timedelta(days=1)

        return all_reports
