from core.message import Message
from agents.qwen_governor import QwenGovernor

class GovernorAgent:
    def __init__(self, bus, logger, use_qwen=True):
        self.bus = bus
        self.logger = logger
        self.use_qwen = use_qwen
        if use_qwen:
            try:
                self.qwen = QwenGovernor()
                print("[Governor] QwenGovernor initialized")
            except Exception as e:
                print(f"[Governor] Qwen init error: {e}")
                self.qwen = None
        else:
            self.qwen = None
            print("[Governor] Fast mode (no Qwen)")

    def _would_treasury_block(self, action, price, balance):
        """
        预测 Treasury 是否会拒绝此操作（匹配硬约束规则）
        """
        # 余额过低
        if balance < 5000:
            return True
        # 操作金额超过国库 10%
        if abs(action) > balance * 0.10:
            return True
        # 极端价格
        if price < 0.7 or price > 1.3:
            return True
        return False

    def step(self):
        msgs = self.bus.get_for("Governor")
        for msg in msgs:
            price = msg.payload.get("price")
            risk_score = msg.payload.get("risk_score")
            action = msg.payload.get("action", 0)
            balance = msg.payload.get("balance", 0)

            if self.use_qwen and self.qwen is not None:
                # Qwen 决策
                try:
                    result = self.qwen.decide(price, risk_score, action, balance)
                    decision = result.get("decision")
                    reason = result.get("reason")
                    risk_level = result.get("risk_level")
                    print(f"[Qwen] {decision} Risk={risk_level}")
                    print(f"[Reason] {reason}")
                except Exception as e:
                    print(f"[Governor] Qwen call failed: {e}")
                    decision = "REJECT"
            else:
                # ========== 快速模式：主动匹配 Treasury 硬约束 ==========
                if self._would_treasury_block(action, price, balance):
                    decision = "REJECT"
                    print(f"[Governor] Fast mode: REJECT (would be blocked by Treasury)")
                else:
                    # 额外经济合理性检查（国库健康、价格偏离）
                    if balance < 10000:
                        decision = "REJECT"
                        print("[Governor] Fast mode: REJECT (treasury too low)")
                    elif price < 0.85 or price > 1.15:
                        if balance < 15000:
                            decision = "REJECT"
                            print("[Governor] Fast mode: REJECT (extreme price + low treasury)")
                        else:
                            decision = "APPROVE"
                            print("[Governor] Fast mode: APPROVE (extreme price but treasury ok)")
                    else:
                        decision = "APPROVE"
                        print("[Governor] Fast mode: APPROVE")

            # 发送决策给 Treasury
            if decision == "APPROVE":
                self.bus.send(
                    Message(
                        "Governor",
                        "Treasury",
                        "EXECUTE",
                        {
                            "price": price,
                            "action": action,
                            "risk_score": risk_score,
                            "approved": True
                        }
                    )
                )
                print("[Governor] APPROVED → EXECUTE")
            else:
                self.bus.send(
                    Message(
                        "Governor",
                        "Treasury",
                        "REJECT",
                        {
                            "price": price,
                            "action": 0,
                            "risk_score": risk_score,
                            "approved": False
                        }
                    )
                )
                print("[Governor] REJECT")

            # 记录日志
            if decision == "APPROVE":
                if action > 0:
                    self.logger.add(f"BUYBACK {action:.2f}")
                elif action < 0:
                    self.logger.add(f"SELL {abs(action):.2f}")
                else:
                    self.logger.add("NO_ACTION")
            else:
                self.logger.add("REJECT")