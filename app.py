"""Flask web server for the interactive AI Trading Bot Dashboard.

Serves the front-end dashboard UI and provides APIs to interact with the
trading bot pipeline, parse logs, download chart data, and modify settings.
"""

import os
import json
import re
from flask import Flask, jsonify, render_template, request
import config
from data_engine import get_market_summary, resolve_ticker, get_smc_indicators
from rag_engine import retrieve_course_rules
from llm_client import generate_trading_decision
from execution_engine import process_signal

app = Flask(__name__, template_folder="templates")

# Resolve templates folder relative to file location
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app.template_folder = TEMPLATES_DIR

def parse_paper_trades_log():
    """Parses paper_trades.log into a list of dictionaries."""
    if not os.path.exists(config.LOG_FILE_PATH):
        return []
    
    trades = []
    try:
        with open(config.LOG_FILE_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line.startswith("["):
                    continue
                
                try:
                    timestamp_part, details_part = line.split("] ", 1)
                    timestamp = timestamp_part.lstrip("[")
                    
                    parts = details_part.split(" | ")
                    trade = {"timestamp": timestamp}
                    for part in parts:
                        if ":" in part:
                            k, v = part.split(":", 1)
                            key = k.strip().lower()
                            val = v.strip()
                            
                            # Normalize key names and strip currency symbols
                            if key == "asset":
                                key = "ticker"
                            elif key == "risk-reward":
                                key = "risk_reward"
                            elif key == "stop-loss":
                                key = "stop_loss"
                            elif key == "price":
                                val = val.replace("$", "")
                                
                            trade[key] = val
                    
                    trades.append(trade)
                except Exception as ex:
                    print(f"[WARNING] Skipping log line due to format mismatch: {line}. Error: {str(ex)}")
                    continue
        return trades[::-1]  # Return newest trades first
    except Exception as e:
        print(f"[ERROR] Failed to parse log: {str(e)}")
        return []

@app.route("/")
def index():
    """Serves the dashboard front-end page."""
    return render_template("index.html")

@app.route("/api/watchlist", methods=["GET"])
def get_watchlist():
    """Fetches real-time watchlist commodities, forex, and crypto prices using yfinance."""
    import yfinance as yf
    
    data = []
    for ticker in config.WATCH_LIST:
        try:
            resolved = resolve_ticker(ticker)
            ticker_data = yf.Ticker(resolved)
            
            # Fetch 2 days of history to calculate daily % change
            history = ticker_data.history(period="2d")
            
            if not history.empty and len(history) >= 2:
                current_price = float(history["Close"].iloc[-1])
                prev_price = float(history["Close"].iloc[-2])
                pct_change = ((current_price - prev_price) / prev_price) * 100
            elif not history.empty:
                current_price = float(history["Close"].iloc[-1])
                pct_change = 0.0
            else:
                current_price = 0.0
                pct_change = 0.0
                
            data.append({
                "ticker": ticker,
                "price": round(current_price, 2),
                "change": round(pct_change, 2)
            })
        except Exception as e:
            data.append({
                "ticker": ticker,
                "price": 0.0,
                "change": 0.0,
                "error": str(e)
            })
            
    return jsonify(data)

@app.route("/api/chart/<ticker>", methods=["GET"])
def get_chart_data(ticker):
    """Downloads last 5 days of 1h candle data for charting and computes SMC structures."""
    import yfinance as yf
    import pandas as pd
    
    try:
        resolved = resolve_ticker(ticker)
        df = yf.download(tickers=resolved, period="5d", interval="1h", progress=False)
        if df.empty:
            return jsonify({"error": f"No data found for ticker {ticker} ({resolved})"}), 404
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Calculate 20 SMA
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df = df.dropna(subset=["Close"])
        
        dates = [t.strftime("%m-%d %H:%M") for t in df.index]
        timestamps = [int(t.timestamp()) for t in df.index]
        opens = [round(float(o), 2) for o in df["Open"].values]
        highs = [round(float(h), 2) for h in df["High"].values]
        lows = [round(float(l), 2) for l in df["Low"].values]
        closes = [round(float(c), 2) for c in df["Close"].values]
        sma = [round(float(s), 2) if not pd.isna(s) else None for s in df["SMA_20"].values]
        volumes = [int(v) for v in df["Volume"].values]
        
        # Calculate SMC structures (session ranges, sweeps, FVGs, Order Blocks)
        smc = get_smc_indicators(df)
        
        # Check if there is an active/recent trade in the log for this asset to show on chart
        trades = parse_paper_trades_log()
        active_trade = None
        for t in trades:
            if t.get("ticker", "").upper() == ticker.upper() and t.get("action", "HOLD") in ["BUY", "SELL"]:
                # Grab the latest non-HOLD trade
                active_trade = {
                    "action": t.get("action"),
                    "price": float(t.get("price", "0").replace("$", "")),
                    "stop_loss": t.get("stop_loss"),
                    "target": t.get("target"),
                    "risk_reward": float(t.get("risk_reward", "5")),
                    "pnl": float(t.get("pnl", "0")),
                    "qty": int(t.get("qty", "50")),
                    "status": t.get("status")
                }
                break
        
        return jsonify({
            "ticker": ticker.upper(),
            "resolved": resolved,
            "dates": dates,
            "timestamps": timestamps,
            "opens": opens,
            "highs": highs,
            "lows": lows,
            "closes": closes,
            "sma": sma,
            "volumes": volumes,
            "smc": smc,
            "active_trade": active_trade
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/run/<ticker>", methods=["POST"])
def run_pipeline(ticker):
    """Triggers the trading bot pipeline for a specific ticker and returns step-by-step results."""
    ticker_upper = ticker.upper()
    try:
        # Step 1: Market data fetching
        market_summary = get_market_summary(ticker_upper)
        if market_summary.startswith("Error:"):
            return jsonify({
                "ticker": ticker_upper,
                "step1": {"status": "error", "message": market_summary},
                "step2": {"status": "skipped"},
                "step3": {"status": "skipped"},
                "step4": {"status": "skipped"}
            }), 400

        # Extract current price from summary
        current_price = 0.0
        for line in market_summary.split("\n"):
            if line.startswith("Current Price:"):
                try:
                    current_price = float(line.split(":")[1].strip())
                except Exception:
                    pass

        # Step 2: Course context retrieval
        course_rules = retrieve_course_rules(ticker_upper)

        # Step 3: LLM reasoning (Ollama request)
        decision = generate_trading_decision(ticker_upper, market_summary, course_rules)
        
        # Check if decision failed/timed out
        llm_status = "success"
        if "timed out" in decision.get("technical_reasoning", "").lower() or "error" in decision.get("technical_reasoning", "").lower():
            llm_status = "warning"

        # Step 4: Paper execution logging
        process_signal(decision, current_price=current_price)

        # Reload updated trade execution log detail to return in final step response
        trades = parse_paper_trades_log()
        executed_trade = None
        for t in trades:
            if t.get("ticker") == ticker_upper:
                executed_trade = t
                break

        return jsonify({
            "ticker": ticker_upper,
            "step1": {"status": "success", "data": market_summary, "current_price": current_price},
            "step2": {"status": "success", "data": course_rules},
            "step3": {"status": llm_status, "data": decision},
            "step4": {"status": "success", "message": "Simulated trade processed and logged successfully.", "trade": executed_trade}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/log", methods=["GET"])
def get_logs():
    """Gets parsed logs of paper trades."""
    return jsonify(parse_paper_trades_log())

@app.route("/api/settings", methods=["GET", "POST"])
def manage_settings():
    """Retrieves or modifies configurations in memory."""
    if request.method == "POST":
        req_data = request.json or {}
        
        # Update configurations dynamically in memory
        if "watch_list" in req_data:
            config.WATCH_LIST = [t.upper().strip() for t in req_data["watch_list"]]
        if "ollama_base_url" in req_data:
            config.OLLAMA_BASE_URL = req_data["ollama_base_url"].strip()
            config.OLLAMA_GENERATE_URL = f"{config.OLLAMA_BASE_URL}/api/generate"
        if "ollama_model" in req_data:
            config.OLLAMA_MODEL = req_data["ollama_model"].strip()
            
        return jsonify({
            "status": "success",
            "message": "Settings updated in memory successfully.",
            "settings": {
                "watch_list": config.WATCH_LIST,
                "ollama_base_url": config.OLLAMA_BASE_URL,
                "ollama_model": config.OLLAMA_MODEL
            }
        })
    else:
        return jsonify({
            "watch_list": config.WATCH_LIST,
            "ollama_base_url": config.OLLAMA_BASE_URL,
            "ollama_model": config.OLLAMA_MODEL
        })

if __name__ == "__main__":
    print("====================================================================")
    print("                 BOTKUBERA INTERACTIVE DASHBOARD")
    print("====================================================================")
    print(f"Server starting on: http://127.0.0.1:5050")
    print("====================================================================")
    app.run(host="127.0.0.1", port=5050, debug=True)
