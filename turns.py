"""
functions needed to implement rules of Mexican Train
Questions:
- to what degree does strategy need to be built in?  E.g. order existing dominoes, etc.
    - for this first iteration, build it in with a few parameters to learn, then try 
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
"""
import random
import numpy as np


# define the set of dominoes
# build the domino pool
MAX_DOMINO_VALUE = 12
DOMINO_POOL = []
for first_domino_val in range(MAX_DOMINO_VALUE + 1):
    for second_domino_val in range(first_domino_val + 1):
        DOMINO_POOL.append((first_domino_val, second_domino_val))

# initialize the trains
# TRAINS is a list of existing trains stored as dictionaries:
# TRAINS = [{"private_to": player_id/None, "currently_public": True/False, "contents": [list of dominoes]}, ...]
TRAINS = []


def draw_initial_hand(number_of_players):

    if number_of_players == 4:
        num_dominoes = 15
    else:
        raise(ValueError, "Currenlty game is only set up for 4 players")
    initial_hand = random.sample(DOMINO_POOL, num_dominoes)
    for domino in initial_hand:
        DOMINO_POOL.remove(domino)

    return initial_hand


def organize_initial_hand_simple_strategy(hand, train_start_number):
    """
    Simple strategy:  
        - find maximum train starting with train_start_number for "private"
        - assign any remaining dominoes with train_start_number to "new"
        - assign the rest to "public"
    This can be generalized with train_start_number to be the last value played on ones' private train 
    (e.g. by another player or by same player, but with additional dominoes drawn)
    """
    organized_hand = {"private": [],  "public": [], "new": []}
    # for now, brute force this - find all possible trains and then select the longest
    possible_trains = get_possible_trains(hand, train_start_number)
    # find the longest trains
    max_train_len = max([len(train) for train in possible_trains])
    longest_trains = [train for train in possible_trains if len(train) == max_train_len]
    contains_startnum = [sum([train_start_number in car for car in train]) for train in longest_trains]
    if len(longest_trains) > 1:
        # if more than one is available, use the one with the fewest of startnum
        longest_train = longest_trains[np.argsort(contains_startnum)[0]]
    else:
        longest_train = longest_trains[0]
    organized_hand["private"] = longest_train
    remaining_hand = list(set(hand).difference(set(longest_train)))
    return organized_hand


def get_possible_trains(remaining_hand, number_to_match, possible_train=[], possible_trains=[], depth=0):
    depth = depth + 1
    next_candidates = [next_domino for next_domino in remaining_hand if number_to_match in next_domino]
    # reverse order if first number isn't train start
    next_candidates = [(next_domino[1], next_domino[0]) if next_domino[1] == number_to_match else next_domino for next_domino in next_candidates]
    for domino in next_candidates:
        # temporarily move the domino from hand to proposed train
        if domino in remaining_hand:
            remaining_hand.remove(domino)
        else:
            remaining_hand.remove((domino[1], domino[0]))
        possible_train.append(domino)
        print(possible_train)
        print(depth)
        print(possible_trains)
        number_to_match = domino[1]
        if len(remaining_hand):
            possible_train, possible_trains = get_possible_trains(remaining_hand, number_to_match, possible_train, possible_trains, depth)
        # put the domino back in hand
        remaining_hand.append(domino)
        possible_trains.append(possible_train)
        possible_train = possible_train[:(depth-1)]
    return possible_train, possible_trains


def add_to_hand(old_hand, domino):
    # ideally the player should reassign the purpose of the dominos based on the drawn domino,
    # but for now just assign it to public like a dummy
    new_hand = old_hand.copy()
    new_hand["public"].append(domino)
    return new_hand


def update_hand(old_hand):
    # ideally the player should reassign the purpose of the dominos based on the board, but for now
    # assume a dumb player that doesn't do this
    new_hand = old_hand.copy()
    return new_hand


def make_train_private(player_id):
    for train in TRAINS:
        if train["private_to"] == player_id:
            train["currently_public"] = False
    return


