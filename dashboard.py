"""
Dashboard - 可视化看板 (Flask Web)
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter
from flask import Flask, render_template_string, jsonify

logger = logging.getLogger(__name__)

app = Flask(__name__)

REPORTS_DIR = Path(__file__).parent / "reports"

TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>📊 智能日报分析看板</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f172a; color: #e2e8f0; min-height:100vh}
.header{background:linear-gradient(135deg,#1e293b,#334155); padding:20px 30px; border-bottom:2px solid #3b82f6}
.header h1{font-size:24px; margin-bottom:5px}
.header span{color:#94a3b8; font-size:14px}
.dashboard{padding:20px 30px; max-width:1400px; margin:0 auto}
.stats{display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:15px; margin-bottom:25px}
.card{background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155}
.card h3{color:#94a3b8; font-size:13px; text-transform:uppercase; margin-bottom:8px}
.card .value{font-size:32px; font-weight:bold}
.card .sub{font-size:13px; color:#94a3b8; margin-top:4px}
.positive{color:#22c55e}
.neutral{color:#eab308}
.negative{color:#ef4444}
.high{color:#ef4444}
.mid{color:#f97316}
.charts{display:grid; grid-template-columns: 1fr 1fr; gap:20px; margin-bottom:25px}
.chart-box{background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155}
.chart-box h3{margin-bottom:15px; color:#94a8b3}
.chart-box canvas{max-height:300px}
.team-grid{display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:15px; margin-bottom:25px}
.member-card{background:#1e293b; border-radius:12px; padding:18px; border:1px solid #334155}
.member-card.risk-high{border-color:#ef4444; box-shadow:0 0 12px rgba(239,68,68,0.1)}
.member-card.risk-medium{border-color:#f97316}
.member-name{font-size:16px; font-weight:bold; margin-bottom:6px}
.member-meta{font-size:12px; color:#94a3b8; margin-bottom:8px}
.member-keywords{display:flex; flex-wrap:wrap; gap:4px; margin-top:6px}
.tag{font-size:11px; padding:2px 8px; border-radius:10px; background:#334155; color:#e2e8f0}
.tag.risk{background:rgba(239,68,68,0.2); color:#ef4444}
.tag.good{background:rgba(34,197,94,0.2); color:#22c55e}
.alerts-box{background:#1e293b; border-radius:12px; padding:20px; border:1px solid #334155}
.alert-item{display:flex; align-items:center; gap:10px; padding:10px; border-radius:8px; margin-bottom:8px; background:#0f172a}
.alert-badge{font-size:11px; padding:3px 10px; border-radius:10px; font-weight:bold}
.badge-high{background:#ef4444; color:white}
.badge-medium{background:#f97316; color:white}
.badge-low{background:#22c55e; color:white}
.alert-member{color:#3b82f6; font-weight:bold}
.loading{text-align:center; padding:40px; color:#94a3b8}
.refresh{display:inline-block; margin-left:15px; font-size:12px; color:#3b82f6; cursor:pointer}
@media(max-width:768px){.charts{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="header">
  <h1>📊 智能日报分析看板 <span class="refresh" onclick="location.reload()">🔄 刷新</span></h1>
  <span>实时监控团队日报动态 | {{ date_range }}</span>
</div>
<div class="dashboard" id="app">
  <div class="loading">⏳ 加载数据中...</div>
</div>
<script>
async function loadData(){
  const resp = await fetch('/api/dashboard');
  const data = await resp.json();
  render(data);
}
function render(d){
  const stats = d.stats;
  const html = `
  <div class="stats">
    <div class="card"><h3>📋 日报总数</h3><div class="value">${stats.total_reports}</div><div class="sub">最近${d.days}天累计</div></div>
    <div class="card"><h3>😊 正面情感</h3><div class="value positive">${stats.positive}%</div><div class="sub">${stats.positive_count} 份</div></div>
    <div class="card"><h3>😐 中性情感</h3><div class="value neutral">${stats.neutral}%</div><div class="sub">${stats.neutral_count} 份</div></div>
    <div class="card"><h3>😟 负面情感</h3><div class="value negative">${stats.negative}%</div><div class="sub">${stats.negative_count} 份</div></div>
    <div class="card"><h3>🔴 高风险</h3><div class="value high">${stats.high_risk}</div><div class="sub">需立即处理</div></div>
    <div class="card"><h3>🟡 中风险</h3><div class="value mid">${stats.medium_risk}</div><div class="sub">需关注</div></div>
  </div>
  <div class="charts">
    <div class="chart-box"><h3>📈 情感趋势</h3><canvas id="sentimentChart"></canvas></div>
    <div class="chart-box"><h3>⚠️ 风险趋势</h3><canvas id="riskChart"></canvas></div>
  </div>
  <div class="chart-box" style="margin-bottom:25px"><h3>👥 团队成员活跃度</h3><canvas id="memberChart"></canvas></div>
  <div class="alerts-box">
    <h3>🚨 最新风险告警</h3>
    ${d.alerts.length === 0 ? '<p style="color:#22c55e;text-align:center;padding:20px">✅ 暂无告警，团队状态良好</p>' :
      d.alerts.map(a => `
        <div class="alert-item">
          <span class="alert-badge badge-${a.level}">${a.level === 'high' ? '🔴 高' : a.level === 'medium' ? '🟡 中' : '🟢 低'}</span>
          <span class="alert-member">${a.reporter}</span>
          <span style="flex:1">${a.content}</span>
          <span style="color:#94a3b8;font-size:12px">${a.date}</span>
        </div>`).join('')
    }
  </div>
  <div class="chart-box" style="margin-top:25px">
    <h3>👥 团队成员详情 <span style="font-weight:normal;color:#94a3b8;font-size:12px">(最近一天)</span></h3>
    <div class="team-grid">
      ${d.members.map(m => `
        <div class="member-card risk-${m.risk_level}">
          <div class="member-name">${m.reporter}</div>
          <div class="member-meta">
            情感: <span class="${m.sentiment}">${m.sentiment}</span> | 
            风险: <span class="${m.risk_level.startsWith('h') ? 'high' : m.risk_level.startsWith('m') ? 'mid' : ''}">${m.risk_level}</span>
            | ${m.date}
          </div>
          <div class="member-keywords">
            ${(m.keywords || []).map(k => {
              const cls = d.risk_kw.includes(k) ? 'risk' : d.positive_kw.includes(k) ? 'good' : '';
              return `<span class="tag ${cls}">${k}</span>`;
            }).join('')}
          </div>
        </div>`).join('')
      }
    </div>
  </div>`;
  document.getElementById('app').innerHTML = html;

  // Charts
  const labels = d.trends.map(t => t.date);
  new Chart(document.getElementById('sentimentChart'), {
    type:'line', data:{
      labels,
      datasets:[
        {label:'正面', data:d.trends.map(t=>t.positive), borderColor:'#22c55e', backgroundColor:'rgba(34,197,94,0.1)', fill:true, tension:0.3},
        {label:'中性', data:d.trends.map(t=>t.neutral), borderColor:'#eab308', backgroundColor:'rgba(234,179,8,0.1)', fill:true, tension:0.3},
        {label:'负面', data:d.trends.map(t=>t.negative), borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,0.1)', fill:true, tension:0.3}
      ]
    }, options:{responsive:true, plugins:{legend:{position:'bottom',labels:{color:'#94a3b8'}}}, scales:{x:{ticks:{color:'#64748b'}}, y:{ticks:{color:'#64748b'}}}}
  });
  new Chart(document.getElementById('riskChart'), {
    type:'bar', data:{
      labels,
      datasets:[
        {label:'高风险', data:d.trends.map(t=>t.high_risk), backgroundColor:'#ef4444'},
        {label:'中风险', data:d.trends.map(t=>t.medium_risk), backgroundColor:'#f97316'}
      ]
    }, options:{responsive:true, plugins:{legend:{position:'bottom',labels:{color:'#94a3b8'}}}, scales:{x:{ticks:{color:'#64748b'}}, y:{ticks:{color:'#64748b'}, beginAtZero:true}}}
  });
  new Chart(document.getElementById('memberChart'), {
    type:'bar', data:{
      labels: d.member_activity.map(m => m.name),
      datasets:[{label:'日报提交数', data:d.member_activity.map(m=>m.count), backgroundColor:'#3b82f6', borderRadius:4}]
    }, options:{indexAxis:'y', responsive:true, plugins:{legend:{display:false}}, scales:{x:{ticks:{color:'#64748b'}}, y:{ticks:{color:'#94a3b8'}}}}
  });
}
loadData();
</script>
</body>
</html>
"""

