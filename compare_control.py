import random
import pandas as pd
import matplotlib.pyplot as plt


days = 365

# 无控制
price = 1.0
no_control = []

for _ in range(days):

    price += random.uniform(
        -0.05,
        0.05
    )

    price = max(
        0.5,
        min(1.5, price)
    )

    no_control.append(price)


# PID控制结果
df = pd.read_csv(
    "output/simulation.csv"
)

pid_control = df["price"]


plt.figure(figsize=(12,6))

plt.plot(
    no_control,
    label="No Control"
)

plt.plot(
    pid_control,
    label="PID Control"
)

plt.axhline(
    y=1.0,
    linestyle="--",
    label="Target"
)

plt.title(
    "Price Stability Comparison"
)

plt.xlabel("Day")
plt.ylabel("Price")

plt.legend()

plt.savefig(
    "output/compare.png"
)

print(
    "compare.png generated"
)
import numpy as np

no_std = np.std(no_control)
pid_std = np.std(pid_control)

print(f"No Control Volatility: {no_std:.4f}")
print(f"PID Control Volatility: {pid_std:.4f}")

improvement = (
    (no_std - pid_std)
    / no_std
    * 100
)

print(
    f"Volatility Reduction: "
    f"{improvement:.2f}%"
)