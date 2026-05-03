"""
Excel客户端 - 从Excel/CSV文件读取日报
"""
from typing import List
from pathlib import Path
import pandas as pd
from models.report import DailyReport
from services.data_source import DataSource


class ExcelClient(DataSource):
    """Excel/CSV日报客户端"""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def fetch_reports(self, date_str: str) -> List[DailyReport]:
        """从Excel/CSV文件读取指定日期的日报"""
        if not self.file_path.exists():
            return []

        # 根据文件后缀自动选择读取方式
        suffix = self.file_path.suffix.lower()
        if suffix == ".csv":
            try:
                df = pd.read_csv(self.file_path, encoding="utf-8")
            except UnicodeDecodeError:
                df = pd.read_csv(self.file_path, encoding="gbk")
        else:
            df = pd.read_excel(self.file_path, engine="openpyxl")

        # 假设列名：姓名, 日期, 日报内容
        # 筛选日期
        df["日期"] = df["日期"].astype(str)
        filtered = df[df["日期"].str.contains(date_str)]

        reports = []
        for _, row in filtered.iterrows():
            reports.append(DailyReport(
                reporter=row.get("姓名", "未知"),
                date=str(row.get("日期", "")),
                content=row.get("日报内容", ""),
                source="excel"
            ))

        return reports

    def submit_report(self, report: DailyReport) -> bool:
        """提交日报到Excel/CSV文件"""
        new_df = pd.DataFrame([{
            "姓名": report.reporter,
            "日期": report.date,
            "日报内容": report.content
        }])

        suffix = self.file_path.suffix.lower()
        if self.file_path.exists():
            if suffix == ".csv":
                existing_df = pd.read_csv(self.file_path, encoding="utf-8")
            else:
                existing_df = pd.read_excel(self.file_path, engine="openpyxl")
            combined = pd.concat([existing_df, new_df], ignore_index=True)
        else:
            combined = new_df

        if suffix == ".csv":
            combined.to_csv(self.file_path, index=False, encoding="utf-8")
        else:
            combined.to_excel(self.file_path, index=False, engine="openpyxl")

        return True
