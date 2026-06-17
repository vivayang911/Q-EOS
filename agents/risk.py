from core.message import Message

class RiskAgent:

    def __init__(self, bus):
        self.bus = bus

    def step(self):
        msgs = self.bus.get_for("Risk")
        for msg in msgs:
            price = msg.payload["price"]
            risk_score = 80 if price < 0.97 else 20
            print(f"[Risk] Risk Score={risk_score}")
            self.bus.send(
                Message(
                    "Risk",
                    "PID",
                    "RISK_RESULT",
                    {"price": price, "risk_score": risk_score}
                )
            )