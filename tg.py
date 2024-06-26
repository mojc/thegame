import random

class GameState:
    def __init__(self, num_players, hps=None):
        self.deck = self.initialize_deck()
        self.hands = self.deal_hands(num_players)
        self.empty_piles = {
            'asc1': {'value':1, 'bookings': [0 for _ in range(num_players)]},
            'asc2': {'value':1, 'bookings': [0 for _ in range(num_players)]},
            'desc1': {'value':100, 'bookings': [0 for _ in range(num_players)]},
            'desc2': {'value':100, 'bookings': [0 for _ in range(num_players)]},
        }
        self.piles = self.empty_piles.copy()
        self.played_cards = []
        self.current_player = 0
        self.hps = hps

    def initialize_deck(self):
        # Initialize the deck with cards from 2 to 99 and shuffle
        deck = list(range(2, 100))
        random.shuffle(deck)
        return deck

    def deal_hands(self, num_players, hand_size=6):
        # Deal hands to each player
        hands = []
        for _ in range(num_players):
            hand = [self.deck.pop() for _ in range(hand_size)]
            hands.append(hand)
        return hands

    def is_valid_move(self, card, pile):
        # Check if a card can be played on the specified pile
        top_card = self.piles[pile]['value']
        if pile.startswith('asc'):
            return card > top_card or card == top_card - 10
        elif pile.startswith('desc'):
            return card < top_card or card == top_card + 10
        return False

    def play_card(self, player, card, pile):
        # Play a card on the specified pile if the move is valid
        if self.is_valid_move(card, pile):
            self.piles[pile]['value'] = card
            self.piles[pile]['bookings'] = [0 for _ in range(len(self.hands))]
            self.hands[player].remove(card)
            self.played_cards.append(card)
            return True
        return False

    def draw_cards(self, player, num_cards):
        # Draw a specified number of cards from the deck to the player's hand
        for _ in range(num_cards):
            if self.deck:
                self.hands[player].append(self.deck.pop())

    def is_winning_state(self):
        # Check if the game is won (all cards played)
        return len(self.deck) == 0 and all(len(hand) == 0 for hand in self.hands)

    def get_possible_moves(self, player, piles=None):
        # Generate all possible moves for a player
        if piles is None:
            piles = self.piles.keys()

        possible_moves = []
        for card in self.hands[player]:
            for pile in piles:
                if self.is_valid_move(card, pile):
                    possible_moves.append((card, pile))
        return possible_moves

    def find_closest_move(self, player, piles=None):
        # Find the optimal move based on the smallest distance to the piles
        if piles is None:
            piles = self.piles.keys()
        possible_moves = self.get_possible_moves(player, piles)
        if not possible_moves:
            return None
        possible_moves.sort(key=lambda move: self.calculate_distance(move[0], move[1]))
        return possible_moves[0]

    def calculate_distance(self, card, pile, bookings=False):
        top_card = self.piles[pile]['value']
        booking_penalty = self.hps['booking_penalties'][max(self.piles[pile]['bookings'])] if bookings else 0
        if pile.startswith('asc'):
            d = card - top_card
        elif pile.startswith('desc'):
            d = top_card - card
        return d + booking_penalty

    def end_turn(self, player, cards_played):
        self.draw_cards(player, cards_played)
        self.current_player = (self.current_player + 1) % len(self.hands)
        return self

    def reset(self):
        # Reset the state of the environment to an initial state
        self.deck = self.initialize_deck()
        self.hands = self.deal_hands(len(self.hands))
        self.piles = self.empty_piles
        self.played_cards = []
        self.current_player = 0

    def __repr__(self):
        return (f"Piles: {self.piles}, Hands: {self.hands}, Deck: {len(self.deck)} cards, "
                f"Current Player: {self.current_player}")

    def level_from_value(self, value):
        if value == -10:
            return 3
        if value < 5:
            return 2
        elif value < 12:
            return 1
        return 0

    def update_bookings(self):
        for i, hand in enumerate(self.hands):
            for key, pile in self.piles.items():
                for card in hand:
                    play_value = self.calculate_distance(card, key)
                    if play_value > 0 or play_value == -10:
                        play_value_level = self.level_from_value(play_value)
                        if play_value_level > self.piles[key]['bookings'][i]:
                            self.piles[key]['bookings'][i] = play_value_level

    def find_best_move(self, player):
        piles = self.piles.keys()

        possible_moves = []
        for card in self.hands[player]:
            for pile in piles:
                if self.is_valid_move(card, pile):
                    cost = self.calculate_distance(card, pile, bookings=True)
                    possible_moves.append((card, pile, cost))

        if not possible_moves:
            return None

        possible_moves.sort(key=lambda move: move[2])
        return possible_moves[0]



