# compare_baseline.py
# Three-way comparison: Single Agent (Simple) vs Single Agent + PID vs Q-EOS Multi-Agent

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("output", exist_ok=True)
os.makedirs("docs", exist_ok=True)

# Load data
single = pd.read_csv("output/single_baseline.csv")
single_pid = pd.read_csv("output/single_pid_baseline.csv")
multi = pd.read_csv("output/simulation_demo.csv")


def calc_metrics(df):
    # 修正说明：原版用 (action != 0) 判断"是否执行"，但 action 是 PID/线性公式
    # 算出的"提案值"，即便 Governor 最终 REJECT，action 列依然会写入非零数字，
    # 导致"提案率"被误判成"执行率"。
    #
    # 三组数据的 decision 列文本格式互不相同：
    #   Single Agent: "APPROVE: 理由文本..."
    #   Single+PID:   "REJECT"
    #   Multi-Agent:  "BUYBACK 7.63" / "SELL 46.31"（不含APPROVE/REJECT字样）
    # 用文本匹配规则适配三种格式容易遗漏，改用"余额是否真实发生变化"作为
    # 唯一判断标准，这对任何 decision 文本格式都成立。
    balances = [50000.0] + df["balance"].tolist()
    executed_mask = pd.Series([
        abs(balances[i + 1] - balances[i]) > 1e-6
        for i in range(len(df))
    ])

    peak = df["balance"].cummax()
    drawdown_series = (peak - df["balance"]) / peak * 100

    return {
        "final_balance": df["balance"].iloc[-1],
        "execution_rate": executed_mask.sum() / len(df) * 100,
        "drawdown": drawdown_series.max(),
        "executions": int(executed_mask.sum()),
        "proposal_rate": (df["action"] != 0).sum() / len(df) * 100,  # 提案率，区别于真实执行率
    }


m1 = calc_metrics(single)
m2 = calc_metrics(single_pid)
m3 = calc_metrics(multi)

print("\n" + "=" * 60)
print("📊 Three-Way Comparison: Single Agent vs Q-EOS")
print("=" * 60)
print(f"{'Metric':<25} {'Single Agent':>15} {'Single+PID':>15} {'Q-EOS':>15}")
print("-" * 75)
print(f"{'Final Treasury (USDC)':<25} {m1['final_balance']:>15.0f} {m2['final_balance']:>15.0f} {m3['final_balance']:>15.0f}")
print(f"{'Execution Rate (%)':<25} {m1['execution_rate']:>15.1f} {m2['execution_rate']:>15.1f} {m3['execution_rate']:>15.1f}")
print(f"{'Proposal Rate (%)':<25} {m1['proposal_rate']:>15.1f} {m2['proposal_rate']:>15.1f} {m3['proposal_rate']:>15.1f}")
print(f"{'Max Drawdown (%)':<25} {m1['drawdown']:>15.1f} {m2['drawdown']:>15.1f} {m3['drawdown']:>15.1f}")
print(f"{'Total Executions':<25} {m1['executions']:>15} {m2['executions']:>15} {m3['executions']:>15}")
print("=" * 60)

# Generate three-bar comparison chart
metrics = ['Treasury\n(USDC)', 'Execution\nRate (%)', 'Max\nDrawdown (%)']
single_values = [m1['final_balance'], m1['execution_rate'], m1['drawdown']]
single_pid_values = [m2['final_balance'], m2['execution_rate'], m2['drawdown']]
multi_values = [m3['final_balance'], m3['execution_rate'], m3['drawdown']]

x = np.arange(len(metrics))
width = 0.25

fig, ax = plt.subplots(figsize=(10, 6))

bars1 = ax.bar(x - width, single_values, width, label='Single Agent', color='#e74c3c', alpha=0.7)
bars2 = ax.bar(x, single_pid_values, width, label='Single + PID', color='#f39c12', alpha=0.7)
bars3 = ax.bar(x + width, multi_values, width, label='Q-EOS Multi-Agent', color='#2ecc71', alpha=0.7)

ax.set_ylabel('Value')
ax.set_title('Three-Way Comparison: Single Agent vs Single+PID vs Multi-Agent')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.legend()
ax.grid(True, alpha=0.3)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)
for bar in bars3:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
             f'{bar.get_height():.1f}', ha='center', va='bottom', fontsize=8)

plt.tight_layout()
plt.savefig('docs/baseline_comparison.png', dpi=150)
plt.savefig('output/baseline_comparison.png', dpi=150)

print("\n✅ Chart saved: docs/baseline_comparison.png")
print("✅ Chart saved: output/baseline_comparison.png")