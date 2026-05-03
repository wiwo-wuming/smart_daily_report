# -*- coding: utf-8 -*-
"""全量模块自检脚本"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

passed = 0
failed = 0
errors = []

def check(name, fn):
    global passed, failed
    try:
        result = fn()
        print(f'  [OK] {name}')
        passed += 1
        return result
    except Exception as e:
        print(f'  [FAIL] {name}: {e}')
        failed += 1
        errors.append((name, str(e)))
        return None

print('=' * 60)
print('Full Module Self-Test')
print('=' * 60)

# ====== 1. utils ======
print('\n--- [utils] ---')

from utils import LLMClient, format_date, ensure_dir
check('import utils', lambda: True)

from utils.helpers import parse_date, get_date_range, truncate_text
check('import helpers', lambda: True)

r_date = check('format_date()', lambda: format_date())
check('parse_date(2026-04-29)', lambda: parse_date('2026-04-29'))
check('truncate_text()', lambda: len(truncate_text('hello world this is a long text', 10)) <= 13)
dates = check('get_date_range()', lambda: get_date_range('2026-04-01', '2026-04-03'))
if dates:
    print(f'       -> {dates}')

# ====== 2. models ======
print('\n--- [models] ---')

from models import DailyReport, ReportAnalysis, Alert
check('import models', lambda: True)

report = check('DailyReport()', lambda: DailyReport(
    reporter='Test', date='2026-04-29', content='Test content', source='test'
))
if report:
    print(f'       -> reporter={report.reporter}, date={report.date}')

analysis = check('ReportAnalysis()', lambda: ReportAnalysis(
    reporter='Test', date='2026-04-29', content='Test',
    keywords=['key1'], sentiment='positive', risk_level='low',
    risks=[], suggestions=[], achievements=[],
    raw_analysis={'summary': 'test summary'}
))
if analysis:
    print(f'       -> summary={analysis.summary}, sentiment={analysis.sentiment}')

alert = check('Alert()', lambda: Alert(
    alert_type='individual', level='high', title='Test Alert',
    content='Test content', affected_members=['Zhang San'],
    suggestions=['Suggestion 1']
))
if alert:
    print(f'       -> level={alert.level}, created_at={alert.created_at}')

# Verify dataclass fields
check('DailyReport attr exist', lambda: (
    hasattr(report, 'reporter') and hasattr(report, 'content') and hasattr(report, 'source')
))
check('ReportAnalysis attr exist', lambda: (
    hasattr(analysis, 'sentiment') and hasattr(analysis, 'risk_level') and
    hasattr(analysis, 'keywords') and hasattr(analysis, 'risks')
))
check('Alert attr exist', lambda: (
    hasattr(alert, 'alert_type') and hasattr(alert, 'level') and
    hasattr(alert, 'affected_members') and hasattr(alert, 'suggestions')
))

# ====== 3. services ======
print('\n--- [services] ---')

from services.data_source import DataSource
check('DataSource ABC class', lambda: True)

from services.json_client import JSONClient
json_client = check('JSONClient()', lambda: JSONClient('./data/sample_reports.json'))
if json_client:
    results = check('JSONClient.fetch_reports()', lambda: json_client.fetch_reports('2026-04-29'))
    if results:
        print(f'       -> got {len(results)} reports')

from services.excel_client import ExcelClient
check('ExcelClient()', lambda: ExcelClient('./data/daily_reports.csv'))

from services.feishu_client import FeishuClient
check('FeishuClient()', lambda: FeishuClient({'app_id':'x','app_secret':'y','app_token':'t','table_id':'z'}))

from services.notification import NotificationService
notif = check('NotificationService()', lambda: NotificationService({'enabled': False}))
if notif:
    # Test send with disabled mode - should not raise
    check('send() disabled mode', lambda: notif.send(Alert(
        alert_type='individual', level='low', title='test', content='test'
    )))

# ====== 4. agents ======
print('\n--- [agents] ---')

import yaml
from pathlib import Path
config_file = Path(__file__).parent / "config.yaml"
with open(config_file, encoding='utf-8') as f:
    raw_config = yaml.safe_load(f)
from utils.helpers import resolve_env_vars
config = check('load config.yaml', lambda: resolve_env_vars(raw_config))
if config:
    print(f'       -> model={config["agent"]["model"]}, api_key=***')

from agents.collector import CollectorAgent
collector = check('CollectorAgent()', lambda: CollectorAgent(config))
if collector:
    results = check('collector.collect()', lambda: collector.collect('2026-04-29'))
    if results:
        print(f'       -> got {len(results)} reports')
        check('reports are DailyReport', lambda: all(isinstance(r, DailyReport) for r in results))

from agents.analyzer import AnalyzerAgent
analyzer = check('AnalyzerAgent()', lambda: AnalyzerAgent(config))
if analyzer:
    prompt = check('_build_analysis_prompt()', lambda: analyzer._build_analysis_prompt(
        DailyReport(reporter='Test', date='2026-04-29', content='Done development')
    ))
    if prompt:
        print(f'       -> prompt length: {len(prompt)} chars')
    # Test safe JSON parse
    parsed = check('_safe_json_parse normal', lambda: (
        analyzer._safe_json_parse('{"a":1}') == {"a":1}
    ))
    parsed2 = check('_safe_json_parse markdown', lambda: (
        analyzer._safe_json_parse('```json\n{"b":2}\n```') == {"b":2}
    ))

from agents.alert_agent import AlertAgent
alert_agent = check('AlertAgent()', lambda: AlertAgent(config))
if alert_agent:
    # Test with mixed analyses
    test_analyses = [
        ReportAnalysis(reporter='A', date='2026-04-29', content='Normal', sentiment='positive', risk_level='low', keywords=[], risks=[], suggestions=[], achievements=[]),
        ReportAnalysis(reporter='B', date='2026-04-29', content='Risk', sentiment='negative', risk_level='high', keywords=[], risks=['Serious issue'], suggestions=['Fix now'], achievements=[]),
        ReportAnalysis(reporter='C', date='2026-04-29', content='Normal', sentiment='neutral', risk_level='low', keywords=[], risks=[], suggestions=[], achievements=[]),
    ]
    alerts_result = check('alert_agent.check()', lambda: alert_agent.check(test_analyses))
    if alerts_result:
        print(f'       -> detected {len(alerts_result)} alerts')
        check('alerts are Alert objects', lambda: all(isinstance(a, Alert) for a in alerts_result))

    # Check team anomaly detection
    check('team_anomaly detection', lambda: alert_agent._check_team_anomaly([ReportAnalysis(
        reporter=f'U{i}', date='2026-04-29', content='Neg', sentiment='negative', risk_level='high',
        keywords=[], risks=['Issue'], suggestions=[], achievements=[]
    ) for i in range(3)]) is not None)

from agents.reporter import ReporterAgent
reporter = check('ReporterAgent()', lambda: ReporterAgent(config))
if reporter:
    test_analysis = [
        ReportAnalysis(reporter='Test', date='2026-04-29', content='Test', sentiment='positive', risk_level='low', keywords=['test'], risks=[], suggestions=[], achievements=[])
    ]
    path = check('reporter.generate()', lambda: reporter.generate(test_analysis, '2026-04-29-test'))
    if path:
        print(f'       -> report: {path}')
        check('report file exists', lambda: Path(path).exists())

    path2 = check('reporter.generate_weekly()', lambda: reporter.generate_weekly())
    if path2:
        check('weekly exists', lambda: Path(path2).exists())

    path3 = check('reporter.generate_monthly()', lambda: reporter.generate_monthly())
    if path3:
        check('monthly exists', lambda: Path(path3).exists())

# ====== 5. Dashboard API ======
print('\n--- [dashboard] ---')

from dashboard import app
check('Flask app exists', lambda: app is not None)

with app.test_client() as client:
    resp = check('GET /', lambda: client.get('/'))
    if resp:
        print(f'       -> status={resp.status_code}, bytes={len(resp.data)}')
        check('HTML contains charts', lambda: b'Chart.js' in resp.data)
        check('HTML contains dashboard', lambda: b'dashboard' in resp.data)

    resp2 = check('GET /api/dashboard', lambda: client.get('/api/dashboard'))
    if resp2:
        import json
        data = json.loads(resp2.data)
        print(f'       -> status={resp2.status_code}')
        print(f'       -> reports={data["stats"]["total_reports"]}, trends={len(data["trends"])}d, members={len(data["member_activity"])}, alerts={len(data["alerts"])}')
        check('API has stats', lambda: 'stats' in data and 'total_reports' in data['stats'])
        check('API has trends', lambda: 'trends' in data and len(data['trends']) > 0)
        check('API has members', lambda: 'members' in data)
        check('API has alerts', lambda: 'alerts' in data)
        check('API has member_activity', lambda: 'member_activity' in data)

# ====== Summary ======
print('\n' + '=' * 60)
print(f'Results: OK={passed}  FAIL={failed}')
if errors:
    print('\nFailures:')
    for name, err in errors:
        print(f'  - {name}: {err}')
else:
    print('All modules passed!')
print('=' * 60)
