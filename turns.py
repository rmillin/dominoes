"""
class with functions needed to implement rules of Mexican Train
Questions:
- to what degree does strategy need to be built in?  E.g. order existing dominoes, etc.
    - for this first iteration, build it in completely, then try 
    writing a more general version without the strategy predetermined

- for this iteration, the strategy is as follows:
1. order initial hand of dominoes to form the longest train starting with the train start number;
these dominoes are for play on the player's private train, the remaining for the public train
2. for each turn, try in order
    - if can start a train, start with some probability (set to 1 for first turn)
    - if public trains exist and can play on one, play on public train with some probability (if can play on multiple,
    choose randomly which)
    - if can play on private train, play on it
    - if cannot do any of the above, draw

- for random strategy, follow the sequence of play defined above, but randomly assign dominoes to
"public", "new", and "private" hands, and don't do any ordering
"""
import random
import numpy as np


"""
simple functions

"""
def find_matching_domino_inds(hand, number):
    # returns all indices in hand that contain number
    matching_domino_inds = {key:[] for key in hand.keys()}
    for key in hand.keys():
        matching_domino_inds[key] = [ind for ind, domino in enumerate(hand[key]) if number in domino]
    return matching_domino_inds


def correct_domino_order(domino, number_to_match):
    # reverse order if first number isn't train start
    if domino[0] != number_to_match:
        return (domino[1], domino[0])
    else:
        return domino


def get_possible_trains(available_dominos, number_to_match, possible_train=[], possible_trains=[], depth=0):
    depth = depth + 1
    next_candidates = [next_domino for next_domino in available_dominos if number_to_match in next_domino]
    # reverse order if first number isn't train start
    next_candidates = [(next_domino[1], next_domino[0]) if next_domino[1] == number_to_match else next_domino for next_domino in next_candidates]
    for domino in next_candidates:
        # temporarily move the domino from hand to proposed train
        if domino in available_dominos:
            available_dominos.remove(domino)
        else:
            available_dominos.remove((domino[1], domino[0]))
        possible_train.append(domino)
        number_to_match = domino[1]
        if len(available_dominos):
            possible_train, possible_trains = get_possible_trains(available_dominos, number_to_match, possible_train, possible_trains, depth)
        # put the domino back in hand
        available_dominos.append(domino)
        possible_trains.append(possible_train)
        possible_train = possible_train[:(depth-1)]
    return possible_train, possible_trains



"""
class for game
"""

