import pandas as pd
import matplotlib.pyplot as plt

baseline = pd.read_csv(
    "output/baseline.csv"
)

controlled = pd.read_csv(
    "output/simulation.csv"
)

baseline_std = baseline["price"].std()
controlled_std = controlled["price"].std()

# ====== 关键：输出到终端 ======
print("\n===== VOLATILITY REPORT =====")
print(f"Baseline Std = {baseline_std:.6f}")
print(f"Q-EOS Std    = {controlled_std:.6f}")

reduction = (
    (baseline_std - controlled_std)
    / baseline_std
    * 100
)

print(
    f"Volatility Reduction = {reduction:.2f}%"
)

# ====== 画图 ======
labels = [
    "Without AI Governance",
    "Qwen Governor + PID"
]

values = [
    baseline_std,
    controlled_std
]

plt.figure(figsize=(8,6))

bars = plt.bar(labels, values)

plt.ylabel("Price Volatility (Std Dev)")
plt.title("Volatility Reduction by AI Governance")

for bar in bars:
    y = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        y,
        f"{y:.3f}",
        ha="center"
    )

plt.savefig(
    "output/stability_comparison.png",
    dpi=300
)

plt.show()