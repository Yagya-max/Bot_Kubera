"""Market data engine using yfinance to fetch and summarize OHLC data.

Downloads recent hourly data, calculates technical indicators like SMA, and builds
structured summaries including Smart Money Concepts (SMC) structures for LLM prompt context.
"""

import pandas as pd
import yfinance as yf

# Mapping display tickers to Yahoo Finance tickers
TICKER_MAPPING = {
    "XAUUSD": "GC=F",      # Gold Futures
    "XAGUSD": "SI=F",      # Silver Futures
    "BTCUSD": "BTC-USD",    # Bitcoin Spot
    "ETHUSD": "ETH-USD",    # Ethereum Spot
    "GBPUSD": "GBPUSD=X"    # GBP/USD Spot Forex
}

def resolve_ticker(ticker: str) -> str:
    """Maps the display ticker to the corresponding Yahoo Finance ticker."""
    return TICKER_MAPPING.get(ticker.upper(), ticker.upper())

def get_smc_indicators(df: pd.DataFrame) -> dict:
    """Calculates Smart Money Concepts (SMC) indicators on historical data.
    
    Identifies Session Highs/Lows, Liquidity Sweeps, Fair Value Gaps (FVG),
    and Order Blocks (OB).
    """
    if len(df) < 30:
        return {}
    
    # Standardize column index names (handle MultiIndex or uppercase/lowercase issues)
    df_clean = df.copy()
    if isinstance(df_clean.columns, pd.MultiIndex):
        df_clean.columns = df_clean.columns.get_level_values(0)
    
    # We define a lookback session (candles -48 to -12, representing previous trading day/session)
    session_data = df_clean.iloc[-48:-12]
    if session_data.empty:
        return {}
        
    session_high = float(session_data["High"].max())
    session_low = float(session_data["Low"].min())
    
    # Check for sweeps in the remaining candles (-12 to -1)
    recent_data = df_clean.iloc[-12:]
    
    bearish_sweep = False
    bullish_sweep = False
    sweep_high_price = 0.0
    sweep_low_price = 0.0
    
    for idx, row in recent_data.iterrows():
        # Bearish sweep: Price spiked above session high, but closed below/at it
        if float(row["High"]) > session_high and float(row["Close"]) <= session_high:
            bearish_sweep = True
            sweep_high_price = float(row["High"])
        # Bullish sweep: Price spiked below session low, but closed above/at it
        if float(row["Low"]) < session_low and float(row["Close"]) >= session_low:
            bullish_sweep = True
            sweep_low_price = float(row["Low"])
            
    # Find Fair Value Gaps (FVG) in the last 20 candles
    fvgs = []
    for i in range(len(df_clean) - 20, len(df_clean) - 1):
        if i < 2:
            continue
        # Bullish FVG: Low of candle i > High of candle i-2 (Green displacement candle i-1)
        low_i = float(df_clean.iloc[i]["Low"])
        high_i2 = float(df_clean.iloc[i-2]["High"])
        close_i1 = float(df_clean.iloc[i-1]["Close"])
        open_i1 = float(df_clean.iloc[i-1]["Open"])
        
        if low_i > high_i2 and close_i1 > open_i1:
            fvgs.append({
                "type": "bullish",
                "top": low_i,
                "bottom": high_i2,
                "time": df_clean.index[i-1].strftime("%Y-%m-%d %H:%M:%S")
            })
        # Bearish FVG: High of candle i < Low of candle i-2 (Red displacement candle i-1)
        high_i = float(df_clean.iloc[i]["High"])
        low_i2 = float(df_clean.iloc[i-2]["Low"])
        close_i1 = float(df_clean.iloc[i-1]["Close"])
        open_i1 = float(df_clean.iloc[i-1]["Open"])
        
        if high_i < low_i2 and close_i1 < open_i1:
            fvgs.append({
                "type": "bearish",
                "top": low_i2,
                "bottom": high_i,
                "time": df_clean.index[i-1].strftime("%Y-%m-%d %H:%M:%S")
            })
            
    # Find Order Blocks (OB) in the last 25 candles
    order_blocks = []
    body_sizes = (df_clean["Close"] - df_clean["Open"]).abs()
    mean_body = float(body_sizes.mean())
    
    for i in range(len(df_clean) - 25, len(df_clean) - 3):
        # Identify sharp displacement after candle i
        close_diff = float(df_clean.iloc[i+2]["Close"]) - float(df_clean.iloc[i+1]["Open"])
        
        # Bullish OB: down candle followed by strong up candles
        if close_diff > 1.8 * mean_body and float(df_clean.iloc[i]["Close"]) < float(df_clean.iloc[i]["Open"]):
            order_blocks.append({
                "type": "bullish",
                "top": float(df_clean.iloc[i]["High"]),
                "bottom": float(df_clean.iloc[i]["Low"]),
                "time": df_clean.index[i].strftime("%Y-%m-%d %H:%M:%S")
            })
        # Bearish OB: up candle followed by strong down candles
        elif close_diff < -1.8 * mean_body and float(df_clean.iloc[i]["Close"]) > float(df_clean.iloc[i]["Open"]):
            order_blocks.append({
                "type": "bearish",
                "top": float(df_clean.iloc[i]["High"]),
                "bottom": float(df_clean.iloc[i]["Low"]),
                "time": df_clean.index[i].strftime("%Y-%m-%d %H:%M:%S")
            })
            
    return {
        "session_high": session_high,
        "session_low": session_low,
        "bearish_sweep": bearish_sweep,
        "bullish_sweep": bullish_sweep,
        "sweep_high_price": sweep_high_price,
        "sweep_low_price": sweep_low_price,
        "fvgs": fvgs,
        "order_blocks": order_blocks
    }

