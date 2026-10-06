"""Mock RAG engine simulating retrieval of SMC and ICT strategy course rules.

Provides technical analysis rules for Session Liquidity Sweeps, Fair Value Gaps (FVG),
and Order Blocks (OB) based on the asset class of each ticker.
"""

from typing import Dict


def retrieve_course_rules(ticker: str) -> str:
    """Mock retrieval function simulating semantic search from an SMC/ICT trading course.

    Retrieves specific trading rules, entry models, and stop-loss/take-profit constraints
    for technical concepts depending on the asset class.

    Args:
        ticker: The stock/commodity/crypto ticker symbol.

    Returns:
        A string detailing the SMC trading course rules to apply for decision making.
    """
    ticker_upper = ticker.upper()

    strategies: Dict[str, str] = {
        "COMMODITY_SMC": (
            "--- TRADING COURSE RULE: Commodity SMC Session Liquidity Sweep Strategy ---\n"
            "Target Assets: XAUUSD (Gold), XAGUSD (Silver)\n"
            "1. SESSION RANGE: Identify the previous consolidation session range (high and low boundaries).\n"
            "2. LIQUIDITY SWEEP:\n"
            "   - BULLISH SWEEP: If price spikes below the session low to grab sell-side liquidity, and immediately closes back inside the range, look for a LONG entry.\n"
            "   - BEARISH SWEEP: If price spikes above the session high to grab buy-side liquidity, and immediately closes back inside the range, look for a SHORT entry.\n"
            "3. ENTRY MODEL: Wait for a Market Structure Shift (displacement candle creating a Fair Value Gap or Order Block). Enter at the FVG retest or 50% equilibrium of the Order Block.\n"
            "4. STOP LOSS: Place a very tight stop loss just beyond the sweep wick (0.05% - 0.10% distance from entry, e.g. 2.5 - 4.5 points on Gold).\n"
            "5. TAKE PROFIT / RR: Target the opposite session boundary or next major liquidity pool. Maintain a high Risk-to-Reward ratio (minimum 5.0x, aiming for 8.0x - 12.0x as seen in high-conviction trades)."
        ),
        "CRYPTO_SMC": (
            "--- TRADING COURSE RULE: Crypto Liquidity Sweep & Displacement Strategy ---\n"
            "Target Assets: BTCUSD (Bitcoin), ETHUSD (Ethereum)\n"
            "1. LIQUIDITY HUNT: Crypto assets frequently sweep key psychological support/resistance levels and previous daily/weekly highs/lows. Identify if a key level was recently swept.\n"
            "2. MARKET STRUCTURE SHIFT (MSS): Look for a sharp, high-volume displacement candle in the opposite direction. The displacement MUST break the most recent swing high (for long) or swing low (for short) on the 15m/1h chart.\n"
            "3. ENTRY: Identify the Fair Value Gap (FVG) or Order Block (OB) created by the displacement candle. Place a limit entry order at the open of the FVG or top of the OB.\n"
            "4. RISK MANAGEMENT: Place a strict 0.10% - 0.15% stop-loss just below/above the swing candle wick. Never trade crypto without a stop-loss.\n"
            "5. TAKE PROFIT: Target the next major swing high/low. Target a Risk/Reward ratio between 5.0x and 10.0x."
        ),
        "FOREX_SMC": (
            "--- TRADING COURSE RULE: Forex London/NY Session Breakout & Retest Strategy ---\n"
            "Target Assets: GBPUSD (Forex)\n"
            "1. SESSION TIMING: Forex is highly session-dependent. Identify the London session high and low boundaries (08:00 - 12:00 UTC) and the New York session overlap.\n"
            "2. THE SWEEP: Wait for the New York session opening to sweep the London session high or low.\n"
            "3. REVERSAL ENTRY: Look for a character change (CHoCH) on the 15m chart. Enter on the retest of the Fair Value Gap (FVG) left behind by the displacement.\n"
            "4. STOP LOSS: Set a tight stop-loss (0.05% - 0.08% or 6 - 10 pips) just above/below the sweep candle.\n"
            "5. TARGET: Target the opposite London session high/low. Aim for a risk/reward ratio of 6.0x - 12.0x."
        ),
        "DEFAULT_SMC": (
            "--- TRADING COURSE RULE: SMC Liquidity Sweep & Retest (General) ---\n"
            "1. Identify the previous key support/resistance boundaries.\n"
            "2. BUY SIGNAL: Bullish sweep of support. Wait for price to sweep the support level, shift market structure upward on volume, and enter on the retest of the FVG. Stop loss at 0.1% below entry.\n"
            "3. SELL SIGNAL: Bearish sweep of resistance. Wait for price to sweep the resistance level, shift market structure downward, and enter on the retest of the FVG. Stop loss at 0.1% above entry.\n"
            "4. Target a minimum Risk/Reward ratio of 5.0x."
        )
    }

    if ticker_upper in ["XAUUSD", "XAGUSD"]:
        return strategies["COMMODITY_SMC"]
    elif ticker_upper in ["BTCUSD", "ETHUSD"]:
        return strategies["CRYPTO_SMC"]
    elif ticker_upper in ["GBPUSD"]:
        return strategies["FOREX_SMC"]
    else:
        return strategies["DEFAULT_SMC"]
