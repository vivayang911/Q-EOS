class DecisionLog:

    def __init__(self):

        self.records = []

    def add(
        self,
        text
    ):

        self.records.append(
            text
        )

    def show(self):

        print("\n===== LOG =====")

        for item in self.records:

            print(item)