import os
import sys
from fpdf import FPDF

class SMCReport(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "B", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "SMC AI TRADING BOT CONSOLE - SYSTEM SPECIFICATION REPORT", ln=True, align="R")
            self.set_draw_color(224, 225, 226)
            self.line(10, 16, 200, 16)
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

def create_report():
    pdf = SMCReport()
    pdf.alias_nb_pages()
    
    # ------------------ PAGE 1: TITLE PAGE ------------------
    pdf.add_page()
    pdf.set_margins(15, 15, 15)
    
    # Primary Color Accent Band (Top banner)
    pdf.set_fill_color(11, 13, 20) # Deep Navy-Black
    pdf.rect(0, 0, 210, 85, 'F')
    
    pdf.ln(25)
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "SMC AI TRADING BOT CONSOLE", ln=True, align="C")
    
    pdf.set_font("helvetica", "I", 12)
    pdf.set_text_color(0, 229, 255) # Cyan Accent
    pdf.cell(0, 8, "Local AI-Driven Algorithmic Paper-Trading Dashboard", ln=True, align="C")
    
    pdf.ln(50)
    pdf.set_font("helvetica", "", 11)
    pdf.set_text_color(43, 45, 66) # Dark grey body
    pdf.cell(0, 6, "PROJECT SPECIFICATION & SYSTEM SPECIFICATION", ln=True, align="C")
    
    pdf.ln(20)
    # Metadata Box
    pdf.set_fill_color(240, 242, 245)
    pdf.rect(35, 135, 140, 65, 'F')
    
    pdf.set_y(140)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 6, "Author:", align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(90, 6, " Antigravity AI Developer Assistant", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 6, "Client Partner:", align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(90, 6, " Yagya (Workspace Owner)", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 6, "Date:", align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(90, 6, " August 2026", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 6, "Assets Supported:", align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(90, 6, " XAUUSD, XAGUSD, BTCUSD, ETHUSD, GBPUSD", ln=True)
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(50, 6, "Project Status:", align="R")
    pdf.set_font("helvetica", "", 10)
    pdf.cell(90, 6, " Completed & Verified", ln=True)
    
    # ------------------ PAGE 2: TABLE OF CONTENTS ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 16)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "Table of Contents", ln=True)
    pdf.ln(5)
    pdf.line(15, 33, 195, 33)
    pdf.ln(8)
    
    toc_items = [
        ("1. Executive Summary & Core Concept", "3"),
        ("2. Smart Money Concepts (SMC) Trading Strategy", "4"),
        ("3. Technical Architecture & Component Design", "5"),
        ("4. Local LLM Integration (Ollama Client)", "6"),
        ("5. User Interface (UI/UX) & Financial Visualizations", "7"),
        ("6. Operation & Startup Instructions", "8"),
    ]
    
    pdf.set_font("helvetica", "", 11)
    for title, page in toc_items:
        pdf.cell(150, 8, title, align="L")
        pdf.set_text_color(11, 13, 20)
        pdf.cell(30, 8, f"Page {page}", align="R", ln=True)
        pdf.ln(2)
        
    # ------------------ PAGE 3: EXECUTIVE SUMMARY ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "1. Executive Summary & Core Concept", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    text = (
        "The SMC AI Trading Bot Console is an advanced algorithmic trading prototype built to simulate "
        "high-probability trade executions using Smart Money Concepts (SMC). The primary goal of the system "
        "is to combine traditional quantitative financial analysis with local large language model (LLM) reasoning "
        "to simulate institutional-grade trading decisions on retail trading charts.\n\n"
        "Rather than relying strictly on standard mathematical indicators like moving averages or RSI crossovers, "
        "the bot identifies key institutional structures: Consolidation Ranges (Session Highs/Lows), Liquidity Sweeps, "
        "Fair Value Gaps, and Order Blocks. By scanning these patterns, calculating their boundaries programmatically, "
        "and retrieving tailored course strategy guidelines, the bot feeds a structured payload to a locally hosted LLM "
        "via Ollama. The model then executes a reasoning loop and outputs structured execution orders."
    )
    pdf.multi_cell(0, 6, text)
    pdf.ln(8)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Target Assets & Symbols Resolution Map", ln=True)
    pdf.ln(2)
    
    # Table header
    pdf.set_fill_color(240, 242, 245)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(30, 8, "Asset Name", border=1, fill=True)
    pdf.cell(35, 8, "YFinance Ticker", border=1, fill=True)
    pdf.cell(35, 8, "Instrument Class", border=1, fill=True)
    pdf.cell(80, 8, "Default Strategy Model", border=1, fill=True, ln=True)
    
    # Table rows
    table_data = [
        ("XAUUSD", "GC=F", "Commodity (Gold)", "SMC Session Sweep & Retest"),
        ("XAGUSD", "SI=F", "Commodity (Silver)", "SMC Session Sweep & Retest"),
        ("BTCUSD", "BTC-USD", "Crypto (Bitcoin)", "Liquidity Hunt & Displacement"),
        ("ETHUSD", "ETH-USD", "Crypto (Ethereum)", "Liquidity Hunt & Displacement"),
        ("GBPUSD", "GBPUSD=X", "Forex (Cable)", "London Session Breakout & Retest")
    ]
    
    pdf.set_font("helvetica", "", 9)
    for row in table_data:
        pdf.cell(30, 8, row[0], border=1)
        pdf.cell(35, 8, row[1], border=1)
        pdf.cell(35, 8, row[2], border=1)
        pdf.cell(80, 8, row[3], border=1, ln=True)

    # ------------------ PAGE 4: SMC STRATEGY ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "2. Smart Money Concepts (SMC) Trading Strategy", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    intro_smc = (
        "Smart Money Concepts (SMC) is a trading philosophy modeled after institutional trading logic. It focuses "
        "on where banks and institutional market-makers place liquidity (resting orders) and how they manipulate "
        "retail stop-losses before moving the market. The bot implements three core pillars of this strategy:"
    )
    pdf.multi_cell(0, 6, intro_smc)
    pdf.ln(6)
    
    strategy_points = [
        ("Session Consolidation Ranges", 
         "Institutions build positions during low-volume sessions (like the Asian session). The bot automatically identifies "
         "this consolidation zone by scanning a lookback window (candle indexes -48 to -12) and extracting the exact high "
         "and low prices, representing key buy-side and sell-side liquidity pools."),
         
        ("Liquidity Sweeps", 
         "A sweep occurs when the price breaches a consolidation boundary (Session High/Low) but fails to sustain. "
         "A bearish sweep spikes above the Session High to capture retail short stop-losses (buy-side liquidity) and closes "
         "back inside the range, indicating a short trade. A bullish sweep spikes below the Session Low to capture long "
         "stop-losses (sell-side liquidity) and closes back inside, indicating a long trade."),
         
        ("Fair Value Gaps (FVG) & Order Blocks (OB) Retests", 
         "An Order Block is the last opposite candle before a rapid institutional movement (displacement). A Fair Value "
         "Gap is a three-candle structure where the wicks of Candle 1 and Candle 3 do not overlap, leaving an imbalance. "
         "The bot places entry limit orders at the open of these imbalances, predicting that price will retest them "
         "before expanding.")
    ]
    
    for title, desc in strategy_points:
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(0, 180, 216)
        pdf.cell(0, 6, title, ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(43, 45, 66)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(4)

    # ------------------ PAGE 5: Technical Architecture ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "3. Technical Architecture & Component Design", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    arch_desc = (
        "The prototype is built as a modular python application orchestrating data fetching, technical calculations, "
        "local RAG rules, local LLM inference, simulated trade logging, and a web-based visualization frontend.\n\n"
        "The backend components are detailed below:"
    )
    pdf.multi_cell(0, 6, arch_desc)
    pdf.ln(5)
    
    components = [
        ("Flask Server (app.py)", "Serves the TradingView-style HTML page. Exposes API endpoints for watchlist stock prices, chart candle data (with embedded SMC ranges, sweeps, FVGs), pipeline triggers, and parsed trade executions log history."),
        ("SMC Data Engine (data_engine.py)", "Fetches raw OHLCV hourly candle data from Yahoo Finance. Computes SMA lines and runs the math models to calculate session highs/lows, sweeps, FVGs, and Order Blocks dynamically on Pandas DataFrames."),
        ("RAG Strategy Rules (rag_engine.py)", "Simulates a semantic search database of a trading course. Provides exact strategy logic, risk rules, and stop-loss/take-profit models depending on the class of asset evaluated."),
        ("LLM Client (llm_client.py)", "Builds system instructions and user payloads. Communicates with local Ollama APIs, sends data to the inference server, and runs JSON parsing and defensive schema validation."),
        ("Execution Engine (execution_engine.py)", "Processes signals. Emulates trade status (OPEN, CLOSED_PROFIT, CLOSED_LOSS) and logs trades to a local log file, ensuring safety by preventing real-capital execution.")
    ]
    
    for name, desc in components:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(11, 13, 20)
        pdf.cell(50, 6, name, align="L")
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(43, 45, 66)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(3)

    # ------------------ PAGE 6: LLM Client ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "4. Local LLM Integration (Ollama Client)", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    llm_desc = (
        "The bot routes decision-making logic to a local LLM hosted via Ollama. By deploying a local model "
        "like llama3:8b, the bot operates without reliance on cloud API fees and preserves data privacy.\n\n"
        "To ensure deterministic executions, the prompt forces the LLM to output exclusively a strict JSON schema. "
        "The client parses, normalizes, and validates this output dynamically. If the model fails to respond or "
        "errors out, defensive defaults are loaded."
    )
    pdf.multi_cell(0, 6, llm_desc)
    pdf.ln(8)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Target JSON Output Schema", ln=True)
    pdf.ln(2)
    
    schema_code = (
        "{\n"
        '    "ticker": "STRING (e.g. XAUUSD)",\n'
        '    "action": "BUY" | "SELL" | "HOLD",\n'
        '    "confidence_score": FLOAT (0.0 to 1.0 representing conviction),\n'
        '    "strategy_applied": "STRING (name of the course rule applied)",\n'
        '    "technical_reasoning": "STRING (short reasoning leading to decision)",\n'
        '    "suggested_stop_loss_pct": FLOAT (recommended stop distance, e.g. 0.080),\n'
        '    "suggested_target_pct": FLOAT (recommended target profit distance, e.g. 0.750),\n'
        '    "risk_reward_ratio": FLOAT (suggested risk-to-reward ratio, e.g. 9.38),\n'
        '    "quantity": INTEGER (suggested contract size/quantity, e.g. 72)\n'
        "}"
    )
    
    pdf.set_fill_color(245, 246, 248)
    pdf.set_font("courier", "", 9)
    pdf.set_text_color(11, 13, 20)
    
    pdf.rect(15, 100, 180, 75, 'F')
    pdf.set_y(102)
    for line in schema_code.split("\n"):
        pdf.cell(0, 5, "  " + line, ln=True)
        
    pdf.ln(12)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    pdf.multi_cell(0, 5, "The execution engine converts these percentages into stop-loss and take-profit target prices relative to the current market price upon entry, emulates a trade outcome, and logs it.")

    # ------------------ PAGE 7: UI/UX Redesign ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "5. User Interface (UI/UX) & Financial Visualizations", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    ui_desc = (
        "The frontend is redesigned to deliver a premium, glassmorphic layout tailored specifically for "
        "Smart Money Concepts (SMC) visual indicators. We integrated the TradingView Lightweight Charts (v4.0) library "
        "and overlaid a dynamic custom drawing layer to display indicators directly on top of the HTML5 canvas."
    )
    pdf.multi_cell(0, 6, ui_desc)
    pdf.ln(6)
    
    ui_features = [
        ("Unified Candlestick Series & SMA", "Displays standard financial candlestick wicks and bodies (green for up, red for down). Computes and displays a dashed golden 20 Simple Moving Average (SMA) line dynamically."),
        ("Consolidation Zone Highlight", "Locates lookback candles corresponding to the Asian session range. Draws a semi-transparent, light blue dashed boundary box on the chart representing the accumulation range."),
        ("Liquidity Sweep Indicators", "Flags candles where the high or low wicks swept past the session consolidation box but closed back inside. Draws cyan sweep arrows above or below the wicks."),
        ("Risk-to-Reward Drawing Overlay", "Draws red (loss) and green (profit) boxes on the chart representing active trades. Anchored with white-bordered floating center badges for PnL/Qty stats and glowing corner touch control points, mimicking the official TradingView Short/Long Position tool.")
    ]
    
    for title, desc in ui_features:
        pdf.set_font("helvetica", "B", 11)
        pdf.set_text_color(0, 180, 216)
        pdf.cell(0, 6, title, ln=True)
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(43, 45, 66)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(4)

    # ------------------ PAGE 8: Deployment & Operation ------------------
    pdf.add_page()
    pdf.ln(15)
    
    pdf.set_font("helvetica", "B", 14)
    pdf.set_text_color(11, 13, 20)
    pdf.cell(0, 10, "6. Operation & Startup Instructions", ln=True)
    pdf.ln(5)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(43, 45, 66)
    
    op_desc = (
        "The project is packaged with a virtual environment and a launcher batch file to make operational "
        "startup seamless on Windows environments."
    )
    pdf.multi_cell(0, 6, op_desc)
    pdf.ln(6)
    
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "How to Launch the System", ln=True)
    pdf.ln(2)
    
    instructions = [
        ("Step 1", "Launch Ollama and start the LLM inference server (Command: 'ollama run llama3:8b')."),
        ("Step 2", "Double-click the 'SMC Trading Bot' shortcut on your Desktop (or run 'run_bot.bat' directly)."),
        ("Step 3", "The script activates the virtual environment, starts the server unbuffered, and launches the browser."),
        ("Step 4", "Open http://127.0.0.1:5050/ to view, choose your instrument, and trigger watchlist scans.")
    ]
    
    for step, desc in instructions:
        pdf.set_font("helvetica", "B", 10)
        pdf.set_text_color(11, 13, 20)
        pdf.cell(20, 6, step, align="L")
        pdf.set_font("helvetica", "", 10)
        pdf.set_text_color(43, 45, 66)
        pdf.multi_cell(0, 5, desc)
        pdf.ln(3)
        
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "Conclusion", ln=True)
    pdf.ln(2)
    pdf.multi_cell(0, 5, "The SMC AI Trading Bot successfully bridges retail chart analysis with local deep learning models. By parsing order blocks, sweeps, and gaps programmatically, the system demonstrates high-conviction trade entries in a completely local, secure environment.")
    
    pdf.output("SMC_Trading_Bot_Project_Report.pdf")
    print("[SUCCESS] PDF successfully written to SMC_Trading_Bot_Project_Report.pdf.")

if __name__ == "__main__":
    create_report()
