#!/usr/bin/env python3
"""
OMEGA Content Publisher — Python version
Publishes to Telegraph (free API, no key required)
"""
import json
import os
import sys
from datetime import datetime

import requests

TELEGRAPH_API = "https://api.telegra.ph"
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".telegraph-token.json")


def create_account(short_name, author_name, author_url=""):
    resp = requests.post(f"{TELEGRAPH_API}/createAccount", json={
        "short_name": short_name,
        "author_name": author_name,
        "author_url": author_url
    })
    data = resp.json()
    if not data.get("ok"):
        raise Exception(f"Create account failed: {data}")
    return data["result"]


def create_page(access_token, title, content, author_name="", author_url=""):
    resp = requests.post(f"{TELEGRAPH_API}/createPage", json={
        "access_token": access_token,
        "title": title,
        "author_name": author_name or "OMEGA AI Research",
        "author_url": author_url or "",
        "content": content,
        "return_content": False
    })
    data = resp.json()
    if not data.get("ok"):
        raise Exception(f"Create page failed: {data.get('error', 'unknown')}")
    return data["result"]


def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            saved = json.load(f)
            if saved.get("access_token"):
                print(f"[OMEGA] Using saved Telegraph account: {saved.get('auth_url', '')}")
                return saved

    print("[OMEGA] Creating new Telegraph account...")
    result = create_account("OMEGA_AI_Research", "OMEGA AI Research",
                            "https://t.me/omega_ai_research")
    with open(TOKEN_FILE, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"[OMEGA] New account: {result['auth_url']}")
    return result


