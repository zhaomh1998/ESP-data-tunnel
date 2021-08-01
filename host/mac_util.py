import time

import numpy as np


class _NodeLossCounter:
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


class _NodeState:
    STATE_IDLE = 0
    STATE_ACTIVE = 1
    STATE_CONFIG_WAIT_ACK = 2

    def __init__(self):
        self.state = self.STATE_IDLE

    def __str__(self):
        if self.state == self.STATE_IDLE:
            return 'Idle'
        elif self.state == self.STATE_ACTIVE:
            return 'Active'
        elif self.state == self.STATE_CONFIG_WAIT_ACK:
            return 'Wait ACK_CFG'
        else:
            raise RuntimeError(f'Invalid state {self.state}')


class Node:
    def __init__(self, node_id, addr):
        self.node_id = node_id
        self.addr = addr
        self.loss_cntr = _NodeLossCounter()
        self.state = _NodeState()
        self.last_active = time.time()
