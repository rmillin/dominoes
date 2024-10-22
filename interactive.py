"""
Attempt at version to play against computer
"""

from turns import MexicanTrain, correct_domino_order
import random

def play_game(train_start_number):

    def validate_user_input(user_input, num_options):
        if user_input in [str(x) for x in list(range(num_options))] + ["d"]:
            valid_input = True
        else:
            valid_input = False
        return valid_input
    

    def handle_draw():
        drawn = random.choice(game.domino_pool)
        game.domino_pool.remove(drawn)
        print("You have drawn ", drawn)
        if any(game.trains):
            print("Current trains are:")
            for train_ind, train in enumerate(game.trains):
                print(train_ind, " - ", train)
        else:
            print("No trains exist yet")
        options = []
        if game.train_start in drawn:
            if (len([train for train in game.trains if train["private_to"] is None]) + game.number_of_players) < game.number_of_possible_trains:
                options.append("Start new public train")
            if len([train for train in game.trains if train["private_to"] == 0]) == 0:
                options.append("Start new private train")
        for train_ind, train in enumerate(game.trains):
            if train["contents"][-1][1] in drawn:
                if train["private_to"] == 0:
                    options.append("Add to your private train")
                elif train["currently_public"] == True:
                    options.append("Add to public train " + str(train))
                else:
                    pass
        if len(options):
            print("You have the following choices:")
            for option_ind, option in enumerate(options):
                print(option_ind, " - ", option)
            response = input("Use the number to the left of the desired option above")
            valid_response = validate_user_input(response, len(options))
            while not valid_response:
                response = input("Input is not a valid option, please try again")
                valid_response = validate_user_input(response, len(options))

            handle_user_choice(response, options, [drawn])

        else:
            print("You cannot play this domino.  It will be added to your hand, and if you have a private train it will be made public")
            # add to hand
            game.hands[0].append(drawn)
            # if the player has a private train, make it public
            game.make_train_public(0)
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
            valid_ip = validate_user_input(response, len(matching_dominos))
            while not valid_ip:
                response = input("Input is not a valid option, please try again")
                valid_ip = validate_user_input(response, len(matching_dominos))

            game.trains[double]["contents"].append(correct_domino_order(matching_dominos[int(response)], number_to_match))
            game.hands[0].remove(matching_dominos[int(response)])
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


    def handle_user_choice(user_input, options, available_dominos):

        # need to add special case where only one domino fits criteria, or the domino has been drawn

        option = options[int(user_input)]
        if option == "Start new private train":
            candidate_dominos = [domino for domino in available_dominos if game.train_start in domino]
            if len(candidate_dominos) > 1:
                print("The following dominos are available to start your private train:")
                for ind, domino in enumerate(candidate_dominos):
                    print(ind, ' - ', domino)
                response = input("Enter the number corresponding to your choice")
                valid_ip = validate_user_input(response, len(candidate_dominos))
                while not valid_ip:
                    response = input("Input is not a valid option, please try again")
                    valid_ip = validate_user_input(response, len(candidate_dominos))
                start_new_train("private", candidate_dominos[int(response)])
            else:
                print(candidate_dominos[0], " is the only available domino and will be used to start the train")
                start_new_train("private", candidate_dominos[0])
        elif option == "Add to your private train":
            private_train = [train for train in game.trains if train["private_to"] == 0][0]
            train_end = private_train["contents"][-1][1]
            candidate_dominos = [domino for domino in available_dominos if train_end in domino]
            if len(candidate_dominos) > 1:
                print("The following dominos are available to add:")
                for ind, domino in enumerate(candidate_dominos):
                    print(ind, ' - ', domino)
                response = input("Enter the number corresponding to your choice")
                valid_ip = validate_user_input(response, len(candidate_dominos))
                while not valid_ip:
                    response = input("Input is not a valid option, please try again")
                    valid_ip = validate_user_input(response, len(candidate_dominos))
                private_train["contents"].append(correct_domino_order(candidate_dominos[int(response)], train_end))
                game.hands[0].remove(candidate_dominos[int(response)])
            else:
                print(candidate_dominos[0], " is the only available domino and will be added")
                private_train["contents"].append(correct_domino_order(candidate_dominos[0], train_end))
                # handle draw or when domino comes from hand
                if candidate_dominos[0] in game.hands[0]:
                    game.hands[0].remove(candidate_dominos[0])

        elif option == "Start new public train":
            candidate_dominos = [domino for domino in available_dominos if game.train_start in domino]
            if len(candidate_dominos) > 1:
                print("The following dominos are available to start a public train:")
                for ind, domino in enumerate(candidate_dominos):
                    print(ind, ' - ', domino)
                response = input("Enter the number corresponding to your choice")
                valid_ip = validate_user_input(response, len(candidate_dominos))
                while not valid_ip:
                    response = input("Input is not a valid option, please try again")
                    valid_ip = validate_user_input(response, len(candidate_dominos))
                start_new_train("public", candidate_dominos[int(response)])
            else:
                print(candidate_dominos[0], " is the only available domino and will be used to start the train")
                start_new_train("public", candidate_dominos[0])
        elif "Add to public" in option:
            chosen_public_train = eval(option.replace("Add to public train ", ""))
            public_train = [train for train in game.trains if train == chosen_public_train][0]
            train_end = public_train["contents"][-1][1]
            candidate_dominos = [domino for domino in available_dominos if train_end in domino]
            if len(candidate_dominos) > 1:
                print("The following dominos are available to add:")
                for ind, domino in enumerate(candidate_dominos):
                    print(ind, ' - ', domino)
                response = input("Enter the number corresponding to your choice")
                valid_ip = validate_user_input(response, len(candidate_dominos))
                while not valid_ip:
                    response = input("Input is not a valid option, please try again")
                    valid_ip = validate_user_input(response, len(candidate_dominos))
                public_train["contents"].append(correct_domino_order(candidate_dominos[int(response)], train_end))
                game.hands[0].remove(candidate_dominos[int(response)])
            else:
                print(candidate_dominos[0], " is the only available domino and will be added")
                public_train["contents"].append(correct_domino_order(candidate_dominos[0], train_end))
                # handle draw or when domino comes from hand
                if candidate_dominos[0] in game.hands[0]:
                    game.hands[0].remove(candidate_dominos[0])

        else:
            raise(ValueError, "Should not end up here ever")
        return

    def start_new_train(type, domino):
        if type == "public":
            new_train = {"private_to": None, 
            "currently_public": True, 
            "contents": [correct_domino_order(domino, game.train_start)]}
        else:
            new_train = {"private_to": 0, 
            "currently_public": False, 
            "contents": [correct_domino_order(domino, game.train_start)]}
        game.trains.append(new_train)
        # handle case when domino is drawn or already in hand
        if domino in game.hands[0]:
            game.hands[0].remove(domino)
        return
    
    def player_turn():
        print("You have the following dominos:")
        for ind, domino in enumerate(game.hands[0]):
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
                if any([game.trains[private_train_ind]["contents"][-1][1] in domino for domino in game.hands[0]]):
                    options.append("Add to your private train")
            public_trains = [train  for train in game.trains if train["currently_public"] and (train["private_to"] != 0)]
            if any(public_trains):
                for train in public_trains:
                    if any([train["contents"][-1][1] in domino for domino in game.hands[0]]):
                        options.append("Add to public train " + str(train))
            num_public_trains = len(public_trains)
            if num_public_trains < (game.number_of_possible_trains - game.number_of_players) and any([game.train_start in domino for domino in game.hands[0]]):
                options.append("Start new public train")

            if len(options):
                # a move is available, so make train private
                if any([train["private_to"] == 0 for train in game.trains]):
                    game.make_train_private(0)
                print("Your options are:")
                for ind, option in enumerate(options):
                    print(ind, " - ", option)
                user_ip = input("Please select a move using the number to the left")
                valid_ip = validate_user_input(user_ip, len(options))
                while not valid_ip:
                    user_ip = input("Input is not a valid option, please try again")
                    valid_ip = validate_user_input(user_ip, len(options))
                handle_user_choice(user_ip, options, game.hands[0])

                # make sure this didn't result in double
                doubles = game.find_double()
                if doubles is not None:
                    handle_double(doubles)

            else:
                print("You have no moves available, and a domino will be drawn for you")
                handle_draw()
                # make sure this didn't result in double
                doubles = game.find_double()
                if doubles is not None:
                    handle_double(doubles)

        return

    game = MexicanTrain(num_players=2, train_start=train_start_number)
    winner = None

    input("Press any key to draw your initial hand.")
    game.draw_initial_hand(player_id=0)
    print("You have drawn the following dominos:")
    for ind, domino in enumerate(game.hands[0]):
        print(ind, " - ", domino)
    print("If you can, start a private train.  The train must start with ", train_start_number)
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
        start_new_train("private", domino_to_use)

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

        # remind player of hand and trains
        print("You have the following dominos:")
        for domino in game.hands[0]:
            print(domino)

        print("The following trains are available for play:")
        for train in game.trains:
            if (train["private_to"] == 0) or train["currently_public"]:
                print(train)
       
        player_turn()
        if not len(game.hands[0]):
            winner = 0
            break
        if not(len(game.domino_pool)):
            break

        # computer turn
        game.take_turn_with_basic_strategy(1)
        player_hand = game.hands[1]
        if not any([len(player_hand[key]) > 0 for key in player_hand.keys()]):
            winner = 1
            break
        if not(len(game.domino_pool)):
            break

    print("Game over!")
    print("Final board:")
    for train in game.trains:
        print(train)

    return winner


if __name__ == "__main__":

    # let human player go first for advantage; 0 = human, 1 = computer
    num_players = 2
    train_start_number = 3
    winner = play_game(train_start_number)
    if winner == 0:
        print("YOU WIN!!!!")
    elif winner == 1:
        print("YOU LOSE!!!")
    else:
        print("Ran out of dominos, game is a draw!")

######################## Need to deal with case where last domino played is double #########