/**
 * OMEGA Content Publisher — Enhanced Market Intelligence
 * Generates professional multi-section market reports from live signals.
 * Port: 3103 | Managed by PM2
 */
const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');

const PORT = process.env.PORT || 3103;
const BASE = __dirname;
const ARTICLES_DIR = path.join(BASE, 'articles');
const SIGNALS_FILE = path.join(BASE, 'signals-output', 'latest-signals.json');

let publishCount = 0;
let lastPublishTime = null;
let articles = [];
const startTime = new Date().toISOString();
let telegraphAvailable = false;

function loadArticles() {
    try {
        articles = fs.readdirSync(ARTICLES_DIR)
            .filter(f => f.endsWith('.html'))
            .map(f => {
                const stat = fs.statSync(path.join(ARTICLES_DIR, f));
                return { name: f, size: stat.size, mtime: stat.mtime.toISOString(), url: `/articles/${f}` };
            })
            .sort((a, b) => new Date(b.mtime) - new Date(a.mtime));
    } catch (e) { articles = []; }
}

function loadSignals() {
    try { return JSON.parse(fs.readFileSync(SIGNALS_FILE, 'utf8')); }
    catch (e) { return null; }
}

function classifyMarket(avgRsi) {
    if (avgRsi < 20) return { zone: 'EXTREME FEAR', icon: '🔴', desc: 'Market in extreme panic. Historic oversold. Contrarian accumulation zone.', color: '233,69,96' };
    if (avgRsi < 30) return { zone: 'FEAR', icon: '🟠', desc: 'Market fearful. Most assets oversold. Watch for reversal signals.', color: '254,202,87' };
    if (avgRsi < 45) return { zone: 'CAUTIOUS', icon: '🟡', desc: 'Market cautious. Weak bias. Wait for trend confirmation.', color: '254,202,87' };
    if (avgRsi < 55) return { zone: 'NEUTRAL', icon: '⚪', desc: 'Market neutral. No clear direction. Sideways expected.', color: '160,160,180' };
    if (avgRsi < 70) return { zone: 'GREED', icon: '🟢', desc: 'Market optimistic. Uptrend intact. Manage position size.', color: '78,205,196' };
    return { zone: 'EXTREME GREED', icon: '🔥', desc: 'Market euphoric. Elevated correction risk. Consider taking profits.', color: '233,69,96' };
}

