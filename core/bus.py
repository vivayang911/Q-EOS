class MessageBus:

    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)

    def get_for(self, receiver):
        result = []
        for msg in self.messages:
            if msg.receiver == receiver:
                result.append(msg)

        self.messages = [
            msg
            for msg in self.messages
            if msg.receiver != receiver
        ]

        return result