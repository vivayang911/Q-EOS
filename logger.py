import csv


class DecisionLog:

    def __init__(self):

        self.records = []

    def add(
        self,
        text,
        day=None,
        price=None,
        action=None,
        balance=None,
        decision=None,
    ):
        """
        升级说明：原版只存一行文本(text)，无法直接导出结构化数据
        （CSV/图表/统计报告都需要逐字段访问）。
        现在同时保留 text（向后兼容旧的 show() 打印行为）和结构化字段。
        调用方如果暂时不传 day/price/action/balance/decision 也不会报错，
        只是导出 CSV 时对应列会是空值——不会破坏现有调用 self.log.add(text) 的代码。
        """
        self.records.append({
            "text": text,
            "day": day,
            "price": price,
            "action": action,
            "balance": balance,
            "decision": decision,
        })

    def show(self):

        print("\n===== LOG =====")

        for item in self.records:

            print(item["text"])

    def export_csv(self, path="output/decision_log.csv"):
        """
        将结构化记录导出为 CSV，供后续图表生成、统计报告、GitHub展示使用。
        只导出曾经被赋值过（非 None）的记录；如果调用方从未传过结构化字段
        （仍在用旧的 self.log.add(text) 调用方式），则只导出 text 列。
        """
        if not self.records:
            print("[DecisionLog] No records to export.")
            return

        has_structured_data = any(
            r["day"] is not None for r in self.records
        )

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if has_structured_data:
                writer.writerow(["day", "price", "action", "balance", "decision", "text"])
                for r in self.records:
                    writer.writerow([
                        r["day"], r["price"], r["action"], r["balance"], r["decision"], r["text"]
                    ])
            else:
                writer.writerow(["text"])
                for r in self.records:
                    writer.writerow([r["text"]])

        print(f"[DecisionLog] Exported {len(self.records)} records to {path}")
            print(item)
