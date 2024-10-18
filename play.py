"""
All players begin with 15 dominoes (current implementation for 4 players only)
Players play in order (which is already determined) until 
- someone runs out of dominoes, in which case they win
- the pool of dominoes is empty and no one can make a legal move

Questions - 
What advantage does basic strategy have over random?
What's the advantage of reshuffling hand before each play?
"""

from turns import MexicanTrain

def play_game(number_of_players, train_start_number):

    game = MexicanTrain(num_players=number_of_players, train_start=train_start_number)
    winner = None

    for player in range(number_of_players):
        game.draw_initial_hand(player_id=player)
        # game.organize_initial_hand_simple_strategy(player_id=player)
        game.randomly_assign_initial_hand(player_id=player)

    while len(game.domino_pool) and (winner is None):
        for player in range(number_of_players):
            game.take_turn_with_basic_strategy(player_id=player)
            player_hand = game.hands[player]
            if not any([len(player_hand[key]) > 0 for key in player_hand.keys()]):
                winner = player
                break
            if not(len(game.domino_pool)):
                break
    return winner


if __name__ == "__main__":

    num_players = 4
    train_start_number = 3
    winners = []
    for iter in range(10000):
        winner = play_game(num_players, train_start_number)
        winners.append(winner)

    for player in range(num_players):
        print(str(player) + ": " + str(len([x for x in winners if x == player])))