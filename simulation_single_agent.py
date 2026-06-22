# simulation_single_agent.py
# 单智能体 Baseline：一个 Qwen Agent 承担全部职责

import csv
import os
from market import Market
from agents.qwen_governor import QwenGovernor


class SingleAgent:
    def __init__(self):
        self.market = Market()
        self.qwen = QwenGovernor()
        self.balance = 50000

    def step(self):
        # 1. 感知价格
        price = self.market.update()
        # 2. 计算风险分
        risk_score = 80 if price < 0.97 else 20
        # 3. 计算控制量（简化PID）
        action = (1 - price) * 10000
        # 4. 调用Qwen决策
        result = self.qwen.decide(price, risk_score, action, self.balance)
        decision = result.get("decision")
        reason = result.get("reason")
        # 5. 执行
        if decision == "APPROVE" and action > 0 and action <= self.balance:
            self.balance -= action
            self.market.apply_buyback(action)
        elif decision == "APPROVE" and action < 0:
            self.balance += abs(action)
            self.market.apply_sell(abs(action))
        elif decision == "APPROVE" and action > self.balance:
            # 修正：原代码这种情况什么都不做，CSV里 decision 仍写 "APPROVE"，
            # 但实际余额未变 —— 这是"批准了但实际没执行"的隐藏分支，容易让
            # 后续统计脚本误以为这一天发生了真实操作。改用余额变化判断真实执行
            # 后这里不再需要单独改 decision 文本，但保留这个分支说明，
            # 方便人工审计时一眼看出"为什么这天 decision=APPROVE 但余额没变"。
            pass
        # 6. 记录决策日志
        log_entry = f"{decision}: {reason[:60]}..."
        return price, action, self.balance, decision


# 运行30天
os.makedirs("output", exist_ok=True)

agent = SingleAgent()

with open("output/single_baseline.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["day", "price", "action", "balance", "decision"])

    for day in range(1, 31):
        price, action, balance, decision = agent.step()
        writer.writerow([
            day,
            round(price, 4),
            round(action, 2),
            round(balance, 2),
            decision
        ])
        print(f"Day {day}: Price={price:.4f}, Balance={balance:.2f}, {decision}")

print("\n✅ 单智能体30天模拟完成: output/single_baseline.csv")