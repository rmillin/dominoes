"""
All players begin with 15 dominoes (current implementation for 4 players only)
Players play in order (which is already determined) until 
- someone runs out of dominoes, in which case they win
- the pool of dominoes is empty and no one can make a legal move
"""

import random

from turns import DOMINO_POOL, draw_initial_hand, take_turn_with_basic_strategy

def play_game(num_players):
    hands = [] # hands ordered by players
    if num_players != 4:
        raise(ValueError, "Play only implemented for 4 players currently")
    else:
        # draw initial hand randomly
        for player in range(num_players):
            player_hand = draw_initial_hand(num_players)

    return