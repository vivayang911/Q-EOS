from core.message import Message
from core.config import INITIAL_TREASURY

class TreasuryAgent:
    def __init__(self, bus, market):
        self.bus = bus
        self.market = market
        self.balance = INITIAL_TREASURY
        self.recent_net_changes = []
        self.max_history = 10

    def _enforce_hard_constraints(self, action, price):
        """硬约束检查（仅当 approved=True 时执行）"""
        if self.balance < 5000:
            return False, f"Emergency stop: treasury below 5000 (current {self.balance:.2f})"
        if abs(action) > self.balance * 0.10:
            return False, f"Action {action:.2f} exceeds 10% of treasury ({self.balance * 0.10:.2f})"
        if price < 0.7 or price > 1.3:
            return False, f"Extreme price deviation {price:.2f}, operations paused"
        if len(self.recent_net_changes) >= 5:
            net_change = sum(self.recent_net_changes[-5:])
            if net_change < -self.balance * 0.05 and action > 0:
                return False, f"Recent net consumption {net_change:.2f} > 5% treasury, buyback paused"
        return True, "Hard constraints passed"

    def step(self):
        msgs = self.bus.get_for("Treasury")
        for msg in msgs:
            approved = msg.payload.get("approved", False)
            action = msg.payload.get("action", 0)
            price = msg.payload.get("price", 1.0)

            # ========== 如果 Governor 拒绝，直接跳过 ==========
            if not approved:
                print(f"[Treasury] BLOCKED ❌ (Governor REJECT) action={action:.2f}")
                continue

            # ========== 硬约束检查（仅当 approved=True） ==========
            hard_ok, reason = self._enforce_hard_constraints(action, price)
            if not hard_ok:
                print(f"[Treasury] BLOCKED ❌ Hard constraint: {reason}")
                continue

            # ========== 执行操作 ==========
            if action > 0:
                if action <= self.balance:
                    self.balance -= action
                    self.market.apply_buyback(action)
                    print(f"[Treasury] EXECUTED Buyback amount={action:.2f}, new balance={self.balance:.2f}")
                    self.recent_net_changes.append(-action)
                else:
                    print(f"[Treasury] FAILED ❌ Insufficient balance for buyback {action:.2f}")
                    continue
            elif action < 0:
                sell_amount = abs(action)
                self.balance += sell_amount
                self.market.apply_sell(sell_amount)
                print(f"[Treasury] EXECUTED Sell amount={sell_amount:.2f}, new balance={self.balance:.2f}")
                self.recent_net_changes.append(sell_amount)
            else:
                print("[Treasury] No action (amount=0)")
                continue

            if len(self.recent_net_changes) > self.max_history:
                self.recent_net_changes.pop(0)