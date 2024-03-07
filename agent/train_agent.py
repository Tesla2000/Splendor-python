from collections import deque

import numpy as np
from torch import nn, optim
from torch.utils.data import DataLoader

from Config import Config
from .Agent import Agent
from .RLDataset import RLDataset


def train_agent(agent: Agent, train_data: deque[tuple[tuple, np.array, int]]):
    agent.train()
    categorical_cross_entropy = nn.CrossEntropyLoss()
    binary_cross_entropy = nn.BCELoss()
    optimizer = optim.Adam(agent.parameters())
    dataset = RLDataset(train_data)
    loader = DataLoader(dataset, batch_size=Config.train_batch_size)
    for batch in loader:
        state, policy, win_probability = batch
        state, policy, win_probability = state.float(), policy.float(), win_probability.float()
        optimizer.zero_grad()
        output_policy, output_v = agent(state)
        bce = binary_cross_entropy((output_v + 1) / 2, win_probability)
        cce = categorical_cross_entropy(output_policy, policy)
        bce.backward(retain_graph=True)
        cce.backward()
        optimizer.step()
