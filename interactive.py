"""
Attempt at version to play against computer
"""

from turns import MexicanTrain, correct_domino_order
import random

def play_game(train_start_number):

    def validate_user_input(user_input):
        if user_input in list(range(len(game.hands[0]))) + ["d"]:
            valid_input = True
        else:
            valid_input = False
        return valid_input
    

    def handle_draw():
        drawn = random.choice(game.domino_pool)
        game.domino_pool.remove(drawn)
        game.hands[0].extend(drawn)
        print("You have drawn ", drawn)
        print("current trains are:")
        for train_ind, train in enumerate(game.trains):
            print(train_ind, " - ", train)
        options = []
        if game.train_start in drawn:
            if (len([train for train in game.trains if train["private_to"] is None]) + game.number_of_players) < game.number_of_possible_trains:
                options.append("start a public train")
            if len([train for train in game.trains if train["private_to"] == 0]) == 0:
                options.append("start a private train")
        for train_ind, train in enumerate(game.trains):
            if train[-1][1] in drawn:
                if train["private_to"] == 0:
                    options.append("add to private train ", train_ind)
                elif train["currently_public"] == True:
                    options.append("add to currently public train ", train_ind)
                else:
                    pass
        if len(options):
            print("You have the following choices:")
            for option_ind, option in enumerate(options):
                print(option_ind, " - ", option)
            response = input("Use the number to the left of the desired option above")
            valid_response = response in list(range(len(options)))
            while not valid_response:
                response = input("Input is not a valid option, please try again")
                valid_response = response in list(range(len(options)))
        return
    

    def handle_double(double):
        current_hand = game.hands[0]
        number_to_match = game.trains[double]["contents"][-1][0]
        print("You need to break the double ", (number_to_match, number_to_match))
        matching_dominos =[domino for domino in game.hands[0] if number_to_match in domino]
        # let the player know they can break
        if len(matching_dominos):
            success = True

            game.trains[double]["contents"].append(correct_domino_order(current_hand["private"][0], number_to_match))
            game.hands[0].remove(to_use)
        else:
            # if can't find a match, draw to find a match
            drawn = random.choice(game.domino_pool)
            game.domino_pool.remove(drawn)
            # if this matches the double, use it; if not, add it to hand
            if number_to_match in drawn:
                game.trains[double]["contents"].append(correct_domino_order(drawn, number_to_match))
                success = True
            else:
                # add to hand
                game.hands[0].append(drawn)
                # make player's train public
                success = False

            return success


    def handle_user_choice(user_input):
        return

    def start_new_train(type, domino):
        if type == "public":
            new_train = {"private_to": None, 
            "currently_public": True, 
            "contents": [correct_domino_order(domino, game.train_start_num)]}
        else:
            new_train = {"private_to": 0, 
            "currently_public": False, 
            "contents": [correct_domino_order(domino, game.train_start_num)]}
        game.trains.append(new_train)
        game.hands[0].remove(domino)
        return game

    game = MexicanTrain(num_players=2, train_start=train_start_number)
    winner = None

    input("Press any key to draw your initial hand.")
    game.draw_initial_hand(player_id=0)
    print("You have drawn the following dominos:")
    for ind, domino in game.hands[0]:
        print(ind, " - ", domino)
    print("If you can, start a private train.  The train must start with " + train_start_number)
    print("To start a train, use the number to the left of the domino displayed above")
    user_ip = input("If you cannot start a train, draw a domino (use the d key).")
    valid_ip = validate_user_input(user_ip)
    while not valid_ip:
        user_ip = input("Input is not a valid option, please try again")
        valid_ip = validate_user_input(user_ip)
    if user_ip == "d":
        handle_draw()
    else:
        domino_to_use = game.hands[0][int(user_ip)]
        game = start_new_train(domino_to_use)

    # check if the player played a double; if so, make them deal with it.
    doubles = game.find_double()
    if doubles is not None:
        handle_double()

    game.draw_initial_hand(player_id=1)
    game.organize_initial_hand_simple_strategy(player_id=1)    

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

    # let human player go first for advantage; 0 = human, 1 = computer
    num_players = 2
    train_start_number = 3
    winner = play_game(num_players, train_start_number)
    if winner == 0:
        print("YOU WIN!!!!")
    elif winner == 1:
        print("YOU LOSE!!!")
    else:
        print("Ran out of dominos, game is a draw!")