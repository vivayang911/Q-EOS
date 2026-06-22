
from core.message import Message


class PolicyAgent:

    def __init__(self, bus):

        self.bus = bus

    def step(self):

        msgs = self.bus.get_for(
            "Policy"
        )

        for msg in msgs:

            price = msg.payload[
                "price"
            ]

            action = msg.payload[
                "action"
            ]

            risk_score = msg.payload[
                "risk_score"
            ]

            balance = msg.payload[
                "balance"
            ]

            deviation = abs(
                price - 1.0
            )

            # =====================
            # Dynamic Policy Layer
            # =====================

            if deviation < 0.01:

                multiplier = 0.5

            elif deviation < 0.05:

                multiplier = 1.0

            else:

                multiplier = 1.5

            # Risk Adjustment

            if risk_score >= 80:

                multiplier *= 0.5

            elif risk_score >= 50:

                multiplier *= 0.8

            # Treasury Protection

            if balance < 30000:

                multiplier *= 0.8

            if balance < 20000:

                multiplier *= 0.6

            if balance < 15000:

                multiplier *= 0.4

            final_action = (
                action * multiplier
            )

            print(
                f"[Policy] "
                f"Multiplier={multiplier:.2f}"
            )

            print(
                f"[Policy] "
                f"Final Action="
                f"{final_action:.2f}"
            )

            self.bus.send(
                Message(
                    "Policy",
                    "Governor",
                    "PROPOSAL",
                    {
                        "price": price,
                        "action": final_action,
                        "risk_score": risk_score,
                        "balance": balance
                    }
                )
            )





