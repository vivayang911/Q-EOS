import os
import csv
import time
from core.bus import MessageBus
from agents.observer import ObserverAgent
from agents.risk import RiskAgent
from agents.pid import PIDAgent
from agents.policy import PolicyAgent
from agents.treasury import TreasuryAgent
from agents.governor import GovernorAgent
from market import Market
from logger import DecisionLog
from core.message import Message

USE_QWEN = True
SIM_DAYS = 365
MARKET_SEED = 105  # 固定种子，确保结果可复现。
                   # 候选筛选标准：价格曾跌至0.87附近(明显depeg,会触发Risk Agent高风险评分
                   # 和Treasury硬约束的关注)，但未触底到0.5-0.6的崩盘级别，
                   # 同时有约146天处于<0.95的中度偏离区间，能持续给系统施压，
                   # 让Qwen有充分机会展现"该批准时批准、该拒绝时拒绝"的真实治理能力，
                   # 而不是像seed=42那样全程温和、365天0次REJECT，
                   # 也不是像某些种子那样直接崩到国库瘫痪、长期100%REJECT。

print("📊 Q-EOS 365天模拟")
print("=" * 60)

bus = MessageBus()
market = Market(seed=MARKET_SEED)
logger = DecisionLog()

treasury = TreasuryAgent(bus, market)
observer = ObserverAgent(bus, market)
risk = RiskAgent(bus)
pid = PIDAgent(bus, treasury)
policy = PolicyAgent(bus)
governor = GovernorAgent(bus, logger, use_qwen=USE_QWEN)

os.makedirs("output", exist_ok=True)

with open("output/simulation.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["day", "price", "action", "balance", "decision"])

    for day in range(1, SIM_DAYS + 1):
        print(f"\n==================== DAY {day:3d}/{SIM_DAYS} ====================")

        observer.step()
        risk.step()
        pid.step()
        policy.step()
        governor.step()
        treasury.step()

        price = market.price
        balance = treasury.balance
        action = 0
        decision = "NONE"

        if len(logger.records) > 0:
            last_record = logger.records[-1]
            # 修正：Logger 升级后 records 里存的是字典 {"text": ..., "day": ..., ...}
            # 而不是原来的纯字符串，这里取出 "text" 字段还原成原来的字符串行为，
            # 兼容旧版 records 仍是字符串的情况（双重保险，避免再次因为格式假设出错）。
            if isinstance(last_record, dict):
                decision = last_record.get("text", "NONE")
            else:
                decision = last_record
            try:
                if decision.startswith("BUYBACK") or decision.startswith("SELL"):
                    action = float(decision.split()[-1])
            except:
                action = 0

        writer.writerow([day, round(price, 4), round(action, 2), round(balance, 2), decision])

print("✅ 365天模拟完成: output/simulation.csv")
