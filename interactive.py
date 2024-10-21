"""
Attempt at version to play against computer
"""

from turns import MexicanTrain, correct_domino_order
import random

def play_game(train_start_number):

    def validate_user_input(user_input, num_options):
        if user_input in list(range(num_options)) + ["d"]:
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
        number_to_match = game.trains[double]["contents"][-1][0]
        print("You need to break the double ", (number_to_match, number_to_match))
        matching_dominos =[domino for domino in game.hands[0] if number_to_match in domino]
        # let the player know they can break
        if len(matching_dominos):
            print("Which domino would you like to use to break it?")
            for option_ind, option in enumerate(matching_dominos):
                print(option_ind, " - ", option)
            response = input("Use the number to the left of the desired option above")
            game.trains[double]["contents"].append(correct_domino_order(matching_dominos[response], number_to_match))
            game.hands[0].remove(matching_dominos[response])
        else:
            # if can't find a match, draw to find a match
            print("You don't have a domino that can break the double, you will have to draw.")
            drawn = random.choice(game.domino_pool)
            print("You drew ", drawn)
            game.domino_pool.remove(drawn)
            # if this matches the double, use it; if not, add it to hand
            if number_to_match in drawn:
                game.trains[double]["contents"].append(correct_domino_order(drawn, number_to_match))
            else:
                print("You cannot use this domino to break.  It will be added to your hand, and if you have a private train it will be made public")
                # add to hand
                game.hands[0].append(drawn)
                # if the player has a private train, make it public
                game.make_train_public(0)
            return


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
        return
    
    def player_turn():
        print("You have the following dominos:")
        for ind, domino in game.hands[0]:
            print(ind, " - ", domino)
        # check for double
        doubles = game.find_double()
        if doubles is not None:
            handle_double(doubles)
        else:
            options = []
            if not any([train["private_to"] == 0 for train in game.trains]) and any([game.train_start in domino for domino in game.hands[0]]):
                options.append("Start new private train")
            if any([train["private_to"] == 0 for train in game.trains]):
                private_train_ind = [ind  for ind, train in enumerate(game.trains)if train["private_to"] == 0][0]
                if any([game.trains[private_train_ind][-1][1] in domino for domino in game.hands[0]]):
                    options.append("Add to your private train")
            public_trains = [train  for train in enumerate(game.trains)if train["currently_public"]]
            if any(public_trains):
                if any([train["currently_public"] for train in game.trains]):
                    for train in public_trains:
                        if any([train[-1][1] in domino for domino in game.hands[0]]):
                            options.append("Add to public train ", train)
            num_public_trains = len(public_trains)
            if num_public_trains < (game.number_of_possible_trains - game.number_of_players) and any([game.train_start in domino for domino in game.hands[0]]):
                options.append("Start a new public train")
        if len(options):
            print("Your options are:")
            for ind, option in enumerate(options):
                print(ind, " - ", option)
            user_ip = input("Please select a move using the number to the left")
            valid_ip = validate_user_input(user_ip, len(options))
            while not valid_ip:
                user_ip = input("Input is not a valid option, please try again")
                valid_ip = validate_user_input(user_ip, len(options))

        else:
            print("You have no moves available, and a domino will be drawn for you")

        return

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
    valid_ip = validate_user_input(user_ip, len(game.hands[0]))
    while not valid_ip:
        user_ip = input("Input is not a valid option, please try again")
        valid_ip = validate_user_input(user_ip, len(game.hands[0]))
    if user_ip == "d":
        handle_draw()
    else:
        domino_to_use = game.hands[0][int(user_ip)]
        game = start_new_train(domino_to_use)

    # check if the player played a double; if so, make them deal with it.
    doubles = game.find_double()
    if doubles is not None:
        handle_double(doubles)

    # computer draws initial hand
    game.draw_initial_hand(player_id=1)
    game.organize_initial_hand_simple_strategy(player_id=1)    
    # computer takes initial turn
    game.take_turn_with_basic_strategy(1)
    
    # game loop
    while len(game.domino_pool) and (winner is None):
        # check for double

        # if double, must break, otherwise remind player of hand, trains, and choices

        # remind player of hand
        print("You have the following dominos:")
        for ind, domino in game.hands[0]:
            print(ind, " - ", domino)


        # computer turn
        game.take_turn_with_basic_strategy(1)
        player_hand = game.hands[1]
        if not any([len(player_hand[key]) > 0 for key in player_hand.keys()]):
            winner = 1
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