from core.message import Message

class ObserverAgent:

    def __init__(
        self,
        bus,
        market
    ):

        self.bus = bus
        self.market = market

    def step(self):

        price = self.market.update()

        print(
            f"[Observer] Price={price}"
        )

        self.bus.send(
            Message(
                "Observer",
                "Risk",
                "PRICE_UPDATE",
                {
                    "price": price
                }
            )
        )