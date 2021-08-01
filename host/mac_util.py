import numpy as np


class NodeLossCounter:
    def __init__(self, window_size=30):
        self.window = window_size
        self.slot = 0
        self.pings = 0
        self.acks = np.zeros(window_size)

    def ping_ok(self):
        if self.pings != 0:
            self.slot += 1
            self.slot %= self.window
        self.acks[self.slot] = 0

        if self.pings < self.window:
            self.pings += 1

    def ack_ok(self):
        self.acks[self.slot] = 1

    def get_loss(self):
        if self.pings == 0:
            loss = 0
        else:
            loss = 100 - int((np.sum(self.acks) / self.pings) * 100)
        return f'{loss} %'
