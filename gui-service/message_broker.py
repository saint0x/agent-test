class MessageBroker:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, subscriber):
        self.subscribers.append(subscriber)

    def publish(self, message):
        for subscriber in self.subscribers:
            subscriber.notify(message)

    def notify_subscribers(self, report):
        message = f"New report generated: {report}"
        self.publish(message)

    def notify_all(self):
        for subscriber in self.subscribers:
            subscriber.notify("All subscribers notified.")
