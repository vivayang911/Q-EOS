import os
import csv
import time

from core.bus import MessageBus
from agents.observer import ObserverAgent
from agents.risk import RiskAgent
from agents.pid import PIDAgent
from agents.treasury import TreasuryAgent
from agents.governor import GovernorAgent
from market import Market
from logger import DecisionLog


# =====================
# 配置：30天 Qwen 演示模式
# =====================
USE_QWEN = True          # 启用 Qwen 真实决策
SIM_DAYS = 30            # 30天演示
# =====================


print("=" * 60)
print("🎬 Q-EOS 演示模式（30天 Qwen 治理）")
print("=" * 60)
print(f"📌 模拟天数: {SIM_DAYS} 天")
print(f"🧠 Qwen 决策: {'启用' if USE_QWEN else '禁用'}")
print("=" * 60)


# =====================
# 初始化
# =====================

bus = MessageBus()
market = Market()
logger = DecisionLog()

# 创建 Agent
treasury = TreasuryAgent(bus, market)
observer = ObserverAgent(bus, market)
risk = RiskAgent(bus)
pid = PIDAgent(bus, treasury)
governor = GovernorAgent(bus, logger, use_qwen=USE_QWEN)


# =====================
# 创建输出目录
# =====================

os.makedirs("output", exist_ok=True)


# =====================
# 仿真
# =====================

with open("output/simulation_demo.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["day", "price", "action", "balance", "decision"])

    for day in range(1, SIM_DAYS + 1):
        print(f"\n{'='*20} DAY {day:2d} {'='*20}")

        observer.step()
        risk.step()
        pid.step()
        governor.step()   # Qwen 决策
        treasury.step()   # 执行

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

        # 模拟调用 Qwen 时的真实延迟，让演示更自然（可选）
        time.sleep(0.5)


print("\n" + "=" * 60)
print("✅ 30天演示模拟完成")
print(f"📊 数据已保存: output/simulation_demo.csv")
print("=" * 60)