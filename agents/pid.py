from core.message import Message
from core.pid_controller import PIDController


class PIDAgent:

    def __init__(self, bus, treasury):

        self.bus = bus
        self.treasury = treasury

        self.pid = PIDController(
            kp=3000,
            ki=50,
            kd=500
        )

    def step(self):

        msgs = self.bus.get_for(
            "PID"
        )

        for msg in msgs:

            price = msg.payload["price"]

            risk_score = msg.payload["risk_score"]

            action = self.pid.calculate(
                target=1.0,
                current=price
            )

            print(
                f"[PID] "
                f"Price={price} "
                f"Action={action:.2f}"
            )

            # 🔥 关键升级：真实 treasury balance
            balance = self.treasury.balance

            self.bus.send(
                Message(
                    "PID",
                    "Governor",
                    "PROPOSAL",
                    {
                        "price": price,
                        "action": action,
                        "risk_score": risk_score,
                        "balance": balance   # ⭐关键修复点
                    }
                )
            )