"""Main orchestrator for the Local AI-Driven Trading Bot Prototype.

Runs a sequential CLI workflow across the watch list of tickers, coordinates
data downloading, retrieves trading strategies, queries Ollama, and logs paper
trades.
"""

import json
import time
from typing import Any, Dict
from config import WATCH_LIST
from data_engine import get_market_summary
from execution_engine import process_signal
from llm_client import generate_trading_decision
from rag_engine import retrieve_course_rules


def run_pipeline_for_ticker(ticker: str) -> None:
    """Executes the pipeline for a single stock ticker.

    1. Fetches historical and live market summary.
    2. Retrieves technical trading course rules.
    3. Feeds context to Ollama local LLM.
    4. Prints decision and routes to the paper trading log.

    Args:
        ticker: The stock ticker symbol.
    """
    print("\n" + "=" * 80)
    print(f"[*] Starting Pipeline execution for stock ticker: {ticker}")
    print("=" * 80)

    # Step 1: Market Data Retrieval
    print(f"[Step 1/4] Downloading latest candle data for {ticker}...")
    market_summary = get_market_summary(ticker)

    if market_summary.startswith("Error:"):
        print(f"[ERROR] {market_summary}")
        print(f"Skipping pipeline run for {ticker}.")
        return

    # Extract price for logging execution purposes
    current_price = 0.0
    for line in market_summary.split("\n"):
        if line.startswith("Current Price:"):
            try:
                current_price = float(line.split(":")[1].strip())
            except (ValueError, IndexError):
                pass

    print("[SUCCESS] Market data successfully fetched and summarized:")
    print("-" * 50)
    print(market_summary)
    print("-" * 50)

    # Step 2: Course Context Retrieval
    print(f"[Step 2/4] Retrieving course strategy rules for {ticker}...")
    course_rules = retrieve_course_rules(ticker)
    print("[SUCCESS] Strategy retrieved:")
    print("-" * 50)
    print(course_rules)
    print("-" * 50)

    # Step 3: local LLM reasoning
    print(f"[Step 3/4] Submitting prompt to local LLM for {ticker}...")
    decision = generate_trading_decision(ticker, market_summary, course_rules)

    print("[SUCCESS] Ollama generated trading decision:")
    print("-" * 50)
    print(json.dumps(decision, indent=4))
    print("-" * 50)

    # Step 4: Paper execution logging
    print(f"[Step 4/4] Routing decision to safe Execution Engine...")
    process_signal(decision, current_price=current_price)
    print(f"[*] Pipeline execution completed for {ticker}.")


def main() -> None:
    """Orchestrates the entire bot loop across all configured watch list tickers."""
    print("================================================================================")
    print("                       BOTKUBERA PROTOTYPE INITIALIZED")
    print("================================================================================")
    print(f"Watch List: {', '.join(WATCH_LIST)}")
    print("Note: This bot runs strictly in paper-trading/simulation mode.")
    print("No real trades will be sent to any exchange.")
    print("================================================================================")

    start_time = time.time()

    for idx, ticker in enumerate(WATCH_LIST, 1):
        print(f"\nProcessing {idx}/{len(WATCH_LIST)} tickers...")
        run_pipeline_for_ticker(ticker)

    end_time = time.time()
    duration = end_time - start_time
    print("\n" + "=" * 80)
    print(f"[FINISHED] Watch list scan completed in {duration:.2f} seconds.")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
