import random
from collections import deque
from itertools import count

import numpy as np
from tqdm import tqdm

from Config import Config
from src.Game import Game
from .Agent import Agent
from .policy import policy


def self_play(
    agents: deque[Agent],
) -> tuple[list[tuple[np.array, np.array, int]], list[Agent]]:
    states = []
    winners = []
    game = Game(n_players=Config.n_players)
    for agent in agents:
        agent.eval()
    id_to_agent = dict(
        (player.id, agent)
        for agent, player in zip(random.sample(agents, Config.n_players), game.players)
    )
    results, winner = _perform_game(game, [], id_to_agent)
    states += results
    winners.append(winner)
    return states, winners


def _perform_game(
    game: Game, states: list, id_to_agent: dict[int, Agent]
) -> tuple[list[tuple[np.array, np.array, int]], Agent]:
    for _ in tqdm(count()):
        agent = id_to_agent[game.current_player.id]
        pi, action = policy(game, agent, Config.c, Config.n_simulations)
        states.append((game, pi / pi.sum(), 0))
        game = game.perform(action)
        if game.is_terminal():
            result = game.get_results()
            return (
                list(
                    (
                        state[0].get_state(),
                        state[1],
                        int(result[state[0].current_player.id] == 1),
                    )
                    for state in states
                ),
                id_to_agent[
                    next(player.id for player in game.players if result[player.id])
                ],
            )
