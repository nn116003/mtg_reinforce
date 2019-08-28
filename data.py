# state phase?
import numpy as np
import torch
import torch.nn.functional as F
import random



class ReplayController(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, transition):
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = self.feature2tensor(transition)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def feature2tensor(self, feature):
        pass

    def __len__(self):
        return len(self.memory)