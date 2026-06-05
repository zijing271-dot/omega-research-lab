#!/usr/bin/env python3
"""
OMEGA Trading Signal Generator
Uses free data (yfinance) to generate real actionable trading signals.
Paper trading ready. Live trading needs exchange API keys.

Revenue path: Signals API → $49-499/mo subscriptions
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os

# === Configuration ===
SYMBOLS = [
    "BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD",
    "AAPL", "NVDA", "MSFT", "GOOGL", "TSLA",
    "QQQ", "SPY", "GLD", "SLV"
]

TIMEFRAMES = {
    "1mo": "1d",   # 1 month, daily candles
    "3mo": "1d",   # 3 months
    "6mo": "1d",   # 6 months
}

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signals-output")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def calculate_rsi(series, period=14):
    """Relative Strength Index"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_macd(series, fast=12, slow=26, signal=9):
    """MACD - Moving Average Convergence Divergence"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(series, period=20, std_dev=2):
    """Bollinger Bands"""
    sma = series.rolling(window=period).mean()
    std = series.rolling(window=period).std()
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    return upper, sma, lower


def calculate_ema_cross(series, fast=50, slow=200):
    """Golden/Death Cross detection"""
    ema_fast = series.ewm(span=fast, adjust=False).mean()
    ema_slow = series.ewm(span=slow, adjust=False).mean()
    return ema_fast, ema_slow


def analyze_symbol(symbol):
    """Generate comprehensive analysis for a symbol"""
    print(f"  [{symbol}] Fetching data...")

    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="6mo")

        if hist.empty:
            print(f"  [{symbol}] ⚠️ No data found")
            return None

        close = hist['Close']
        volume = hist['Volume']
        high = hist['High']
        low = hist['Low']

        current_price = close.iloc[-1]
        prev_close = close.iloc[-2] if len(close) > 1 else current_price
        price_change_pct = ((current_price - close.iloc[-22]) / close.iloc[-22]) * 100 if len(close) >= 22 else 0
        volume_avg = volume.iloc[-20:].mean() if len(volume) >= 20 else volume.mean()

        # RSI
        rsi = calculate_rsi(close)
        rsi_current = rsi.iloc[-1] if not rsi.empty else 50

        # MACD
        macd_line, signal_line, histogram = calculate_macd(close)
        macd_current = macd_line.iloc[-1] if not macd_line.empty else 0
        signal_current = signal_line.iloc[-1] if not signal_line.empty else 0
        hist_current = histogram.iloc[-1] if not histogram.empty else 0
        hist_prev = histogram.iloc[-2] if len(histogram) > 1 else 0

        # Bollinger Bands
        bb_upper, bb_mid, bb_lower = calculate_bollinger_bands(close)
        bb_upper_current = bb_upper.iloc[-1]
        bb_lower_current = bb_lower.iloc[-1]
        bb_mid_current = bb_mid.iloc[-1]

        # EMA Cross
        ema_50, ema_200 = calculate_ema_cross(close)
        ema_50_current = ema_50.iloc[-1] if not ema_50.empty else current_price
        ema_200_current = ema_200.iloc[-1] if not ema_200.empty else current_price

        # Volume analysis
        current_volume = volume.iloc[-1]
        volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1

        # Support/Resistance (simple: recent swing highs/lows)
        recent_high = high.iloc[-60:].max() if len(high) >= 60 else high.max()
        recent_low = low.iloc[-60:].min() if len(low) >= 60 else low.min()

        # === SIGNAL LOGIC ===

        signals = []
        score = 0  # -100 to +100

        # RSI signals
        if rsi_current < 30:
            signals.append(f"RSI OVERSOLD ({rsi_current:.1f})")
            score += 25
        elif rsi_current < 40:
            signals.append(f"RSI near oversold ({rsi_current:.1f})")
            score += 10
        elif rsi_current > 70:
            signals.append(f"RSI OVERBOUGHT ({rsi_current:.1f})")
            score -= 25
        elif rsi_current > 60:
            signals.append(f"RSI near overbought ({rsi_current:.1f})")
            score -= 10

        # MACD signals
        if hist_current > 0 and hist_prev <= 0:
            signals.append("MACD BULLISH CROSSOVER")
            score += 20
        elif hist_current < 0 and hist_prev >= 0:
            signals.append("MACD BEARISH CROSSOVER")
            score -= 20
        elif hist_current > hist_prev:
            signals.append("MACD bullish momentum increasing")
            score += 5
        elif hist_current < hist_prev:
            signals.append("MACD bearish momentum increasing")
            score -= 5

        # EMA Cross (Golden/Death Cross)
        if ema_50_current > ema_200_current:
            if (current_price / ema_200_current - 1) * 100 < 5:
                signals.append("GOLDEN CROSS zone — bullish structure")
                score += 15
        else:
            if prev_close > close.iloc[-2]:
                signals.append("DEATH CROSS zone — bearish structure")
                score -= 15

        # Bollinger Band signals
        if current_price <= bb_lower_current:
            signals.append(f"Price AT LOWER BB — potential bounce")
            score += 15
        elif current_price >= bb_upper_current:
            signals.append(f"Price AT UPPER BB — potential reversal")
            score -= 15
        if current_price < bb_mid_current:
            signals.append("Price below BB midline — bearish bias")
            score -= 5
        else:
            signals.append("Price above BB midline — bullish bias")
            score += 5

        # Volume signals
        if volume_ratio > 1.5:
            signals.append(f"High volume ({volume_ratio:.1f}x avg) — conviction move")
            score += 5 if current_price > prev_close else -5

        # Price relative to support/resistance
        dist_to_support = (current_price - recent_low) / current_price * 100
        dist_to_resistance = (recent_high - current_price) / current_price * 100

        # Determine overall signal
        if score >= 40:
            action = "🟢 STRONG BUY"
        elif score >= 15:
            action = "🟡 BUY"
        elif score >= -15:
            action = "⚪ HOLD/NEUTRAL"
        elif score >= -40:
            action = "🟠 SELL"
        else:
            action = "🔴 STRONG SELL"

        result = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "price_change_30d_pct": round(price_change_pct, 2),
            "action": action,
            "score": score,
            "signals": signals[:6],
            "indicators": {
                "rsi": round(rsi_current, 1),
                "macd": round(macd_current, 4),
                "macd_signal": round(signal_current, 4),
                "macd_histogram": round(hist_current, 4),
                "bb_upper": round(bb_upper_current, 2) if pd.notna(bb_upper_current) else None,
                "bb_lower": round(bb_lower_current, 2) if pd.notna(bb_lower_current) else None,
                "bb_mid": round(bb_mid_current, 2) if pd.notna(bb_mid_current) else None,
                "ema_50": round(ema_50_current, 2),
                "ema_200": round(ema_200_current, 2),
                "volume_ratio": round(volume_ratio, 2),
            },
            "levels": {
                "support": round(recent_low, 2),
                "resistance": round(recent_high, 2),
                "dist_to_support_pct": round(dist_to_support, 2),
                "dist_to_resistance_pct": round(dist_to_resistance, 2),
            }
        }

        print(f"  [{symbol}] {action} (Score: {score}) | Price: ${current_price:.2f} | RSI: {rsi_current:.1f}")
        return result

    except Exception as e:
        print(f"  [{symbol}] ❌ Error: {e}")
        return None


def main():
    print("=" * 70)
    print("  OMEGA Trading Signal Generator")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Analyzing {len(SYMBOLS)} symbols")
    print("=" * 70)

    results = []
    for symbol in SYMBOLS:
        result = analyze_symbol(symbol)
        if result:
            results.append(result)

    # Sort by score (best to worst)
    results.sort(key=lambda x: x['score'], reverse=True)

    # Summary table
    print("\n" + "=" * 70)
    print("  📊 SIGNAL SUMMARY (sorted by conviction)")
    print("=" * 70)
    print(f"{'Symbol':<12} {'Price':>10} {'30d%':>8} {'Action':<22} {'Score':>6} {'RSI':>6}")
    print("-" * 70)

    for r in results:
        print(f"{r['symbol']:<12} ${r['current_price']:>9.2f} {r['price_change_30d_pct']:>7.1f}% {r['action']:<22} {r['score']:>5} {r['indicators']['rsi']:>5.0f}")

    # Top picks
    print("\n" + "=" * 70)
    print("  🎯 TOP TRADING IDEAS")
    print("=" * 70)

    buys = [r for r in results if 'BUY' in r['action']]
    sells = [r for r in results if 'SELL' in r['action']]

    if buys:
        print("\n  🟢 BUY Candidates:")
        for r in buys[:5]:
            print(f"    {r['symbol']}: ${r['current_price']:.2f} | {', '.join(r['signals'][:3])}")

    if sells:
        print("\n  🔴 SELL/AVOID Candidates:")
        for r in sells[:5]:
            print(f"    {r['symbol']}: ${r['current_price']:.2f} | {', '.join(r['signals'][:3])}")

    # Save results
    report = {
        "generated_at": datetime.now().isoformat(),
        "symbols_analyzed": len(results),
        "results": results,
        "market_summary": {
            "buy_count": len(buys),
            "sell_count": len(sells),
            "neutral_count": len([r for r in results if 'HOLD' in r['action']]),
            "avg_score": round(np.mean([r['score'] for r in results]), 1),
        }
    }

    report_file = os.path.join(OUTPUT_DIR, f"signals-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    # Latest summary
    with open(os.path.join(OUTPUT_DIR, "latest-signals.json"), 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n  📁 Full report saved: {report_file}")
    print(f"  📁 Latest summary: {os.path.join(OUTPUT_DIR, 'latest-signals.json')}")

    return report


if __name__ == "__main__":
    main()
