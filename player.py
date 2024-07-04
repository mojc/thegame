import random

hyperparameters = {
    'additional_play_limit': 10,
    'booking_penalties': {
        0: 0,
        1: 5,
        2: 10,
        3: 20
    }
}


class Player:
    def __init__(self, idx, hps=hyperparameters):
        self.hps = hps
        self.idx = idx  # to know which booking is theirs

    def query_action(self, hand, piles, cards_played):
        if cards_played < 2:
            possible_moves = []
            for card in hand:
                for pile_name, pile in piles.items():
                    if self.is_valid_move(card, pile_name, pile):
                        cost = self.calculate_distance(card, pile_name, pile, bookings=True)
                        possible_moves.append((card, pile_name, cost))

            if not possible_moves:
                return "pass", None, None

            possible_moves.sort(key=lambda move: move[2])  # sort by cost - internal decision
            return "play", possible_moves[0][0], possible_moves[0][1]
        else:
            return "pass", None, None


    def is_valid_move(self, card, pilename, pile):
        # Check if a card can be played on the specified pile
        top_card = pile['value']
        if pilename.startswith('asc'):
            return card > top_card or card == top_card - 10
        elif pilename.startswith('desc'):
            return card < top_card or card == top_card + 10
        return False

    def discuss(self, hand, piles):
        for key, pile in piles.items():
            for card in hand:
                play_value = self.calculate_distance(card, key, pile)
                if play_value > 0 or play_value == -10: ## TODO simplify ?
                    play_value_level = self.level_from_value(play_value)
                    if play_value_level > piles[key]['bookings'][self.idx]:
                        piles[key]['bookings'][self.idx] = play_value_level

    def calculate_distance(self, card, pile_name, pile, bookings=False):
        top_card = pile['value']
        booking_penalty = self.hps['booking_penalties'][max(pile['bookings'])] if bookings else 0
        if pile_name.startswith('asc'):
            d = card - top_card
        elif pile_name.startswith('desc'):
            d = top_card - card
        return d + booking_penalty

    def level_from_value(self, value):
        if value == -10:
            return 3
        if value < 5:
            return 2
        elif value < 12:
            return 1
        return 0






