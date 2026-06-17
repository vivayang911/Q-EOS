import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import os

# 创建输出目录
os.makedirs("output", exist_ok=True)

# =====================
# 1. 加载数据（修正解析逻辑）
# =====================

df = pd.read_csv("output/simulation.csv")

# 打印列名和示例数据（用于调试）
print("列名:", df.columns.tolist())
print("前5行决策列:", df["decision"].head(10).tolist())

# 解析决策列：提取是否拒绝 + 实际执行金额
def parse_decision(row):
    decision = row["decision"]
    action = row["action"]
    
    # 如果 decision 是字符串且包含 "REJECT"，则标记为拒绝
    if isinstance(decision, str) and "REJECT" in decision.upper():
        return "REJECT", 0  # 拒绝时执行金额为 0
    else:
        # 如果是 BUYBACK/SELL 或 "NONE"，提取金额
        if isinstance(decision, str) and "BUYBACK" in decision.upper():
            try:
                amount = float(decision.split()[-1])
                return "APPROVE", amount
            except:
                return "APPROVE", action
        elif isinstance(decision, str) and "SELL" in decision.upper():
            try:
                amount = float(decision.split()[-1])
                return "APPROVE", amount
            except:
                return "APPROVE", action
        else:
            # NO_ACTION 或 NONE
            return "APPROVE", action

# 应用解析
df[["decision_type", "executed_amount"]] = df.apply(
    lambda r: pd.Series(parse_decision(r)), axis=1
)

# 统计拒绝数量
reject_count = (df["decision_type"] == "REJECT").sum()
print(f"拒绝次数: {reject_count} / {len(df)}")

# 计算滚动拒绝率（30天窗口）
df["reject_rolling"] = (
    df["decision_type"] == "REJECT"
).rolling(window=30, min_periods=1).mean() * 100

# =====================
# 2. 创建四合一图表
# =====================

fig = plt.figure(figsize=(16, 12))
fig.suptitle("Q-EOS Governance Analytics Dashboard", fontsize=20, fontweight="bold")

# --- 图1: 治理拒绝率 (左上) ---
ax1 = plt.subplot(2, 2, 1)
ax1.plot(df["day"], df["reject_rolling"], color="crimson", linewidth=2)
ax1.axhline(y=50, color="gray", linestyle="--", alpha=0.5, label="50% threshold")
ax1.set_xlabel("Day")
ax1.set_ylabel("Rejection Rate (%)")
ax1.set_title("1️⃣ Governance Rejection Rate (30-day rolling)")
ax1.set_ylim(0, 100)
ax1.grid(True, alpha=0.3)
ax1.legend()
avg_reject = df["reject_rolling"].mean()
ax1.text(0.02, 0.95, f"Avg Rejection: {avg_reject:.1f}%", 
         transform=ax1.transAxes, fontsize=10, verticalalignment='top')

# --- 图2: AI干预热力图 (右上) ---
ax2 = plt.subplot(2, 2, 2)
colors = df["decision_type"].map({"APPROVE": "blue", "REJECT": "red"})
# 只显示有实际执行金额的点（忽略 amount=0）
valid_mask = df["executed_amount"] != 0
valid_df = df[valid_mask]
scatter = ax2.scatter(
    valid_df["price"], 
    valid_df["executed_amount"], 
    c=valid_df["decision_type"].map({"APPROVE": "blue", "REJECT": "red"}), 
    alpha=0.6, 
    s=20,
    edgecolors='none'
)
ax2.axhline(y=0, color="black", linestyle="-", linewidth=0.8)
ax2.axvline(x=1.0, color="green", linestyle="--", linewidth=1.5, label="Target Price")
ax2.set_xlabel("Market Price")
ax2.set_ylabel("Executed Action (Positive=Buyback, Negative=Sell)")
ax2.set_title("2️⃣ AI Intervention Heatmap (Action vs Price)")
legend_elements = [
    Patch(facecolor='blue', alpha=0.6, label='APPROVED'),
    Patch(facecolor='red', alpha=0.6, label='REJECTED')
]
ax2.legend(handles=legend_elements)
ax2.grid(True, alpha=0.2)
ax2.text(0.02, 0.95, f"Total Interventions: {len(valid_df)}", 
         transform=ax2.transAxes, fontsize=10, verticalalignment='top')