def make_train_public(player_id):
    for train in TRAINS:
        if train["private_to"] == player_id:
            train["currently_public"] = True
    return


def find_double():
    # returns the index of the train with a double if exists, otherwise returns None
    double_inds = []
    for ind, train in enumerate(TRAINS):
        if len(train["contents"]):
            if train["contents"][-1][0] == train[-1][1]:
                double_inds.append(ind)
    if len(double_inds) > 1:
        raise(ValueError, "More than one train has a double that needs to be broken; something has gone wrong in play")
    elif len(double_inds) == 1:
        return double_inds[0]
    else:
        return None


def play_double():
    return


def find_matching_domino_inds(hand, number):
    # returns all indices in hand that contain number
    matching_domino_inds = {key:[] for key in hand.keys()}
    for key in hand.keys():
        matching_domino_inds[key] = [ind for ind, domino in enumerate(hand[key]) if number in domino]
    return matching_domino_inds

def take_turn_with_basic_strategy(player_id, current_hand, train_start_number, prob_public_train=1, prob_start_train=0):
    """   
    train_start_number is the number with which all trains must start (the double in the center of play) 
    prob_public_train is the probability that a player plays on a public train when they could play on a private train
    prob_start_train is the probability that a player starts a new train when they could play on an existing train
    for now, public trains includes all player private trains that are currently open to others
    current_hand is a dictionary with assigment based on intended use - 
    {"private": [], "public": [], "new": []}
    """
    updated_hand = update_hand()
    """
    - Check for double on the board:
    Player must always handle double if present (unless they place the double and its their final domino, or it is impossible 
    to break it because all breaking dominoes have been played)
    """
    double = find_double()
    # if double exists, check if you can break; if not, draw, then try to break
    if double:
        number_to_match = TRAINS[double]["contents"][-1][0]
        is_private = TRAINS[double]["private_to"] == player_id
        matching = find_matching_domino_inds(current_hand, number_to_match)
        # if double is on private train, next domino in private train hand is first choice
        # then try domino another domino public train hand
        if len(matching["private"]) or len(matching["public"]) or len(matching["first"]):
            if is_private:
                if len(matching["private"]) and (0 in matching["private"]):
                    # use this domino and remove it from updated_hand
                    TRAINS[double]["contents"].append(current_hand["private"][0])
                    updated_hand["private"].pop(0)
                elif len(matching["public"]):
                    # select a domino randomly from the public hand
                    to_use = random.choice(matching["public"])

                elif len(matching["first"]):
                    pass
                elif len(matching["private"]):
                    pass
                else:
                    pass
            else:
                pass
            make_train_private(player_id)
            return update_hand
        else:
            # if can't find a match, draw to find a match
            drawn = random.sample(DOMINO_POOL)
            DOMINO_POOL.remove(drawn)
            # if this matches the double, use it; if not, add it to hand
            if number_to_match in drawn:
                TRAINS[double]["contents"].append(drawn)
                make_train_private(player_id)
            else:
                # add to hand
                updated_hand = add_to_hand(current_hand, drawn)
                # make player's train public
                make_train_public(player_id)
    else:
        """
        check if player has a private train.  
            - If so
                - see if player can play on it
                - if not, see if player can play on another train
                - if not, draw
                    - if can play drawn domino, do so
                    - if not, add to hand, make train public
                
            - if not
                - see if player can start one
                - If not, see if player can play on public train
                    - if not, draw
                        - if can play drawn domino, do so
                        - if not, add to hand
        The above should work even for a first turn
        """
    return updated_hand


def take_turn_with_random_strategy(player_id, current_hand, train_start_number, prob_public_train=1, prob_start_train=0):
    updated_hand = current_hand.copy()
    return updated_hand


if __name__ == "__main__":
    hand = [(1, 2), (2, 3), (3, 4), (4, 5), (2, 7), (7, 8), (1, 4), (4, 9)]
    candidate_dominoes = [(1, 2), (1, 4)]
    number_to_match = 1
    train, trains = get_possible_trains(hand, number_to_match)
    print('done')