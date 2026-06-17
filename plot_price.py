import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("output", exist_ok=True)

# =====================
# Load data
# =====================

qwen = pd.read_csv("output/simulation.csv")
baseline = pd.read_csv("output/baseline.csv")

# =====================
# 1. Price Curve
# =====================

plt.figure(figsize=(10, 5))

plt.plot(qwen["day"], qwen["price"], label="Qwen Controlled", linewidth=2)
plt.plot(baseline["day"], baseline["price"], label="No AI (Baseline)", linestyle="--")

plt.axhline(1.0, linestyle=":", color="gray")

plt.title("Price Stability Comparison")
plt.xlabel("Day")
plt.ylabel("Price")

plt.legend()
plt.tight_layout()

plt.savefig("output/price_curve.png")

plt.close()

# =====================
# 2. Treasury Curve（关键修复点）
# =====================

plt.figure(figsize=(10, 5))

plt.plot(qwen["day"], qwen["balance"], label="Qwen Treasury", linewidth=2)
plt.plot(baseline["day"], baseline["balance"], label="Baseline Treasury", linestyle="--")

plt.title("Treasury Stability Comparison")
plt.xlabel("Day")
plt.ylabel("Balance")

plt.legend()
plt.tight_layout()

plt.savefig("output/treasury_curve.png")

plt.close()

print("✅ All plots generated:")
print("- output/price_curve.png")
print("- output/treasury_curve.png")