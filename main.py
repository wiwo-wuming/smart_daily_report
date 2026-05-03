"""
智能日报分析与告警系统 - 主入口
"""
import argparse
import yaml
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 设置 UTF-8 输出
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from rich.console import Console
from rich.table import Table

from agents.collector import CollectorAgent
from agents.analyzer import AnalyzerAgent
from agents.alert_agent import AlertAgent
from agents.reporter import ReporterAgent
from utils.logger import setup_logging

console = Console()

def load_config():
    config_path = Path(__file__).parent / "config.yaml"

    # 检查配置文件是否存在
    if not config_path.exists():
        console.print(f"[red]错误: 配置文件不存在: {config_path}[/red]")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 空文件检查
    if config is None:
        console.print("[red]错误: config.yaml 为空或格式无效[/red]")
        sys.exit(1)

    # 加载 .env 文件（如果存在）
    try:
        from dotenv import load_dotenv
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            load_dotenv(env_path)
    except ImportError:
        pass

    # 解析 ${ENV_VAR} 占位符
    from utils.helpers import resolve_env_vars
    config = resolve_env_vars(config)

    # 校验 API Key 是否有效
    api_key = config.get("agent", {}).get("api_key", "")
    if not api_key or api_key.startswith("${"):
        console.print("[yellow]警告: API Key 未配置或仍为占位符，LLM 调用将失败。[/yellow]")
        console.print("[yellow]       请设置环境变量或创建 .env 文件 (参考 .env.example)[/yellow]")

    return config

def analyze_date(config, date_str: str):
    """分析指定日期的日报"""
    console.print(f"\n[bold blue]=[/bold blue] [bold]智能日报分析系统[/bold]")
    console.print(f"[dim]分析日期: {date_str}[/dim]\n")

    # 1. 采集日报
    console.print("[yellow]>> 采集日报数据...[/yellow]")
    collector = CollectorAgent(config)
    reports = collector.collect(date_str)
    console.print(f"[green]>> 采集到 {len(reports)} 份日报[/green]")

    if not reports:
        console.print("[yellow]>> 没有找到该日期的日报数据[/yellow]")
        return

    # 2. 分析每份日报
    console.print("[yellow]>> AI分析中...[/yellow]")
    analyzer = AnalyzerAgent(config)
    analyzed = []
    for report in reports:
        result = analyzer.analyze(report)
        analyzed.append(result)

    # 生成团队洞察
    console.print("[yellow]>> 生成团队洞察...[/yellow]")
    insights = analyzer.generate_insights(analyzed)
    if insights is not None:
        console.print(f"[green]>> 团队洞察: {insights.get('team_mood', 'N/A')}[/green]")

    # 显示分析结果
    _display_results(analyzed)

    # 3. 告警检测
    console.print("\n[yellow]>> 检测告警...[/yellow]")
    alert_agent = AlertAgent(config)
    alerts = alert_agent.check(analyzed)

    if alerts:
        if config.get("alerts", {}).get("enabled", False):
            console.print(f"[red]>> 检测到 {len(alerts)} 个告警，正在发送...[/red]")
            alert_agent.send(alerts)
        else:
            console.print(f"[yellow]>> 检测到 {len(alerts)} 个告警 (告警发送已禁用)[/yellow]")
    else:
        console.print("[green]>> 无需告警[/green]")

    # 4. 生成报告
    console.print("\n[yellow]>> 生成报告...[/yellow]")
    reporter = ReporterAgent(config)
    report_path = reporter.generate(analyzed, date_str)
    console.print(f"[green]>> 报告已生成: {report_path}[/green]")

def batch_analyze(config, days: int):
    """批量分析最近N天的日报"""
    console.print(f"\n[bold blue]=[/bold blue] [bold]批量日报分析 (最近{days}天)[/bold]\n")
    end_date = datetime.now()

    for i in range(days):
        date = end_date - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        console.print(f"\n[cyan]--- {date_str} ---[/cyan]")
        try:
            analyze_date(config, date_str)
        except Exception as e:
            console.print(f"[red]>> 分析失败: {e}[/red]")

def generate_report(config, period: str):
    """生成周期报告"""
    console.print(f"\n[bold blue]=[/bold blue] [bold]生成{period}报告[/bold]\n")
    reporter = ReporterAgent(config)
    report_path = reporter.generate_weekly() if period == "week" else reporter.generate_monthly()
    console.print(f"[green]>> 报告已生成: {report_path}[/green]")

def _display_results(results):
    """显示分析结果"""
    table = Table(title="日报分析结果")
    table.add_column("姓名", style="cyan")
    table.add_column("情感", style="magenta")
    table.add_column("风险", style="yellow")
    table.add_column("关键词", style="green")
    table.add_column("建议", style="blue")

    for r in results:
        sentiment_icon = "[+]" if r.sentiment == "positive" else "[~]" if r.sentiment == "neutral" else "[-]"
        risk_icon = "[!!]" if r.risk_level == "high" else "[!]" if r.risk_level == "medium" else "[OK]"
        keywords = ", ".join(r.keywords[:3]) if r.keywords else "-"
        suggestion = r.suggestions[0][:20] + "..." if r.suggestions and len(r.suggestions[0]) > 20 else (r.suggestions[0] if r.suggestions else "-")

        table.add_row(
            r.reporter,
            f"{sentiment_icon} {r.sentiment}",
            f"{risk_icon} {r.risk_level}",
            keywords,
            suggestion
        )

    console.print(table)

def main():
    parser = argparse.ArgumentParser(description="智能日报分析与告警系统")
    parser.add_argument("command", choices=["analyze", "batch", "report", "dashboard"],
                        help="命令: analyze(分析), batch(批量), report(报告), dashboard(看板)")
    parser.add_argument("--date", type=str, default="today", help="日期 (YYYY-MM-DD 或 today)")
    parser.add_argument("--days", type=int, default=7, help="批量分析天数")
    parser.add_argument("--week", action="store_true", help="生成周报")
    parser.add_argument("--month", action="store_true", help="生成月报")

    args = parser.parse_args()
    config = load_config()

    # 初始化日志系统
    log_level = config.get("logging", {}).get("level", "INFO")
    setup_logging(log_level)

    if args.command == "analyze":
        date = datetime.now().strftime("%Y-%m-%d") if args.date == "today" else args.date
        analyze_date(config, date)
    elif args.command == "batch":
        batch_analyze(config, args.days)
    elif args.command == "report":
        if not args.week and not args.month:
            parser.error("report 命令需要指定 --week 或 --month")
        generate_report(config, "week" if args.week else "month")
    elif args.command == "dashboard":
        from dashboard import run_dashboard
        run_dashboard(config)

if __name__ == "__main__":
    main()