from itertools import chain
from typing import Iterable, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from .Game import Game


class StateExtractor:
    @classmethod
    def get_state(cls, game: "Game") -> tuple:
        return tuple(
            chain.from_iterable(
                (
                    chain.from_iterable(
                        (
                            card.cost.red,
                            card.cost.green,
                            card.cost.blue,
                            card.cost.black,
                            card.cost.white,
                            card.production.red,
                            card.production.green,
                            card.production.blue,
                            card.production.black,
                            card.production.white,
                            card.points,
                        )
                        for tier in game.board.tiers
                        for card in tier.visible
                    ),
                    chain.from_iterable(
                        (
                            card.cost.red,
                            card.cost.green,
                            card.cost.blue,
                            card.cost.black,
                            card.cost.white,
                            card.production.red,
                            card.production.green,
                            card.production.blue,
                            card.production.black,
                            card.production.white,
                            card.points,
                        )
                        for card in game.current_player.reserve
                    ),
                    chain.from_iterable(
                        tuple(iter(aristocrat.cost))
                        for aristocrat in game.board.aristocrats
                    ),
                    chain.from_iterable(
                        (
                            *tuple(iter(player.resources)),
                            *tuple(iter(player.production)),
                            player.points,
                        )
                        for player in game.players
                    ),
                    (len(player.reserve) for player in game.players[1:]),
                )
            )
        )

    @classmethod
    def _get_flatten_elements(cls, iterable: Iterable) -> Any:
        for element in iterable:
            if isinstance(element, Iterable):
                for inner_element in cls._get_flatten_elements(element):
                    yield inner_element
            else:
                yield element
