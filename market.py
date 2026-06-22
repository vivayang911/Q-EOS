import random

from core.config import (
    BLACK_SWAN_PROBABILITY,
    MARKET_RANDOM_MIN,
    MARKET_RANDOM_MAX,
    BLACK_SWAN_MIN,
    BLACK_SWAN_MAX,
    PRESSURE_MULTIPLIER,
    PRESSURE_DECAY
)


class Market:

    def __init__(self, seed=None):
        # 公平对比实验需要固定种子，保证两组实验面对完全相同的市场冲击路径。
        # seed=None 时行为与原版完全一致（不影响 simulation.py / simulation_demo.py 等已有脚本）。
        if seed is not None:
            self._rng = random.Random(seed)
        else:
            self._rng = random

        self.price = 1.0

        self.buy_pressure = 0

        self.sell_pressure = 0

    def apply_buyback(
        self,
        amount
    ):

        pressure = amount / 10000

        self.buy_pressure += pressure

        print(
            f"[Market] Buy Pressure +{pressure:.4f}"
        )

    def apply_sell(
        self,
        amount
    ):

        pressure = amount / 10000

        self.sell_pressure += pressure

        print(
            f"[Market] Sell Pressure -{pressure:.4f}"
        )

    def update(self):

        # 正常市场波动
        random_move = self._rng.uniform(
            MARKET_RANDOM_MIN,
            MARKET_RANDOM_MAX
        )

        # Treasury干预
        pressure_move = (
            self.buy_pressure * PRESSURE_MULTIPLIER
            -
            self.sell_pressure * PRESSURE_MULTIPLIER
        )

        # 黑天鹅事件
        if self._rng.random() < BLACK_SWAN_PROBABILITY:

            shock = self._rng.uniform(
                BLACK_SWAN_MIN,
                BLACK_SWAN_MAX
            )

            self.price += shock

            print(
                f"[Market] Shock={shock:.4f}"
            )

        self.price += (
            random_move
            + pressure_move
        )

        # 压力衰减
        self.buy_pressure *= (
            PRESSURE_DECAY
        )

        self.sell_pressure *= (
            PRESSURE_DECAY
        )

        # 限制价格区间
        self.price = max(
            0.5,
            min(
                1.5,
                self.price
            )
        )

        return round(
            self.price,
            4
        )
