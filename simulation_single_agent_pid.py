# simulation_single_agent_pid.py
# 公平版单Agent Baseline：使用真实PID控制器（与多Agent版本相同的Kp/Ki/Kd）

import csv
import os
from market import Market
from core.pid_controller import PIDController
from agents.qwen_governor import QwenGovernor

class SingleAgentWithPID:
    def __init__(self):
        self.market = Market()
        # 使用与多Agent版本完全相同的PID参数
        self.pid = PIDController(kp=3000, ki=50, kd=500)
        self.qwen = QwenGovernor()
        self.balance = 50000
        self.integral = 0
        self.prev_error = 0

    def step(self):
        # 1. 感知价格
        price = self.market.update()
        
        # 2. 风险评估（与多Agent版本RiskAgent保持一致）
        risk_score = 80 if price < 0.97 else 20
        
        # 3. 使用真实PID算法计算action（与多Agent版本完全一致）
        action = self.pid.calculate(target=1.0, current=price)
        
        # 4. Qwen决策（与多Agent版本完全一致）
        result = self.qwen.decide(price, risk_score, action, self.balance)
        decision = result.get("decision")
        reason = result.get("reason")
        
        # 5. 执行
        if decision == "APPROVE":
            if action > 0 and action <= self.balance:
                self.balance -= action
                self.market.apply_buyback(action)
            elif action < 0:
                self.balance += abs(action)
                self.market.apply_sell(abs(action))
            # action == 0 时不执行任何操作
        
        return price, action, self.balance, decision

# 运行30天
os.makedirs("output", exist_ok=True)

agent = SingleAgentWithPID()

with open("output/single_pid_baseline.csv", "w", newline="", encoding="utf-8") as f:
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
        print(f"Day {day:2d}: Price={price:.4f}, Action={action:.2f}, Balance={balance:.2f}, {decision}")

print("\n✅ 公平版单Agent（含PID）30天模拟完成: output/single_pid_baseline.csv")