def load_all_reports(days=7):
    """加载最近N天的所有报告"""
    all_reports = []
    end_date = datetime.now()
    for i in range(days):
        date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        json_path = REPORTS_DIR / f"report_{date_str}.json"
        if json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for analysis in data.get("analyses", []):
                    analysis["_date"] = data.get("date", date_str)
                    all_reports.append(analysis)
    return all_reports

@app.route("/")
def index():
    return render_template_string(TEMPLATE, date_range=datetime.now().strftime("%Y-%m-%d"))

@app.route("/api/dashboard")
def api_dashboard():
    days = 7
    all_reports = load_all_reports(days)

    # 统计数据
    total = len(all_reports)
    sentiment_counts = Counter(r.get("sentiment", "neutral") for r in all_reports)
    risk_counts = Counter(r.get("risk_level", "low") for r in all_reports)

    positive_count = sentiment_counts.get("positive", 0)
    neutral_count = sentiment_counts.get("neutral", 0)
    negative_count = sentiment_counts.get("negative", 0)
    high_risk = risk_counts.get("high", 0)
    medium_risk = risk_counts.get("medium", 0)

    positive_pct = round(positive_count * 100 / total) if total else 0
    neutral_pct = round(neutral_count * 100 / total) if total else 0
    negative_pct = round(negative_count * 100 / total) if total else 0

    # 趋势数据
    trends = []
    end_date = datetime.now()
    for i in range(days):
        date_str = (end_date - timedelta(days=i)).strftime("%Y-%m-%d")
        day_reports = [r for r in all_reports if r.get("_date") == date_str]
        day_sentiments = Counter(r.get("sentiment", "neutral") for r in day_reports)
        day_risks = Counter(r.get("risk_level", "low") for r in day_reports)
        trends.append({
            "date": date_str,
            "positive": day_sentiments.get("positive", 0),
            "neutral": day_sentiments.get("neutral", 0),
            "negative": day_sentiments.get("negative", 0),
            "high_risk": day_risks.get("high", 0),
            "medium_risk": day_risks.get("medium", 0),
        })
    trends.reverse()

    # 成员活跃度
    member_counter = Counter(r.get("reporter", "?") for r in all_reports)
    member_activity = [{"name": n, "count": c} for n, c in member_counter.most_common(10)]

    # 最新一天的详细数据
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_reports = [r for r in all_reports if r.get("_date") == today_str]

    # 告警汇总
    alerts = []
    all_keywords_set = set()
    for r in all_reports:
        if r.get("risk_level") in ("high", "medium"):
            alerts.append({
                "level": r["risk_level"],
                "reporter": r.get("reporter", "?"),
                "content": "; ".join(r.get("risks", [])[:2]) or "检测到风险",
                "date": r.get("_date", ""),
            })
        for kw in r.get("keywords", []):
            all_keywords_set.add(kw)

    # 只返回最新5条告警（高风险优先，同级按日期倒序）
    alerts = sorted(alerts, key=lambda x: (1 if x["level"] == "high" else 0, x["date"]), reverse=True)[:5]

    # 从 app.config 读取关键词分类
    risk_kw = app.config.get("RISK_KEYWORDS", [])
    positive_kw = app.config.get("POSITIVE_KEYWORDS", [])

    return jsonify({
        "days": days,
        "stats": {
            "total_reports": total,
            "positive": positive_pct,
            "positive_count": positive_count,
            "neutral": neutral_pct,
            "neutral_count": neutral_count,
            "negative": negative_pct,
            "negative_count": negative_count,
            "high_risk": high_risk,
            "medium_risk": medium_risk,
        },
        "trends": trends,
        "members": today_reports if today_reports else all_reports[-5:] if all_reports else [],
        "member_activity": member_activity,
        "alerts": alerts,
        "all_keywords": list(all_keywords_set),
        "risk_kw": risk_kw,
        "positive_kw": positive_kw,
    })

def run_dashboard(config):
    """启动看板服务"""
    host = config.get("dashboard", {}).get("host", "0.0.0.0")
    port = config.get("dashboard", {}).get("port", 5000)

    # 将分析关键词配置注入 Flask app，供 API 使用
    analysis = config.get("analysis", {})
    app.config["RISK_KEYWORDS"] = analysis.get("risk_keywords", [])
    app.config["POSITIVE_KEYWORDS"] = analysis.get("positive_keywords", [])

    logger.info("看板已启动: http://localhost:%d", port)
    app.run(host=host, port=port, debug=False)
