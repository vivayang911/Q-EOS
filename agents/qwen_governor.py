import json
import dashscope
from dashscope import Generation

from core.config import (
    QWEN_API_KEY,
    MODEL_NAME
)


class QwenGovernor:

    def __init__(self):

        dashscope.api_key = QWEN_API_KEY

    def decide(
        self,
        price,
        risk_score,
        action,
        balance
    ):

        # =====================
        # Hard Rules
        # =====================

        if risk_score >= 90:
            return {
                "decision": "REJECT",
                "reason": "Risk too high",
                "risk_level": "HIGH",
                "multiplier": 0
            }

        if balance < 10000:
            return {
                "decision": "REJECT",
                "reason": "Balance too low",
                "risk_level": "HIGH",
                "multiplier": 0
            }

        if abs(action) > balance * 0.10:
            return {
                "decision": "REJECT",
                "reason": "Action exceeds 10% treasury",
                "risk_level": "HIGH",
                "multiplier": 0
            }

        if price < 0.85 and action < 0:
            return {
                "decision": "REJECT",
                "reason": "Depeg sell blocked",
                "risk_level": "HIGH",
                "multiplier": 0
            }

        if price > 1.15 and action > 0:
            return {
                "decision": "REJECT",
                "reason": "Overheat buy blocked",
                "risk_level": "HIGH",
                "multiplier": 0
            }

        # =====================
        # AI Layer
        # =====================

        prompt = f"""
You are a stablecoin governance AI.

Return ONLY JSON.

Market Price: {price}
Risk Score: {risk_score}
Treasury Balance: {balance}
Proposed Action: {action}

You must decide BOTH:
1. APPROVE or REJECT
2. intervention strength (multiplier)

Policy strength rules:

Price near peg (0.98 - 1.02):
multiplier = 0.5

Moderate deviation (0.95 - 0.98 OR 1.02 - 1.05):
multiplier = 1.0

Severe depeg (<0.95 or >1.05):
multiplier = 1.5

Rules:
- Return JSON only
- If reject, multiplier must be 0

Format:
{{
  "decision": "APPROVE",
  "reason": "...",
  "risk_level": "LOW",
  "multiplier": 1.0
}}
Return ONLY JSON.

price={price}
risk={risk_score}
balance={balance}
action={action}

Return:
{{
  "decision":"APPROVE",
  "reason":"...",
  "risk_level":"LOW",
  "multiplier":1.0
}}
"""

        try:
            response = Generation.call(
                model=MODEL_NAME,
                prompt=prompt
            )

            text = response.output.text.strip()

            result = json.loads(text)

            result.setdefault("multiplier", 1.0)

            return result

        except Exception as e:

            return {
                "decision": "REJECT",
                "reason": str(e),
                "risk_level": "UNKNOWN",
                "multiplier": 0
            }