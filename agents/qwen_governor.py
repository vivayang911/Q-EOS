import json
import re
import time
import dashscope
from dashscope import Generation

from core.config import QWEN_API_KEY, MODEL_NAME


class QwenGovernor:
    def __init__(self):
        dashscope.api_key = QWEN_API_KEY

    def _extract_json(self, text):
        """
        Qwen 有时会用 Markdown 代码块包裹 JSON（```json ... ```），
        或在 JSON 前后附带解释性文字。直接 json.loads(text) 在这些情况下
        会抛 JSONDecodeError。这里先尝试直接解析，失败后用正则提取
        被包裹/夹杂文字的 JSON 主体作为兜底。
        """
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 去除常见的 Markdown 代码块围栏后再试一次
        fenced = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
        try:
            return json.loads(fenced.strip())
        except json.JSONDecodeError:
            pass

        # 非贪婪匹配第一个完整的 {...} 块，避免贪婪匹配截取过多内容
        match = re.search(r"\{.*?\}", text, re.S)
        if match:
            return json.loads(match.group())

        raise ValueError(f"No valid JSON found in Qwen response: {text[:200]}")

    def decide(self, price, risk_score, action, balance, max_retries=2):
        """
        Qwen 最终治理决策层
        """
        # 硬规则兜底（安全底线）
        if balance < 10000:
            return {
                "decision": "REJECT",
                "reason": "Treasury balance below safety threshold (10,000 USDC).",
                "risk_level": "HIGH"
            }

        if abs(action) > balance * 0.10:
            return {
                "decision": "REJECT",
                "reason": f"Action {action:.2f} exceeds 10% of treasury balance.",
                "risk_level": "HIGH"
            }

        # Qwen 推理
        prompt = f"""
You are the final governance approval layer.

The policy engine has already determined
the final intervention amount.

Price: {price}
Risk Score: {risk_score}
Treasury Balance: {balance}
Policy Approved Action: {action}

Your task:
ONLY decide whether this action
should be APPROVED or REJECTED.

Focus on:
1. Treasury safety
2. Risk exposure
3. Abnormal market conditions

Do NOT redesign the action size.

Return JSON only, with no Markdown formatting, no code fences, no explanation:
{{
  "decision": "APPROVE",
  "reason": "...",
  "risk_level": "LOW"
}}
"""

        last_error = None
        for attempt in range(max_retries + 1):
            try:
                response = Generation.call(
                    model=MODEL_NAME,
                    prompt=prompt
                )

                text = response.output.text.strip()
                result = self._extract_json(text)

                # 确保返回字段完整
                result.setdefault("decision", "REJECT")
                result.setdefault("reason", "Qwen response missing decision")
                result.setdefault("risk_level", "UNKNOWN")

                return result

            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # 短暂退避后重试，应对偶发的网络抖动/超时
                    time.sleep(1.5 * (attempt + 1))
                    continue

        # 重试耗尽后，明确选择 fail-closed（拒绝），而非 fail-open（默认放行）。
        # 治理/资金类系统在不确定状态下应当拒绝操作、维持现状，
        # 而不是在连 Qwen 本身都无法确认的情况下批准资金操作。
        # 这次故障的具体原因会被记录在 reason 里，便于事后区分
        # "Qwen 主动拒绝" 与 "API 故障导致的拒绝"，避免两者在日志里混淆。
        return {
            "decision": "REJECT",
            "reason": f"Qwen API unreachable after {max_retries + 1} attempts: {str(last_error)}",
            "risk_level": "UNKNOWN",
            "is_system_failure": True
        }
