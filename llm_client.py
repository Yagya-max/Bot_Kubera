"""Ollama LLM client integration for generating trading decisions.

Handles communicating with the local Ollama API, prompt formatting, and
defensive validation of JSON output schemas.
"""

import json
from typing import Any, Dict
import requests
from config import CONNECTION_TIMEOUT, OLLAMA_GENERATE_URL, OLLAMA_MODEL


def generate_trading_decision(
    ticker: str, market_data: str, course_rules: str
) -> Dict[str, Any]:
    """Sends stock data and trading rules to local Ollama API and retrieves a

    structured trade decision.

    Args:
        ticker: The stock ticker symbol.
        market_data: The text summary of OHLC and SMA data.
        course_rules: The text rules from the trading course.

    Returns:
        A dictionary containing the parsed JSON trading signal.
    """
    # Safe fallback response
    fallback_decision: Dict[str, Any] = {
        "ticker": ticker.upper(),
        "action": "HOLD",
        "confidence_score": 0.0,
        "strategy_applied": "N/A",
        "technical_reasoning": "Fallback activated due to an error, timeout, or invalid response format.",
        "suggested_stop_loss_pct": 0.0,
        "suggested_target_pct": 0.0,
        "risk_reward_ratio": 5.0,
        "quantity": 50,
    }

    # Construct the instruction and formatting prompt
    system_prompt = (
        "You are an algorithmic execution layer for a professional financial trading system.\n"
        "Your task is to analyze the provided market data and apply the specific trading course rules to make a decision.\n"
        "You must respond ONLY with a valid JSON object matching the exact schema below.\n"
        "Do not include any pre-text, post-text, markdown backticks, or comments in your response.\n\n"
        "Target JSON Schema:\n"
        "{\n"
        '    "ticker": "STRING (e.g., XAUUSD)",\n'
        '    "action": "BUY" | "SELL" | "HOLD",\n'
        '    "confidence_score": FLOAT (0.0 to 1.0 representing your conviction),\n'
        '    "strategy_applied": "STRING (name of the course rule applied)",\n'
        '    "technical_reasoning": "STRING (short explanation of indicators/volume leading to decision)",\n'
        '    "suggested_stop_loss_pct": FLOAT (recommended stop-loss percentage from rules, e.g. 0.08),\n'
        '    "suggested_target_pct": FLOAT (recommended take-profit percentage, e.g. 0.75),\n'
        '    "risk_reward_ratio": FLOAT (suggested risk-to-reward ratio, e.g. 9.38),\n'
        '    "quantity": INTEGER (suggested contract size/quantity, e.g. 72)\n'
        "}\n"
    )

    user_prompt = (
        f"Ticker: {ticker}\n\n"
        f"--- MARKET DATA ---\n"
        f"{market_data}\n\n"
        f"--- TRADING COURSE RULES ---\n"
        f"{course_rules}\n\n"
        f"Decision:"
    )

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\n{user_prompt}",
        "format": "json",
        "stream": False,
    }

    try:
        # Send POST request to Ollama
        response = requests.post(
            OLLAMA_GENERATE_URL, json=payload, timeout=CONNECTION_TIMEOUT
        )

        # Check response status
        if response.status_code != 200:
            print(
                f"[WARNING] Ollama returned status code {response.status_code} for {ticker}."
            )
            fallback_decision["technical_reasoning"] = (
                f"Ollama server returned HTTP {response.status_code}."
            )
            return fallback_decision

        response_data = response.json()
        raw_text = response_data.get("response", "").strip()

        if not raw_text:
            print(f"[WARNING] Empty response text from Ollama for {ticker}.")
            return fallback_decision

        # Parse raw text as JSON
        decision = json.loads(raw_text)

        # Normalize action and check schema
        action_val = str(decision.get("action", "HOLD")).upper()
        if action_val not in ["BUY", "SELL", "HOLD"]:
            action_val = "HOLD"

        # Safe defaults if keys are missing
        validated_decision: Dict[str, Any] = {
            "ticker": str(decision.get("ticker", ticker)).upper(),
            "action": action_val,
            "confidence_score": float(decision.get("confidence_score", 0.0)),
            "strategy_applied": str(
                decision.get("strategy_applied", "Unknown Strategy")
            ),
            "technical_reasoning": str(
                decision.get("technical_reasoning", "No reasoning provided.")
            ),
            "suggested_stop_loss_pct": float(
                decision.get("suggested_stop_loss_pct", 0.0)
            ),
            "suggested_target_pct": float(
                decision.get("suggested_target_pct", 0.0)
            ),
            "risk_reward_ratio": float(
                decision.get("risk_reward_ratio", 5.0)
            ),
            "quantity": int(
                decision.get("quantity", 50)
            ),
        }

        # Validate ranges
        if not (0.0 <= validated_decision["confidence_score"] <= 1.0):
            validated_decision["confidence_score"] = max(
                0.0, min(1.0, validated_decision["confidence_score"])
            )

        return validated_decision

    except requests.exceptions.ConnectionError:
        print("\n" + "=" * 60)
        print("[ERROR] Connection to Ollama failed!")
        print(f"Failed to connect to: {OLLAMA_GENERATE_URL}")
        print("Please verify that Ollama is installed and running locally.")
        print(f"Ensure you have downloaded the target model: `ollama run {OLLAMA_MODEL}`")
        print("=" * 60 + "\n")
        fallback_decision["technical_reasoning"] = (
            "Ollama server connection error. Is the service running locally?"
        )
        return fallback_decision

    except requests.exceptions.Timeout:
        print(f"[ERROR] Request to Ollama timed out after {CONNECTION_TIMEOUT} seconds.")
        fallback_decision["technical_reasoning"] = "Request to Ollama timed out."
        return fallback_decision

    except json.JSONDecodeError as jde:
        print(f"[WARNING] Failed to parse Ollama response as JSON: {jde}")
        print(f"Raw response was: {raw_text}")
        fallback_decision["technical_reasoning"] = (
            f"JSON decoding error: {str(jde)}"
        )
        return fallback_decision

    except Exception as e:
        print(f"[ERROR] Unexpected error in llm_client: {str(e)}")
        fallback_decision["technical_reasoning"] = f"Unexpected error: {str(e)}"
        return fallback_decision
