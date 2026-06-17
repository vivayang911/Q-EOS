import os
import csv

from core.bus import MessageBus
from agents.observer import ObserverAgent
from agents.risk import RiskAgent
from agents.pid import PIDAgent
from agents.treasury import TreasuryAgent
from agents.governor import GovernorAgent
from market import Market
from logger import DecisionLog


# =====================
# 初始化
# =====================

bus = MessageBus()
market = Market()
logger = DecisionLog()

# ⚠️ 重要：Treasury 必须先创建（因为 PID 和 Governor 需要引用它）
treasury = TreasuryAgent(bus, market)

observer = ObserverAgent(bus, market)
risk = RiskAgent(bus)

# ✅ PID 需要传入 treasury 引用
pid = PIDAgent(bus, treasury)

# ✅ Governor 可以传入 use_qwen=False（快速模拟模式）
governor = GovernorAgent(bus, logger, use_qwen=False)


# =====================
# 创建输出目录
# =====================

os.makedirs("output", exist_ok=True)


# =====================
# 仿真
# =====================

with open("output/simulation.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["day", "price", "action", "balance", "decision"])

    for day in range(1, 366):
        if day % 10 == 0:
            print(f"Running Day {day}/365")

        # ✅ 正确的 Agent 调用顺序
        observer.step()
        risk.step()
        pid.step()
        governor.step()   # Governor 先决策，发送 approved 字段
        treasury.step()   # Treasury 检查 approved 后再执行

        # 记录数据
        price = market.price
        balance = treasury.balance
        action = 0
        decision = "NONE"

        if len(logger.records) > 0:
            decision = logger.records[-1]
            try:
                if decision.startswith("BUYBACK") or decision.startswith("SELL"):
                    action = float(decision.split()[-1])
            except:
                action = 0

        writer.writerow([
            day,
            round(price, 4),
            round(action, 2),
            round(balance, 2),
            decision
        ])


print("\n365-day simulation completed")
print("CSV saved: output/simulation.csv")