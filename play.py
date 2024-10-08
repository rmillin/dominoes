"""
All players begin with 15 dominoes (current implementation for 4 players only)
Players play in order (which is already determined) until 
- someone runs out of dominoes, in which case they win
- the pool of dominoes is empty and no one can make a legal move

Questions - 
What advantage does basic strategy have over random?
What's the advantage of reshuffling hand before each play?
"""

import random

from turns import DOMINO_POOL, draw_initial_hand, take_turn_with_basic_strategy, organize_initial_hand_simple_strategy

def play_game(player_strategies, train_start_number):
    hands = [] # hands ordered by players
    num_players = len(player_strategies)
    if num_players != 4:
        raise(ValueError, "Play only implemented for 4 players currently")
    else:
        # draw initial hand randomly, then organize based on simple strategy
        for player in range(num_players):
            player_strategy = player_strategies[player]
            player_hand = draw_initial_hand(num_players)
            player_hand = organize_initial_hand_simple_strategy(player_hand, train_start_number)
            hands.append(player_hand)

    return