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
    winner = None
    if num_players != 4:
        raise(ValueError, "Play currently only implemented for 4 players")
    if any([strategy != "basic" for strategy in player_strategies]):
        raise(ValueError, "Play currently only implemented for basic strategy")
        # draw initial hand randomly, then organize based on simple strategy
    for player in range(num_players):
        # player_strategy = player_strategies[player]
        player_hand = draw_initial_hand(num_players)
        player_hand = organize_initial_hand_simple_strategy(player_hand, train_start_number)
        hands.append(player_hand)
    # as long as no game ending condition is met, players take turns in order
    while len(DOMINO_POOL) and (winner is None):
        for player in range(num_players):
            player_hand = hands[player]
            player_updated_hand = take_turn_with_basic_strategy(player, player_hand, train_start_number)
            if not any([len(player_updated_hand[key]) > 0 for key in player_updated_hand.keys()]):
                winner = player
    return winner


if __name__ == "__main__":
    player_strategies = ["basic", "basic", "basic", "basic"]