def get_market_summary(ticker: str) -> str:
    """Downloads the last 5 days of 1-hour candle data for a given ticker,
    computes a 20-period Simple Moving Average (SMA) and SMC indicators,
    and formats them into a structured text summary.
    """
    try:
        resolved = resolve_ticker(ticker)
        # Download historical 1-hour candle data for the last 5 days
        df: pd.DataFrame = yf.download(
            tickers=resolved, period="5d", interval="1h", progress=False
        )

        if df.empty:
            return f"Error: No market data fetched for ticker {ticker} (resolved: {resolved})."

        # Clean up any MultiIndex columns
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Ensure we have the required columns
        required_cols = ["Close", "Volume", "High", "Low", "Open"]
        for col in required_cols:
            if col not in df.columns:
                return f"Error: Required column '{col}' missing from data for {ticker}."

        # Compute SMA
        df["SMA_20"] = df["Close"].rolling(window=20).mean()

        # Extract the latest 3 rows
        latest_rows = df.tail(3)

        # Format the latest 3 rows into a highly structured text summary
        summary_lines = [
            f"=== Market Summary for Ticker: {ticker} (Yahoo: {resolved}) ===",
            "Latest 1-Hour Candles (ordered newest last):",
        ]

        for timestamp, row in latest_rows.iterrows():
            close_val = float(row["Close"]) if not pd.isna(row["Close"]) else 0.0
            vol_val = int(row["Volume"]) if not pd.isna(row["Volume"]) else 0
            sma_val = float(row["SMA_20"]) if not pd.isna(row["SMA_20"]) else 0.0

            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z")
            sma_str = f"{sma_val:.2f}" if sma_val > 0.0 else "N/A (Insufficient history)"

            summary_lines.append(
                f"- Time: {time_str} | Close: {close_val:.2f} | Volume: {vol_val:,} | SMA(20): {sma_str}"
            )

        # Add brief general metadata
        current_price = float(df["Close"].iloc[-1])
        summary_lines.append(f"Current Price: {current_price:.2f}")

        # Compute SMC metrics
        smc = get_smc_indicators(df)
        summary_lines.append("\n=== Smart Money Concepts (SMC) Structure ===")
        if smc:
            summary_lines.append(f"Previous Session High: {smc['session_high']:.2f}")
            summary_lines.append(f"Previous Session Low: {smc['session_low']:.2f}")
            
            sweep_status = "None"
            if smc['bearish_sweep'] and smc['bullish_sweep']:
                sweep_status = "Double Sweep (Session High & Low swept)"
            elif smc['bearish_sweep']:
                sweep_status = "Bearish Sweep of Session High (Potential Short Entry)"
            elif smc['bullish_sweep']:
                sweep_status = "Bullish Sweep of Session Low (Potential Long Entry)"
            summary_lines.append(f"Liquidity Sweep Status: {sweep_status}")
            
            if smc['fvgs']:
                summary_lines.append("Detected Fair Value Gaps (FVG):")
                for fvg in smc['fvgs'][-2:]:  # Show latest 2
                    summary_lines.append(f"- {fvg['type'].upper()} FVG between {fvg['bottom']:.2f} and {fvg['top']:.2f} (Time: {fvg['time']})")
            else:
                summary_lines.append("No active Fair Value Gaps detected.")
                
            if smc['order_blocks']:
                summary_lines.append("Detected Order Blocks (OB):")
                for ob in smc['order_blocks'][-2:]:  # Show latest 2
                    summary_lines.append(f"- {ob['type'].upper()} Order Block at range {ob['bottom']:.2f} - {ob['top']:.2f} (Time: {ob['time']})")
            else:
                summary_lines.append("No clear Order Blocks detected.")
        else:
            summary_lines.append("Could not calculate SMC indicators (insufficient history).")

        return "\n".join(summary_lines)

    except Exception as e:
        return f"Error: Exception occurred while retrieving data for {ticker}: {str(e)}"