function generateReport(signals) {
    const date = new Date().toISOString().split('T')[0];
    const ts = new Date().toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai' });
    const crypto = signals.results.filter(r => r.symbol.includes('USD'));
    const equities = signals.results.filter(r => ['NVDA','TSLA','AAPL','MSFT','GOOGL','SPY','QQQ'].includes(r.symbol));
    const commodities = signals.results.filter(r => ['GLD','SLV','BNB-USD'].includes(r.symbol));
    const buys = signals.results.filter(r => r.action === 'BUY');
    const sells = signals.results.filter(r => r.action === 'SELL');
    const avgCryptoRsi = crypto.length > 0 ? crypto.reduce((s,r) => s + r.indicators.rsi, 0) / crypto.length : 50;
    const mkt = classifyMarket(avgCryptoRsi);
    const topDecliners = [...signals.results].sort((a,b) => a.price_change_30d_pct - b.price_change_30d_pct).slice(0, 3);
    const topGainers = [...signals.results].sort((a,b) => b.price_change_30d_pct - a.price_change_30d_pct).slice(0, 3);

    const signalRow = (r) => {
        const aIcon = r.action === 'BUY' ? '🟢' : (r.action === 'SELL' ? '🔴' : '🟡');
        const chg = r.price_change_30d_pct;
        const chgColor = chg > 0 ? '#4ecdc4' : (chg < -15 ? '#e94560' : '#feca57');
        const rsiColor = r.indicators.rsi < 20 ? '#e94560' : (r.indicators.rsi < 30 ? '#feca57' : '#aaa');
        const sigText = (r.signals || []).slice(0,2).map(s => `<span style="color:#777;font-size:.8em">${s}</span>`).join('<br>');
        return `<tr>
            <td>${aIcon} <b>${r.symbol}</b></td>
            <td style="text-align:right;font-family:monospace">$${r.current_price.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2})}</td>
            <td style="text-align:right;color:${rsiColor};font-weight:700">${r.indicators.rsi.toFixed(1)}</td>
            <td style="text-align:right;color:${chgColor}">${chg>0?'+':''}${chg.toFixed(1)}%</td>
            <td style="text-align:center;font-weight:700;color:${r.action==='BUY'?'#4ecdc4':r.action==='SELL'?'#e94560':'#feca57'}">${r.action}</td>
            <td>${sigText}</td></tr>`;
    };

    return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>OMEGA Market Intelligence — ${date}</title>
<style>
body{font-family:system-ui;background:#0a0a1a;color:#e0e0f0;max-width:960px;margin:0 auto;padding:20px;line-height:1.6}
.header{text-align:center;padding:30px 0 20px;border-bottom:2px solid #1a1a4a;margin-bottom:24px}
.header h1{background:linear-gradient(135deg,#7c5cfc,#4ecdc4);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-size:2rem;margin:0}
.header .ts{color:#888;font-size:.85rem;margin-top:4px}
.zone-badge{display:inline-block;padding:8px 24px;border-radius:20px;font-weight:700;font-size:1.05rem;margin:12px 0}
.stats-grid{display:flex;gap:14px;margin:20px 0;flex-wrap:wrap;justify-content:center}
.stat{background:#0d0d25;border:1px solid #1a1a3a;border-radius:10px;padding:14px 22px;text-align:center;min-width:110px}
.stat .num{font-size:1.7rem;font-weight:900;color:#4ecdc4}.stat .label{font-size:.75rem;color:#888;margin-top:2px}
.section{margin:28px 0}.section h2{color:#7c5cfc;font-size:1.2rem;border-bottom:1px solid #1a1a3a;padding-bottom:8px;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:.88rem}
th{background:#0d0d25;color:#888;text-align:left;padding:10px 8px;border-bottom:2px solid #1a1a4a;font-weight:600}
td{padding:9px 8px;border-bottom:1px solid #12122a}
tr:hover{background:rgba(124,92,252,0.03)}
.insight{background:rgba(78,205,196,0.04);border:1px solid rgba(78,205,196,0.12);border-radius:10px;padding:14px 18px;margin:12px 0}
.insight h3{color:#4ecdc4;font-size:.95rem;margin:0 0 8px}
.insight p{color:#aaa;font-size:.85rem;margin:4px 0}
.footer{text-align:center;color:#555;font-size:.75rem;margin-top:36px;padding-top:16px;border-top:1px solid #1a1a3a}.footer a{color:#7c5cfc}
</style></head><body>
<div class="header">
  <h1>OMEGA Market Intelligence</h1>
  <div class="ts">${date} · ${ts} CST · ${signals.symbols_analyzed} Symbols</div>
  <div class="zone-badge" style="background:rgba(${mkt.color},0.1);color:${mkt.zone.includes('FEAR')?'#e94560':'#4ecdc4'}">${mkt.icon} ${mkt.zone}</div>
  <p style="color:#999;max-width:600px;margin:10px auto;font-size:.9rem">${mkt.desc}</p>
</div>
<div class="stats-grid">
  <div class="stat"><div class="num">${signals.symbols_analyzed}</div><div class="label">Symbols</div></div>
  <div class="stat"><div class="num" style="color:#4ecdc4">${buys.length}</div><div class="label">BUY</div></div>
  <div class="stat"><div class="num" style="color:#e94560">${sells.length}</div><div class="label">SELL</div></div>
  <div class="stat"><div class="num" style="color:#feca57">${signals.results.length - buys.length - sells.length}</div><div class="label">HOLD</div></div>
  <div class="stat"><div class="num" style="color:${avgCryptoRsi<30?'#e94560':'#4ecdc4'}">${avgCryptoRsi.toFixed(1)}</div><div class="label">Crypto RSI</div></div>
</div>
<div class="section"><h2>🔴 Crypto Markets</h2><table><tr><th>Symbol</th><th>Price</th><th>RSI</th><th>30d</th><th>Signal</th><th>Indicators</th></tr>${crypto.map(signalRow).join('')}</table></div>
<div class="section"><h2>📈 Equity Markets</h2><table><tr><th>Symbol</th><th>Price</th><th>RSI</th><th>30d</th><th>Signal</th><th>Indicators</th></tr>${equities.map(signalRow).join('')}</table></div>
<div class="section"><h2>🏆 Commodities</h2><table><tr><th>Symbol</th><th>Price</th><th>RSI</th><th>30d</th><th>Signal</th><th>Indicators</th></tr>${commodities.map(signalRow).join('')}</table></div>
<div class="section"><h2>💡 AI Insights</h2>
  <div class="insight"><h3>📉 Biggest Decliners (30d)</h3>${topDecliners.map(r => `<p><b>${r.symbol}</b>: ${r.price_change_30d_pct.toFixed(1)}% — RSI ${r.indicators.rsi.toFixed(1)} | ${r.signals?.[0]||''}</p>`).join('')}</div>
  <div class="insight"><h3>📊 Top Performers (30d)</h3>${topGainers.map(r => `<p><b>${r.symbol}</b>: +${r.price_change_30d_pct.toFixed(1)}% — RSI ${r.indicators.rsi.toFixed(1)} | ${r.signals?.[0]||''}</p>`).join('')}</div>
  <div class="insight"><h3>🎯 Strategy</h3><p>${avgCryptoRsi<20?'🔴 <b>Extreme Oversold:</b> Crypto RSI at historic lows. Consider DCA into quality assets. Set stop-losses. <i>Not financial advice.</i>':avgCryptoRsi<30?'🟠 <b>Oversold:</b> Watch for RSI divergence + MACD cross for entry. Maintain cash reserves.':'⚪ <b>Neutral:</b> No extreme signals. Standard position sizing.'}</p></div>
</div>
<div class="footer">
  <p>Generated by <b>OMEGA Content Service</b> · Autonomous 24/7 · ${new Date().toISOString()}</p>
  <p>OMEGA Empire · 910 Agents · 29 Sectors · <a href="https://zijing271.github.io">zijing271.github.io</a></p>
</div></body></html>`;
}

async function runPublishCycle() {
    const signals = loadSignals();
    if (!signals) return { status: 'SKIPPED', reason: 'No signals data' };
    const date = new Date().toISOString().split('T')[0];
    const title = `Market-Update-${date}`;
    const content = generateReport(signals);

    if (telegraphAvailable) {
        try {
            const result = await publishArticle(title, content);
            publishCount++; lastPublishTime = new Date().toISOString();
            return { status: 'PUBLISHED', url: result.url, title };
        } catch (e) {
            const fname = `${date}-market-update.html`;
            fs.writeFileSync(path.join(ARTICLES_DIR, fname), content);
            publishCount++; lastPublishTime = new Date().toISOString();
            return { status: 'PUBLISHED_LOCAL', file: fname };
        }
    } else {
        const fname = `${date}-market-update.html`;
        fs.writeFileSync(path.join(ARTICLES_DIR, fname), content);
        publishCount++; lastPublishTime = new Date().toISOString();
        return { status: 'PUBLISHED_LOCAL', file: fname };
    }
}

const server = http.createServer((req, res) => {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Content-Type', 'application/json');

    if (url.pathname === '/' || url.pathname === '/api/health') {
        loadArticles();
        const sigs = loadSignals();
        res.end(JSON.stringify({ service:'OMEGA Content Publisher', status:'RUNNING', port:PORT, uptime_seconds:(new Date()-new Date(startTime))/1000, publish_count:publishCount, last_publish:lastPublishTime, telegraph_available:telegraphAvailable, articles_count:articles.length, signals_available:!!sigs }, null, 2));
    } else if (url.pathname === '/api/report') {
        const sigs = loadSignals();
        if (!sigs) { res.statusCode = 503; res.end(JSON.stringify({error:'Signal data unavailable'})); return; }
        res.setHeader('Content-Type', 'text/html; charset=utf-8');
        res.end(generateReport(sigs));
    } else if (url.pathname === '/api/articles') {
        loadArticles();
        res.end(JSON.stringify({ count: articles.length, articles }, null, 2));
    } else if (url.pathname === '/api/publish') {
        runPublishCycle().then(r => res.end(JSON.stringify(r,null,2))).catch(e => { res.statusCode=500; res.end(JSON.stringify({error:e.message})); });
    } else if (url.pathname.startsWith('/articles/')) {
        const fname = path.basename(url.pathname);
        const fpath = path.join(ARTICLES_DIR, fname);
        if (fs.existsSync(fpath)) { res.setHeader('Content-Type', 'text/html; charset=utf-8'); res.end(fs.readFileSync(fpath,'utf8')); }
        else { res.statusCode = 404; res.end('Not found'); }
    } else {
        res.statusCode = 404; res.end(JSON.stringify({error:'Not found', endpoints:['/api/health','/api/report','/api/articles','/api/publish','/articles/:name']}));
    }
});

function publishArticle(title, htmlContent) {
    return new Promise((resolve, reject) => {
        const params = new URLSearchParams();
        params.append('title', title); params.append('content', htmlContent); params.append('access_token', 'anonymous');
        const body = params.toString();
        const req = https.request({ hostname:'api.telegra.ph', path:'/createPage', method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded','Content-Length':body.length}, timeout:8000 }, (res) => {
            let d = ''; res.on('data', c => d += c);
            res.on('end', () => { try { const j = JSON.parse(d); if (j.ok) resolve(j.result); else reject(new Error(j.error||'API error')); } catch(e) { reject(e); } });
        });
        req.on('error', reject); req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
        req.write(body); req.end();
    });
}

function checkTelegraph() {
    return new Promise((resolve) => {
        const req = https.get({ hostname:'api.telegra.ph', path:'/getPage?path=OmegaTest-2026-06-06&return_content=false', timeout:5000 }, (res) => {
            let d = ''; res.on('data', c => d += c);
            res.on('end', () => { try { resolve(JSON.parse(d).ok||false); } catch(e) { resolve(false); } });
        });
        req.on('error', () => resolve(false)); req.on('timeout', () => { req.destroy(); resolve(false); });
    });
}

(async () => {
    telegraphAvailable = await checkTelegraph();
    console.log(`[OMEGA-Content] Telegraph: ${telegraphAvailable?'AVAILABLE':'UNAVAILABLE (local fallback)'}`);
    loadArticles();
    console.log(`[OMEGA-Content] ${articles.length} articles loaded`);
    server.listen(PORT, () => { console.log(`[OMEGA-Content] Enhanced service running on port ${PORT}`); });
    setInterval(async () => {
        try { const r = await runPublishCycle(); console.log(`[OMEGA-Content] Publish: ${JSON.stringify(r)}`); }
        catch (e) { console.error(`[OMEGA-Content] Error: ${e.message}`); }
    }, 3 * 3600 * 1000);
})();
