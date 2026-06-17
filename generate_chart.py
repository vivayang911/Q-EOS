import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs('project_assets', exist_ok=True)

# 读取数据
df_pid = pd.read_csv('output/simulation.csv')   # 有PID控制的价格列 'price'
df_no = pd.read_csv('output/comparison.csv')    # 无PID控制的价格列 'no_pid_price'

# 统一长度（取较短的数据集长度）
min_len = min(len(df_pid), len(df_no))
days = df_pid['day'][:min_len]
price_pid = df_pid['price'][:min_len]
price_no = df_no['no_pid_price'][:min_len]

# 绘图
plt.figure(figsize=(12, 5))
plt.plot(days, price_pid, label='With PID Control', linewidth=2, color='blue')
plt.plot(days, price_no, label='Without PID Control', linewidth=2, color='red', alpha=0.7)
plt.xlabel('Day')
plt.ylabel('Price (Target = 1.0)')
plt.title('PID Control vs. No Control: Price Stability Comparison')
plt.legend()
plt.grid(True, alpha=0.3)
plt.axhline(y=1.0, color='green', linestyle='--', label='Target Price')
plt.savefig('project_assets/pid_comparison.png', dpi=150, bbox_inches='tight')
print("✅ 图片已生成：project_assets/pid_comparison.png")