def build_content():
    return [
        {"tag": "h1", "children": [
            "Crypto Market Analysis: BTC at Critical Support, ETH Below $2,000 — June 2026 Outlook"]},
        {"tag": "p", "children": [
            f"📅 {datetime.now().strftime('%Y-%m-%d')} | 🔍 OMEGA AI Research | ⏱ 8 min read"]},
        {"tag": "h3", "children": [
            "Institutional outflows, geopolitical tensions, and technical breakdowns create a high-stakes environment for crypto traders"]},

        {"tag": "h2", "children": ["📊 Market Snapshot"]},
        {"tag": "p", "children": [
            "The crypto market enters June 2026 in a precarious position. Bitcoin has corrected over 15% from its April highs above $82,000, while Ethereum fights to stay above the psychological $2,000 level. Institutional ETF outflows continue for a third consecutive week exceeding $1 billion. Here's the complete analysis."]},
        {"tag": "p", "children": [
            "• Bitcoin (BTC): ~$67,300 — consolidating below all major EMAs after 15%+ correction from recent highs\n"
            "• Ethereum (ETH): ~$1,965 — fighting to reclaim $2,000 psychological support\n"
            "• Total Crypto Market Cap: ~$2.3 trillion — down from $2.8T April peak\n"
            "• BTC Dominance: 56.2% — capital rotating to BTC safety during risk-off\n"
            "• Fear & Greed Index: 28 (Fear) — extreme caution among retail traders"]},

        {"tag": "h2", "children": ["🔍 Key Market Drivers"]},
        {"tag": "p", "children": [
            "1. US-Iran Geopolitical Tensions: The Strait of Hormuz blockade keeps oil above $90/barrel, fueling inflation fears and risk-off sentiment across all asset classes."]},
        {"tag": "p", "children": [
            "2. Massive ETF Outflows: Spot BTC ETFs recorded $1.42B in outflows last week — the third consecutive week exceeding $1 billion. BlackRock's IBIT alone lost approximately $1 billion between May 18-22."]},
        {"tag": "p", "children": [
            "3. Strategy (MicroStrategy) BTC Sale: The company sold 32 BTC (~$2.5M), its first sale since 2022. Standard Chartered analysts flagged this as a potential catalyst for ETH outperformance against BTC."]},
        {"tag": "p", "children": [
            "4. Macro Headwinds: World Cup distractions, IPO market pressure, lingering inflation, and AI stock mania are drawing institutional capital away from crypto markets."]},
        {"tag": "p", "children": [
            "5. Leverage Flush: Over $800M in long liquidations across exchanges in the past two weeks, resetting open interest to healthier levels and clearing excessive speculative positioning."]},

        {"tag": "h2", "children": ["📈 Technical Analysis"]},
        {"tag": "h4", "children": ["Bitcoin (BTC)"]},
        {"tag": "p", "children": [
            "BTC is trading at $67,300, down significantly from April highs above $82,000. The price sits below the 50-day, 100-day, and 200-day EMAs — a structurally bearish configuration that demands caution."]},
        {"tag": "p", "children": [
            "Key Support: $65,000–$62,500 zone. This area has historically attracted strong spot buying and represents the last line of defense before a potential drop to $56,000. A daily close below $60,000 would be particularly damaging."]},
        {"tag": "p", "children": [
            "Key Resistance: $75,000–$77,000 must be reclaimed to invalidate the bearish structure and signal a short-term bottom. Until this level is breached, rallies should be viewed with skepticism."]},
        {"tag": "p", "children": [
            "RSI (daily): 37 — approaching oversold territory but not there yet. MACD is negative but the histogram is showing early signs of slowing downward momentum. On-chain data shows long-term holder supply increasing and exchange balances declining — classic accumulation signals despite price weakness."]},

        {"tag": "h4", "children": ["Ethereum (ETH)"]},
        {"tag": "p", "children": [
            "ETH is clinging to $1,965, having broken below the critical $2,000 psychological support. The ETH/BTC ratio continues to decline, now at approximately 0.029, reflecting Bitcoin's dominance during risk-off periods."]},
        {"tag": "p", "children": [
            "Key Support: $1,840–$1,750 zone. A breakdown below $1,750 could accelerate selling toward $1,550 — a level not seen since late 2023. Bulls need to defend this zone aggressively."]},
        {"tag": "p", "children": [
            "Key Resistance: $2,060–$2,170 must be reclaimed for any meaningful recovery. Above that, $2,371 becomes the next upside target."]},
        {"tag": "p", "children": [
            "The silver lining: ETH fundamentals are actually improving. Layer-2 TVL is growing, stablecoin dominance on Ethereum remains unchallenged, RWA tokenization adoption is accelerating, and staking yield (3-5% APR) is attracting institutional treasury allocation. Standard Chartered's Geoffrey Kendrick compares ETH's current setup to Amazon after the dot-com crash — underlying fundamentals improving while price lags."]},

        {"tag": "h2", "children": ["🏦 Institutional Outlook"]},
        {"tag": "p", "children": [
            "• Standard Chartered: Year-end 2026 targets of BTC $100,000 and ETH $4,000. Current levels described as a 'buying zone' by Geoffrey Kendrick, Global Head of Digital Assets Research."]},
        {"tag": "p", "children": [
            "• Peter Brandt (Veteran Trader): Bearish expanding triangle pattern on BTC targets ~$56,000. Invalidation above $75,000 would flip this bearish thesis."]},
        {"tag": "p", "children": [
            "• Tom Lee (Fundstrat): Ultra-bullish on ETH long-term, suggests $250,000 possible if BTC reaches $2-3M. Considered an outlier but historically accurate on major calls."]},
        {"tag": "p", "children": [
            "• Bitcoin Rainbow Chart (June 1, 2026): BTC band range $59,186–$491,731. Current price sits in the 'BUY!' zone according to this logarithmic regression model."]},
        {"tag": "p", "children": [
            "• Polymarket Prediction Odds: BTC above $75,000 by July 1: 34%. ETH above $2,500 by Q3 2026: 28%. Markets are pricing in continued near-term weakness."]},

        {"tag": "h2", "children": ["⚖️ Bull vs Bear Case"]},
        {"tag": "pre", "children": [
            "BULL CASE                          | BEAR CASE\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "BTC oversold at strong support     | $1.42B+ weekly ETF outflows continuing\n"
            "Standard Chartered: 'buying zone'   | US-Iran tensions unresolved, oil > $90\n"
            "ETH fundamentals growing (L2, RWA)  | BTC lost inflation-hedge narrative\n"
            "Strategy expected to buy back BTC   | Death crosses confirmed on daily chart\n"
            "Long-term holders accumulating      | AI stocks drawing institutional capital\n"
            "Leverage flush = healthier market   | World Cup + IPO season = distraction"]},

        {"tag": "h2", "children": ["🎯 Strategy Implications"]},
        {"tag": "p", "children": [
            "1. DCA Strategy: Current fear levels (Fear & Greed at 28) have historically been profitable entry points for dollar-cost averaging into BTC and ETH. Consider weekly buys at these levels."]},
        {"tag": "p", "children": [
            "2. Support Bounce Trade: BTC at $65,000 with a tight stop at $62,000 offers a favorable 3:1 risk/reward if the support zone holds. Target: $73,000–75,000 resistance."]},
        {"tag": "p", "children": [
            "3. ETH Contrarian Play: If Standard Chartered's Amazon analogy proves correct, ETH at sub-$2,000 could represent a generational entry. Position size small (1-2% of portfolio) due to the bearish trend."]},
        {"tag": "p", "children": [
            "4. Risk Management is Paramount: Maximum 1-2% portfolio risk per trade. Use wider stops (5-8%) in the current volatile environment. The market doesn't care about your conviction — it cares about your risk management."]},
        {"tag": "p", "children": [
            "5. Cash is a Position: In a confirmed downtrend with geopolitical uncertainty, holding stablecoins (USDC/USDT) earning 5-8% APY in DeFi protocols is a valid strategy while waiting for trend reversal confirmation."]},

        {"tag": "hr", "children": []},
        {"tag": "p", "children": [
            "⚠️ Disclaimer: This article is for informational purposes only and does not constitute financial, investment, or trading advice. Cryptocurrency and stock trading involves substantial risk of loss and is not suitable for all investors. Past performance does not guarantee future results. Always conduct your own research and consult with a qualified financial advisor before making investment decisions."]},
        {"tag": "p", "children": [
            "📡 Generated by OMEGA AI Research | Autonomous Content Factory | Powered by real-time market data analysis"]},
    ]


def main():
    print("[OMEGA] Content Factory Publisher v2 (Python)")
    print(f"[OMEGA] Time: {datetime.now().isoformat()}")

    account = get_token()
    title = "Crypto Market Analysis: BTC at Critical Support, ETH Below $2,000 — June 2026 Outlook"
    content = build_content()

    print(f"[OMEGA] Publishing: {title}")
    print(f"[OMEGA] Content blocks: {len(content)}")

    result = create_page(account["access_token"], title, content,
                         "OMEGA AI Research", "")

    print(f"\n[OMEGA] ✅ Published successfully!")
    print(f"[OMEGA] 📎 URL: {result['url']}")
    print(f"[OMEGA] 👁 Views: {result.get('views', 0)}")
    print(f"[OMEGA] 📁 Path: {result['path']}")

    # Save publish record
    log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publish-log.jsonl")
    record = {
        "url": result["url"],
        "title": title,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "type": "crypto-analysis",
        "path": result["path"]
    }
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[OMEGA] 📊 Publish log updated: {log_file}")
    return result


if __name__ == "__main__":
    main()
