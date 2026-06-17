import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("output/simulation.csv")

plt.figure(figsize=(10, 5))

plt.plot(
    df["day"],
    df["price"],
    label="PID Controlled"
)

plt.axhline(
    y=1.0,
    linestyle="--",
    label="Target Price"
)

plt.title("Q-EOS Price Stabilization")
plt.xlabel("Day")
plt.ylabel("Price")
plt.legend()

plt.savefig("output/price_curve.png")

print("price_curve.png generated")