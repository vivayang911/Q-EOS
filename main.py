from core.bus import MessageBus

from agents.observer import ObserverAgent
from agents.risk import RiskAgent
from agents.pid import PIDAgent
from agents.policy import PolicyAgent
from agents.treasury import TreasuryAgent
from agents.governor import GovernorAgent

from market import Market
from logger import DecisionLog


# =====================
# Init
# =====================

bus = MessageBus()

market = Market()

logger = DecisionLog()


# Treasury必须先创建
treasury = TreasuryAgent(
    bus,
    market
)

observer = ObserverAgent(
    bus,
    market
)

risk = RiskAgent(
    bus
)

# PID获得Treasury引用
pid = PIDAgent(
    bus,
    treasury
)

# Policy层：动态调整干预强度（PID → Policy → Governor）
policy = PolicyAgent(
    bus
)

governor = GovernorAgent(
    bus,
    logger
)


# =====================
# Simulation
# =====================

for day in range(1, 366):

    print(
        f"\n===== DAY {day} ====="
    )

    observer.step()

    risk.step()

    pid.step()

    policy.step()

    governor.step()

    treasury.step()


print(
    "\n365-day simulation completed"
)
