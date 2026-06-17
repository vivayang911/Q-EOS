import csv

from core.bus import MessageBus
from agents.observer import ObserverAgent
from agents.risk import RiskAgent
from agents.pid import PIDAgent
from agents.treasury import TreasuryAgent
from market import Market

bus = MessageBus()
market = Market()

observer = ObserverAgent(bus, market)
risk = RiskAgent(bus)

treasury = TreasuryAgent(bus, market)

# ✅ 修复：PID 需要 treasury
pid = PIDAgent(bus, treasury)

with open("output/baseline.csv", "w", newline="") as f:

    writer = csv.writer(f)
    writer.writerow(["day", "price", "balance"])

    for day in range(1, 366):

        observer.step()
        risk.step()
        pid.step()
        treasury.step()

        writer.writerow([
            day,
            market.price,
            treasury.balance
        ])

print("baseline simulation done")