class MexicanTrain():
    def __init__(self, num_players, train_start) -> None:

        def define_domino_pool():
            domino_pool = []
            for first_domino_val in range(self.max_domino_value + 1):
                for second_domino_val in range(first_domino_val + 1):
                    domino_pool.append((first_domino_val, second_domino_val))
            self.domino_pool = domino_pool
        
        if (num_players >= 4) and (num_players <= 6):
            self.initial_num_dominoes = 15
            self.max_domino_value = 12
        elif (num_players == 2) or (num_players == 3):
            self.initial_num_dominoes = 8
            self.max_domino_value = 9
        else:
            raise(ValueError, "Currently game is only set up for 2 to 6 players")

        self.number_of_players = num_players
        self.number_of_possible_trains = 8
        self.train_start = train_start
        self.trains = []
        self.domino_pool = define_domino_pool()
        self.hands = [None] * num_players

        define_domino_pool()

    def draw_initial_hand(self, player_id):
        initial_hand = random.sample(self.domino_pool, self.initial_num_dominoes)
        for domino in initial_hand:
            self.domino_pool.remove(domino)
        self.hands[player_id] = initial_hand.copy()

    def make_train_private(self, player_id):
        for train in self.trains:
            if train["private_to"] == player_id:
                train["currently_public"] = False

    def make_train_public(self, player_id):
        for train in self.trains:
            if train["private_to"] == player_id:
                train["currently_public"] = True   
    
    def add_to_hand(self, player_ind, domino, division="public"):
        # ideally the player should reassign the purpose of the dominos based on the drawn domino,
        # but for now just assign it to public like a dummy
        hand = self.hands[player_ind]
        hand[division].append(domino)


    def update_hand(self, player_ind):
        # ideally the player should reassign the purpose of the dominos based on the board, but for now
        # assume a dumb player that doesn't do this
        pass

    def find_double(self):
        # returns the index of the train with a double if exists, otherwise returns None
        double_inds = []
        for ind, train in enumerate(self.trains):
            if len(train["contents"]):
                if train["contents"][-1][0] == train["contents"][-1][1]:
                    double_inds.append(ind)
        if len(double_inds) > 1:
            raise(ValueError, "More than one train has a double that needs to be broken; something has gone wrong in play")
        elif len(double_inds) == 1:
            return double_inds[0]
        else:
            return None
        
    def break_double(self, player_id, double):
        current_hand = self.hands[player_id]
        number_to_match = self.trains[double]["contents"][-1][0]
        is_private = self.trains[double]["private_to"] == player_id
        matching = find_matching_domino_inds(current_hand, number_to_match)
        # if double is on private train, next domino in private train hand is first choice
        # then try domino another domino public train hand
        if len(matching["private"]) or len(matching["public"]) or len(matching["new"]):
            success = True
            if is_private:
                if len(matching["private"]) and (0 in matching["private"]):
                    # use this domino and remove it from updated_hand
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["private"][0], number_to_match))
                    current_hand["private"].pop(0)
                elif len(matching["public"]):
                    # select a domino randomly from the public hand
                    to_use = random.choice(matching["public"])
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["public"][to_use], number_to_match))
                    current_hand["public"].pop(to_use)
                elif len(matching["new"]):
                    # select a domino randomly from the new train hand
                    to_use = random.choice(matching["new"])
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["new"][to_use], number_to_match))
                    current_hand["new"].pop(to_use)
                else: 
                    # the remaining case is that the domino is in "private" but not next in the train
                    to_use = random.choice(matching["private"])
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["private"][to_use], number_to_match))
                    current_hand["private"].pop(to_use)
            else:
                # in this case, prefer to use from the public hand, then the new hand, then the 
                # private hand closest to the end
                if len(matching["public"]):
                    # select a domino randomly from the public hand
                    to_use = random.choice(matching["public"])
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["public"][to_use], number_to_match))
                    current_hand["public"].pop(to_use)
                elif len(matching["new"]):
                    # select a domino randomly from the new train hand
                    to_use = random.choice(matching["new"])
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["new"][to_use], number_to_match))
                    current_hand["new"].pop(to_use)
                else:
                    to_use = matching["private"][-1]
                    self.trains[double]["contents"].append(correct_domino_order(current_hand["private"][to_use], number_to_match))
                    current_hand["private"].pop(to_use)

            return success
        
        else:
            # if can't find a match, draw to find a match
            drawn = random.choice(self.domino_pool)
            self.domino_pool.remove(drawn)
            # if this matches the double, use it; if not, add it to hand
            if number_to_match in drawn:
                self.trains[double]["contents"].append(correct_domino_order(drawn, number_to_match))
                success = True
            else:
                # add to hand
                self.add_to_hand(player_id, drawn)
                # make player's train public
                success = False

            return success

    def start_new_train(self, type, player_id):
        # assume that a player never starts a private train for another player
        hand = self.hands[player_id]
        success = False
        matching = find_matching_domino_inds(hand, self.train_start)
        # if a public train, first try to start from "new train" hand, then public, then private
        if type == "public":
            # can only start a public train if not all possible public spots have been filled
            if (len([train for train in self.trains if train["private_to"] is None]) + self.number_of_players) < self.number_of_possible_trains:
                if any([len(matching[key]) for key in matching.keys()]):
                    new_train = {"private_to": None, 
                            "currently_public": True, 
                            "contents": []}
                if len(matching["new"]):
                    # select a domino randomly from the new train hand
                    success = True
                    to_use = random.choice(matching["new"])
                    new_train["contents"] =  [correct_domino_order(hand["new"][to_use], self.train_start)]
                    hand["new"].pop(to_use)
                elif len(matching["public"]):
                    success = True
                    to_use = random.choice(matching["public"])
                    new_train["contents"] =  [correct_domino_order(hand["public"][to_use], self.train_start)]
                    hand["public"].pop(to_use)
                elif len(matching["private"]):
                    success = True
                    # use the last domino in the private train to avoid disruption
                    to_use = matching["private"][-1]
                    new_train["contents"] = [correct_domino_order(hand["private"][to_use], self.train_start)]
                    hand["private"].pop(to_use)
                else:
                    success = False
        elif type == "private":
            # if starting new private train, ideally the domino should be the first from the private hand
            if any([len(matching[key]) for key in matching.keys()]):
                new_train = {"private_to": player_id, 
                        "currently_public": False, 
                        "contents": []}
            if len(matching["private"]):
                success = True
                # use the first domino in the private train
                to_use = matching["private"][0]
                new_train["contents"] = [correct_domino_order(hand["private"][to_use], self.train_start)]
                hand["private"].pop(to_use)
            elif len(matching["new"]):
                # select a domino randomly from the new train hand
                success = True
                to_use = random.choice(matching["new"])
                new_train["contents"] =  [correct_domino_order(hand["new"][to_use], self.train_start)]
                hand["new"].pop(to_use)
            elif len(matching["public"]):
                success = True
                to_use = random.choice(matching["public"])
                new_train["contents"] =  [correct_domino_order(hand["public"][to_use], self.train_start)]
                hand["public"].pop(to_use)
            else:
                success = False        
        else:
            raise(ValueError, "Unrecognized train type")
        # add the new train to the board
        if success:
            self.trains.append(new_train)

        return success


    def make_move_with_basic_strategy(self, player_id):
        """
        check if player can play from public hand on public train
            - if so, do it
            - if not, check if player has a private train.  
                - if not, see if player can start one
                    - if so, start new train
                    - if not, draw
                        - if can play drawn domino, do so
                        - if not, add to hand
                - If so, see if player can play on it
                    - if so, play on private train
                    - if not, see if can play on public train
                    - if not, draw
                        - if can play drawn domino, do so
                        - if not, add to hand, make train public

        The above should work even for a first turn
        """
        current_hand = self.hands[player_id]
        if len(self.trains):
            available_public_train_inds = [ind for ind, train in enumerate(self.trains) if (train["currently_public"] == True) and not(train["private_to"] == player_id)]
            private_train_ind = [ind for ind, train in enumerate(self.trains) if train["private_to"] == player_id]
            private_train_exists = len(private_train_ind) > 0
            if private_train_exists:
                private_train_ind = private_train_ind[0]
        else:
            available_public_train_inds = []
            private_train_exists = False
        found_move = False
        # if a public train exists, try to add to it from "public" or "new"
        if len(available_public_train_inds):
            for public_train_ind in available_public_train_inds:
                number_to_match = self.trains[public_train_ind]["contents"][-1][1]
                matching = find_matching_domino_inds(current_hand, number_to_match)
                if len(matching["public"]):
                    found_move = True
                    to_use = random.choice(matching["public"])
                    self.trains[public_train_ind]["contents"].append(correct_domino_order(current_hand["public"][to_use], number_to_match))
                    current_hand["public"].pop(to_use)
                    break
            if not found_move:
                for public_train_ind in available_public_train_inds:
                    number_to_match = self.trains[public_train_ind]["contents"][-1][1]
                    matching = find_matching_domino_inds(current_hand, number_to_match)
                    if len(matching["new"]):
                        found_move = True
                        to_use = random.choice(matching["new"])
                        self.trains[public_train_ind]["contents"].append(correct_domino_order(current_hand["new"][to_use], number_to_match))
                        current_hand["new"].pop(to_use)
                        break
        # if this doesn't work, and the player doesn't have a private train, try to start one
        # if the player has a private train, try to add to it; start a new train if that's not possible
        if not found_move:
            if not private_train_exists:
                found_move = self.start_new_train("private", player_id)
            else:
                number_to_match = self.trains[private_train_ind]["contents"][-1][1]
                matching = find_matching_domino_inds(current_hand, number_to_match)
                # if a match is found anywhere, a move can be made
                if any([len(matching[key]) for key in matching.keys()]):
                    found_move = True
                    if len(matching["private"]) and (0 in matching["private"]):
                        # use this domino and remove it from updated_hand
                        self.trains[private_train_ind]["contents"].append(correct_domino_order(current_hand["private"][0], number_to_match))
                        current_hand["private"].pop(0)
                    elif len(matching["public"]):
                        # select a domino randomly from the public hand
                        to_use = random.choice(matching["public"])
                        self.trains[private_train_ind]["contents"].append(correct_domino_order(current_hand["public"][to_use], number_to_match))
                        current_hand["public"].pop(to_use)
                    elif len(matching["new"]):
                        # select a domino randomly from the new train hand
                        to_use = random.choice(matching["new"])
                        self.trains[private_train_ind]["contents"].append(correct_domino_order(current_hand["new"][to_use], number_to_match))
                        current_hand["new"].pop(to_use)
                    elif len(matching["private"]): 
                        # the remaining case is that the domino is in "private" but not next in the train
                        to_use = random.choice(matching["private"])
                        self.trains[private_train_ind]["contents"].append(correct_domino_order(current_hand["private"][to_use], number_to_match))
                        current_hand["private"].pop(to_use)
                else:
                    # try to start a new public train
                    found_move = self.start_new_train("public", player_id)
        return found_move


    def draw_and_try_move(self, player_id):
        # must draw since cannot play anywhere.  repeat the whole process
        drawn = random.choice(self.domino_pool)
        self.domino_pool.remove(drawn)
        success = False
        if self.train_start in drawn:
            # if the player doesn't have a private train, try to start one
            private_train_ind = [ind for ind, train in enumerate(self.trains) if train["private_to"] == player_id]
            private_train_exists = len(private_train_ind) > 0
            if not private_train_exists:
                success = True
                new_train = {"private_to": player_id, 
                    "currently_public": False, 
                    "contents": [correct_domino_order(drawn, self.train_start)]}
            else:
                # can only start a public train if the number of public trains plus the number of possible private trains is less than the total number of trains allowed
                if (len([train for train in self.trains if train["private_to"] is None]) + self.number_of_players) < self.number_of_possible_trains:
                    success = True
                    new_train = {"private_to": None, 
                        "currently_public": True, 
                        "contents": [correct_domino_order(drawn, self.train_start)]}
                    self.trains.append(new_train)
        if not success:
            # if can't start a new train, see if drawn domino matches the end of any available train
            success = False
            for train in self.trains:
                if train["currently_public"] or (train["private_to"] == player_id):
                    number_to_match = train["contents"][-1][1]
                    if number_to_match in drawn:
                        train["contents"].append(correct_domino_order(drawn, number_to_match))
                        self.make_train_private(player_id)
                        success = True
                        break
        if not success:
            # add to hand
            self.add_to_hand(player_id, drawn)
            # make player's train private or public depending on outcome
            
        return success


    def take_turn_with_basic_strategy(self, player_id):
        """   
        train_start_number is the number with which all trains must start (the double in the center of play) 
        for now, public trains includes all player private trains that are currently open to others
        current_hand is a dictionary with assigment based on intended use - 
        {"private": [], "public": [], "new": []}
        """
        self.update_hand(player_id)
        """
        - Check for double on the board:
        Player must always handle double if present (unless they place the double and its their final domino, or it is impossible 
        to break it because all breaking dominoes have been played)
        """
        double = self.find_double()        
        # if double exists, check if you can break; if not, draw, then try to break
        if double is not None:
            success = self.break_double(player_id,  double)
        else:
            success = self.make_move_with_basic_strategy(player_id)
            if success:
                # special case - if the domino played was the player's last, then don't
                # worry if it was a double
                if (not any([len(self.hands[player_id][key]) > 0 for key in self.hands[player_id].keys()])) or len(self.domino_pool) == 0:
                        pass
                else:
                    # if the domino used is a double, must try to break it
                    double = self.find_double()
                    if double is not None:
                        success = self.break_double(player_id, double)
            else:
                success = self.draw_and_try_move(player_id)
                if success:
                    # special cases - if the domino played was the player's last, or if there
                    # are no dominos left, then don't worry if it was a double
                    if (not any([len(self.hands[player_id][key]) > 0 for key in self.hands[player_id].keys()])) or len(self.domino_pool) == 0:
                        pass
                    # otherwise, must check if it was a double and, if so, try to break
                    else:
                        double = self.find_double()
            
                        if double is not None:
                            success = self.break_double(player_id, double)

        if success:
            self.make_train_private(player_id)
        else:
            self.make_train_public(player_id)

        
    def organize_initial_hand_simple_strategy(self, player_id):
        """
        Simple strategy:  
            - find maximum train starting with train_start_number for "private"
            - assign any remaining dominoes with train_start_number to "new"
            - assign the rest to "public"
        This can be generalized with train_start_number to be the last value played on ones' private train 
        (e.g. by another player or by same player, but with additional dominoes drawn)
        """
        unorganized_hand = self.hands[player_id]
        organized_hand = {"private": [],  "public": [], "new": []}
        # for now, brute force this - find all possible trains and then select the longest
        _, possible_trains = get_possible_trains(unorganized_hand, self.train_start, possible_train=[], possible_trains=[])
        # find the longest trains
        if len(possible_trains):
            max_train_len = max([len(train) for train in possible_trains])
            longest_trains = [train for train in possible_trains if len(train) == max_train_len]
            contains_startnum = [sum([self.train_start in car for car in train]) for train in longest_trains]
            if len(longest_trains) > 1:
                # if more than one is available, use the one with the fewest of startnum
                longest_train = longest_trains[np.argsort(contains_startnum)[0]]
            else:
                longest_train = longest_trains[0]
        else:
            longest_train = []
        # assign remaining dominoes with start number to "new", and then the rest to "public"
        organized_hand["private"] = longest_train
        remaining_hand = list((set(unorganized_hand).difference(set(longest_train))).difference(set([(train[1], train[0]) for train in longest_train])))
        possible_train_starts = [el for el in remaining_hand if self.train_start in el]
        organized_hand["new"] = possible_train_starts
        organized_hand["public"] = list((set(remaining_hand).difference(set(possible_train_starts))).difference(set([(train[1], train[0]) for train in possible_train_starts])))
        self.hands[player_id] = organized_hand

    def randomly_assign_initial_hand(self, player_id):
        """
        Assign equal numbers of dominos to the three hands, chosen randomly
        """
        unorganized_hand = self.hands[player_id]
        n_per_type = int(self.initial_num_dominoes/3)
        random.shuffle(unorganized_hand)
        organized_hand = {"private": unorganized_hand[:n_per_type],  
                          "public": unorganized_hand[n_per_type:2*n_per_type], 
                          "new": unorganized_hand[2*n_per_type:]}
        self.hands[player_id] = organized_hand



if __name__ == "__main__":

    number_of_players = 4
    train_start_number = 3

    game = MexicanTrain(num_players=number_of_players, train_start=train_start_number)

    for player in range(number_of_players):
        game.draw_initial_hand(player_id=player)
        game.organize_initial_hand_simple_strategy(player_id=player)


    while 1:
        for player in range(number_of_players):
            game.take_turn_with_basic_strategy(player_id=player)


