"""
数据源基类
"""
from abc import ABC, abstractmethod
from typing import List
from models.report import DailyReport

class DataSource(ABC):
    """数据源抽象基类"""

    @abstractmethod
    def fetch_reports(self, date_str: str) -> List[DailyReport]:
        """获取指定日期的日报"""
        pass

    @abstractmethod
    def submit_report(self, report: DailyReport) -> bool:
        """提交日报"""
        pass
