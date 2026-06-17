import os
import csv

from market import Market

os.makedirs(
    "output",
    exist_ok=True
)

market = Market()

with open(
    "output/baseline.csv",
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "day",
            "price"
        ]
    )

    for day in range(
        1,
        366
    ):

        price = market.update()

        writer.writerow(
            [
                day,
                price
            ]
        )

print(
    "baseline saved"
)