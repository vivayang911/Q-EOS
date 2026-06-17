import random
import csv
import os

os.makedirs("output", exist_ok=True)

days = 365
price = 1.0
prices = []

for _ in range(days):
    price += random.uniform(-0.05, 0.05)
    price = max(0.5, min(1.5, price))
    prices.append(price)

with open("output/comparison.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["day", "no_pid_price"])
    for i, p in enumerate(prices, start=1):
        writer.writerow([i, p])

print("comparison.csv generated")