def basic_game(num_players):
    game_state = GameState(num_players)
    game_lost = False

    while not game_state.is_winning_state() and not game_lost:
        current_player = game_state.current_player
        cards_played = 0

        while cards_played < 2 or (len(game_state.deck) == 0 and cards_played < 1):
            closest_move = game_state.find_closest_move(current_player)
            if not closest_move:
                game_lost = True
                break  # No valid moves available, the game is lost
            card, pile = closest_move
            game_state.play_card(current_player, card, pile)
            cards_played += 1

        if not game_lost:
            game_state.end_turn(current_player, cards_played)
            # print(game_state)

    # print("Game Over!")
    if game_state.is_winning_state():
        print("You won!")
    else:
        print("No more valid moves available. You lost.")
    print(f"Cards left: {len(game_state.deck) + sum([len(hand) for hand in game_state.hands])}")
    return len(game_state.deck) + sum([len(hand) for hand in game_state.hands])


def lower_than_game(num_players, threshold, reserve=True):
    game_state = GameState(num_players)
    print(game_state)
    game_lost = False

    while not game_state.is_winning_state() and not game_lost:
        current_player = game_state.current_player
        cards_played = 0

        while cards_played < 2 or (len(game_state.deck) == 0 and cards_played < 1):
            closest_move = game_state.find_closest_move(current_player)
            if not closest_move:
                game_lost = True
                break  # No valid moves available, the game is lost
            card, pile = closest_move
            game_state.play_card(current_player, card, pile)
            # print(current_player, card, pile)
            cards_played += 1

        while game_state.find_closest_move(current_player):
            _piles = game_state.piles.copy()
            if reserve:
                for player in range(len(game_state.hands)):
                    try:
                        _card, _pile = game_state.find_closest_move(player)
                    except TypeError:
                        pass
                    # remove that pile from options when somebody else has a better card
                    if game_state.calculate_distance(_card, _pile) <= threshold:
                        try:
                            _piles.pop(_pile)
                        except KeyError:
                            pass
            try:
                card, pile = game_state.find_closest_move(current_player, piles=_piles)
            except TypeError:
                break
            if game_state.calculate_distance(card, pile) >= threshold:
                break
            elif game_state.calculate_distance(card, pile):
                game_state.play_card(current_player, card, pile)
                # print(current_player, card, pile)
                cards_played += 1

        if not game_lost:
            game_state.end_turn(current_player, cards_played)
            # print(game_state)

    # print("Game Over!")
    # if game_state.is_winning_state():
    #     print("You won!")
    # else:
    #     print("No more valid moves available. You lost.")
    # print(f"Cards left: {len(game_state.deck) + sum([len(hand) for hand in game_state.hands])}")
    return len(game_state.deck) + sum([len(hand) for hand in game_state.hands])


# results = [basic_game(3) for game in range(1000)]
# print('Average number of cards left:', sum(results) / len(results))
# print(f'Number of wins: {results.count(0)} in {len(results)} games ({results.count(0)/len(results) * 100 })')
# 0.5% wins with 23 cards left on average for a 3 player basic game


def game_with_bookings(num_players, hps):
    game_state = GameState(num_players, hps)
    print(game_state)
    game_lost = False

    while not game_state.is_winning_state() and not game_lost:
        current_player = game_state.current_player
        cards_played = 0

        while cards_played < 2 or (len(game_state.deck) == 0 and cards_played < 1):
            # find best move
            try:
                card, pile, cost = game_state.find_best_move(current_player)
            except TypeError:
                game_lost = True
                break

            # discussion
            print(game_state.hands[game_state.current_player])
            game_state.play_card(current_player, card, pile)
            game_state.update_bookings()
            print(current_player, card, pile)
            print(game_state.hands)
            print(game_state.piles)

            cards_played += 1

        if not game_lost:
            game_state.end_turn(current_player, cards_played)

    return len(game_state.deck) + sum([len(hand) for hand in game_state.hands])

hyperparameters = {
    'booking_penalties': {
        0: 0,
        1: 5,
        2: 10,
        3: 20
    }
}

if __name__ == "__main__":
    random.seed(42)
    num_players = 4
    print(f'-----hps: {hyperparameters}')
    results = [game_with_bookings(num_players, hps=hyperparameters) for game in range(1000)]
    print('Average number of cards left:', sum(results) / len(results))
    print(f'Number of wins for {num_players} players: {results.count(0)} in {len(results)} games ({results.count(0) / len(results) * 100})')