# --- 图3: 国库保护效力 (左下) ---
ax3 = plt.subplot(2, 2, 3)
ax3.fill_between(df["day"], 0, df["balance"], color="forestgreen", alpha=0.3, label="Treasury Balance")
ax3.plot(df["day"], df["balance"], color="darkgreen", linewidth=2)
ax3.axhline(y=10000, color="orange", linestyle="--", linewidth=2, label="Hard Constraint Floor (10,000)")
ax3.axhline(y=50000, color="blue", linestyle=":", linewidth=1.5, alpha=0.7, label="Initial Balance (50,000)")
# 标记拒绝事件
reject_days = df[df["decision_type"] == "REJECT"]["day"]
reject_balances = df[df["decision_type"] == "REJECT"]["balance"]
if len(reject_days) > 0:
    ax3.scatter(reject_days, reject_balances, color="red", s=30, marker="x", label="REJECT Events", zorder=5)
ax3.set_xlabel("Day")
ax3.set_ylabel("Treasury Balance (USDC)")
ax3.set_title("3️⃣ Treasury Protection Effectiveness")
ax3.legend(loc="upper right")
ax3.grid(True, alpha=0.3)
ax3.text(0.02, 0.05, f"Final Balance: {df['balance'].iloc[-1]:.0f} USDC", 
         transform=ax3.transAxes, fontsize=10, verticalalignment='bottom')

# --- 图4: 稳定性评分 (右下) ---
ax4 = plt.subplot(2, 2, 4)
price_std = df["price"].std()
price_mean = df["price"].mean()
volatility_score = max(0, min(100, 100 - (price_std / 0.05) * 80))

initial_balance = 50000
final_balance = df["balance"].iloc[-1]
treasury_score = min(100, (final_balance / initial_balance) * 100)

reject_rate = avg_reject
if 20 <= reject_rate <= 60:
    governance_score = 100
elif reject_rate < 20:
    governance_score = 50 + (reject_rate / 20) * 50
else:
    governance_score = max(0, 100 - (reject_rate - 60) / 40 * 100)

max_drawdown = (df["balance"].max() - df["balance"].min()) / initial_balance * 100
drawdown_score = max(0, 100 - max_drawdown * 1.2)

stability_score = (volatility_score * 0.35 + 
                   treasury_score * 0.30 + 
                   governance_score * 0.20 + 
                   drawdown_score * 0.15)

categories = ["Price Volatility", "Treasury Health", "Governance Efficiency", "Drawdown Control"]
scores = [volatility_score, treasury_score, governance_score, drawdown_score]
colors = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c"]

bars = ax4.barh(categories, scores, color=colors, alpha=0.7)
ax4.set_xlim(0, 110)
ax4.set_xlabel("Score (0-100)")
ax4.set_title("4️⃣ Q-EOS Stability Score")
ax4.grid(True, alpha=0.2, axis='x')

for bar, score in zip(bars, scores):
    ax4.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f"{score:.1f}", 
             va='center', fontsize=10, fontweight='bold')

ax4.text(0.6, 0.95, f"OVERALL: {stability_score:.1f}", 
         transform=ax4.transAxes, fontsize=16, fontweight='bold', color="darkblue",
         bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray', boxstyle='round,pad=0.5'))

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("output/governance_analysis.png", dpi=200, bbox_inches="tight")
print("✅ 分析图表已生成：output/governance_analysis.png")

# =====================
# 4. 终端输出评分摘要
# =====================

print("\n" + "="*50)
print("📊 Q-EOS Governance Analytics Report")
print("="*50)
print(f"📈 Price Volatility (Std):    {price_std:.4f}  -> Score: {volatility_score:.1f}")
print(f"🏦 Treasury Health (Final):   {final_balance:.0f}  -> Score: {treasury_score:.1f}")
print(f"⚖️  Governance Efficiency:      Reject Rate {reject_rate:.1f}% -> Score: {governance_score:.1f}")
print(f"🛡️  Max Drawdown:               {max_drawdown:.1f}%  -> Score: {drawdown_score:.1f}")
print("-"*50)
print(f"🏆 OVERALL STABILITY SCORE:    {stability_score:.1f} / 100")
print("="*50)