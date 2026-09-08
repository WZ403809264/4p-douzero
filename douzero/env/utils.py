import itertools

# global parameters
MIN_SINGLE_CARDS = 5
MIN_PAIRS = 3
MIN_TRIPLES = 2

# action types
TYPE_0_PASS = 0
TYPE_1_SINGLE = 1
TYPE_2_PAIR = 2
TYPE_3_TRIPLE = 3
TYPE_4_BOMB = 4
TYPE_5_KING_BOMB = 5
TYPE_7_3_2 = 6
TYPE_8_SERIAL_SINGLE = 7
TYPE_9_SERIAL_PAIR = 8
TYPE_10_SERIAL_TRIPLE = 9
TYPE_12_SERIAL_3_2 = 10
TYPE_15_WRONG = 11

# return all possible results of selecting num cards from cards list
def select(cards, num):
    return [list(i) for i in itertools.combinations(cards, num)]
