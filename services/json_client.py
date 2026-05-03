"""
JSON客户端 - 从JSON文件读取日报（测试用）
"""
from typing import List
from pathlib import Path
import json
from models.report import DailyReport
from services.data_source import DataSource


class JSONClient(DataSource):
    """JSON文件日报客户端"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def fetch_reports(self, date_str: str) -> List[DailyReport]:
        """从JSON文件读取指定日期的日报"""
        if not self.file_path.exists():
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        reports = []
        for item in data:
            if date_str in item.get("date", ""):
                reports.append(DailyReport(
                    reporter=item.get("reporter", "未知"),
                    date=item.get("date", ""),
                    content=item.get("content", ""),
                    source="json"
                ))

        return reports

    def submit_report(self, report: DailyReport) -> bool:
        """提交日报到JSON文件"""
        if self.file_path.exists():
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []

        data.append({
            "reporter": report.reporter,
            "date": report.date,
            "content": report.content
        })

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True
