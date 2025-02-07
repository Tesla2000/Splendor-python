from itertools import pairwise, starmap
from typing import Optional

import pytorch_lightning as pl
import torch
from torch import nn, Tensor

from Config import Config


class Agent(pl.LightningModule):
    device = Config.device
    _input_size_dictionary = {
        2: 256,
    }

    def __init__(
        self,
        n_players: int = Config.n_players,
        hidden_size: tuple = Config.hidden_size,
        n_moves: int = Config.n_actions,
        loss_fn: Optional[nn.Module] = None
    ):
        super().__init__()
        self.tanh = nn.Tanh()
        self.softmax = nn.Softmax(dim=1)
        first_size = self._get_size(n_players)
        self.hidden_sizes = hidden_size
        sizes = first_size, *hidden_size
        self.layers = nn.ModuleList(starmap(nn.Linear, pairwise(sizes)))
        self.fc_p = nn.Linear(sizes[-1], n_moves)
        self._n_moves = n_moves
        self.relu = nn.LeakyReLU()
        if loss_fn is None:
            loss_fn = nn.MSELoss()
        self.loss_fn = loss_fn
        self.optimizer = None

    def _get_size(self, n_players: int) -> int:
        return self._input_size_dictionary[n_players]

    def forward(self, state: Tensor):
        for layer in self.layers:
            state = layer(state)
            state = self.relu(state)
        return self.fc_p(state)

    def configure_optimizers(self):
        if self.optimizer is None:
            self.optimizer = torch.optim.Adam(
                self.parameters(),
                lr=Config.initial_train_learning_rate)
        scheduler = torch.optim.lr_scheduler.ExponentialLR(
            self.optimizer, gamma=.1 ** (1 / Config.lr_decline_rate)
        )
        return [self.optimizer], [
            {"scheduler": scheduler, "interval": "epoch"}]

    def lr_scheduler_step(self, scheduler, metric):
        scheduler.step(metric)

    def training_step(self, batch, batch_idx):
        state, moves_till_end, move_indexes = batch
        outputs = self(state)
        loss = sum(self.loss_fn(output[move_index], move_till_end.float()) for
                   move_index, move_till_end, output in
                   zip(move_indexes, moves_till_end, outputs))
        return {"loss": loss}
