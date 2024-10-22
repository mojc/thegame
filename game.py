import random
from abc import ABC, abstractmethod

class Card:
    def __init__(self, value):
        self.value = value

class Pile:
    def __init__(self, initial_value, is_ascending, num_players):
        self.value = initial_value
        self.is_ascending = is_ascending
        self.bookings = [0 for _ in range(num_players)]

    def reset(self):
        self.bookings = [0 for _ in range(len(self.bookings))]

class Player:
    def __init__(self, hand=None):
        self.hand = hand or []

class GameState:
    def __init__(self, num_players, hps=None):
        self.deck = self.initialize_deck()
        self.players = [Player() for _ in range(num_players)]
        self.piles = {
            'asc1': Pile(1, True, num_players),
            'asc2': Pile(1, True, num_players),
            'desc1': Pile(100, False, num_players),
            'desc2': Pile(100, False, num_players),
        }
        self.played_cards = []
        self.current_player_index = 0
        self.hps = hps or {}
        self.shuffle_deck()
        self.deal_hands()

    def initialize_deck(self):
        return [Card(value) for value in range(2, 100)]

    def shuffle_deck(self):
        random.shuffle(self.deck)

    def deal_hands(self):
        hand_size = 8 if len(self.players) == 1 else 7 if len(self.players) == 2 else 6
        for player in self.players:
            player.hand = [self.deck.pop() for _ in range(hand_size)]

    def reset(self):
        self.deck = self.initialize_deck()
        self.shuffle_deck()
        self.deal_hands()
        for pile in self.piles.values():
            pile.reset()
        self.played_cards = []
        self.current_player_index = 0

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def draw_cards(self, player, num_cards):
        for _ in range(num_cards):
            if self.deck:
                player.hand.append(self.deck.pop())

    def __repr__(self):
        return (f"Piles: {self.piles}, Players: {self.players}, Deck: {len(self.deck)} cards, "
                f"Current Player: {self.current_player_index}")

class GameRules(ABC):
    @abstractmethod
    def is_valid_move(self, card, pile):
        pass

    @abstractmethod
    def calculate_distance(self, card, pile, bookings=False):
        pass

    @abstractmethod
    def update_bookings(self, game_state):
        pass

    @abstractmethod
    def find_best_move(self, player, game_state):
        pass

class StandardGameRules(GameRules):
    def __init__(self, hps):
        self.hps = hps

    def is_valid_move(self, card, pile):
        if pile.is_ascending:
            return card.value > pile.value or card.value == pile.value - 10
        else:
            return card.value < pile.value or card.value == pile.value + 10

    def calculate_distance(self, card, pile, bookings=False):
        booking_penalty = 0
        if bookings and pile.bookings:
            max_booking = max(pile.bookings)
            booking_penalty = self.hps.get('booking_penalties', {}).get(max_booking, 0)
        if pile.is_ascending:
            d = card.value - pile.value
        else:
            d = pile.value - card.value
        return d + booking_penalty

    def level_from_value(self, value):
        if value == -10:
            return 3
        if value < 5:
            return 2
        elif value < 12:
            return 1
        return 0

    def update_bookings(self, game_state):
        for i, player in enumerate(game_state.players):
            for pile_name, pile in game_state.piles.items():
                for card in player.hand:
                    play_value = self.calculate_distance(card, pile)
                    if play_value > 0 or play_value == -10:
                        play_value_level = self.level_from_value(play_value)
                        if play_value_level > pile.bookings[i]:
                            pile.bookings[i] = play_value_level
                            # Log the booking
                            print(f"Player {i} booked pile {pile_name} with level {play_value_level}")

    def find_best_move(self, player, game_state):
        possible_moves = []
        for card in player.hand:
            for pile_name, pile in game_state.piles.items():
                if self.is_valid_move(card, pile):
                    cost = self.calculate_distance(card, pile, bookings=True)
                    possible_moves.append((card, pile_name, cost))

        if not possible_moves:
            return None

        possible_moves.sort(key=lambda move: move[2])
        return possible_moves[0]

class GameEngine:
    def __init__(self, game_state, rules, max_cost_threshold):
        self.game_state = game_state
        self.rules = rules
        self.max_cost_threshold = max_cost_threshold

    def play_card(self, card, pile_name):
        pile = self.game_state.piles[pile_name]
        if self.rules.is_valid_move(card, pile):
            current_player_index = self.game_state.current_player_index
            print(f"Player {current_player_index} playing card {card.value} on pile {pile_name} (current value: {pile.value})")
            pile.value = card.value
            pile.reset()
            self.game_state.current_player.hand.remove(card)
            self.game_state.played_cards.append(card)
            return True
        return False

    def is_winning_state(self):
        return len(self.game_state.deck) == 0 and all(len(player.hand) == 0 for player in self.game_state.players)

    def end_turn(self, cards_played):
        self.game_state.draw_cards(self.game_state.current_player, cards_played)
        self.game_state.next_player()

    def play_game(self):
        game_lost = False

        while not self.is_winning_state() and not game_lost:
            current_player_index = self.game_state.current_player_index
            current_player_hand = [c.value for c in self.game_state.current_player.hand]
            print(f"Starting turn with hand: {current_player_hand} (Player {current_player_index}) ")

            cards_played = 0

            while True:
                best_move = self.rules.find_best_move(self.game_state.current_player, self.game_state)
                if not best_move:
                    if len(self.game_state.deck) == 0 and cards_played > 0:
                        break
                    game_lost = True
                    break

                card, pile_name, cost = best_move
                if cards_played >= 2 and cost > self.max_cost_threshold:
                    break

                self.play_card(card, pile_name)
                self.rules.update_bookings(self.game_state)
                cards_played += 1

            # Log the bookings at the end of the player's turn
            print(f"End of Player {current_player_index}'s turn. Current bookings:")
            for pile_name, pile in self.game_state.piles.items():
                print(f"  Pile {pile_name}: {pile.bookings}")

            if not game_lost:
                self.end_turn(cards_played)

        # Log the game result
        if self.is_winning_state():
            print("Game won! All cards have been played.")
        else:
            remaining_cards = len(self.game_state.deck) + sum(len(player.hand) for player in self.game_state.players)
            print(f"Game lost. Cards remaining: {remaining_cards}")

        return len(self.game_state.deck) + sum(len(player.hand) for player in self.game_state.players)

def run_game_with_bookings(num_players, hps):
    game_state = GameState(num_players, hps)
    rules = StandardGameRules(hps)
    max_cost_threshold = hps.get('max_cost_threshold', 5)  # Default to 5 if not specified
    engine = GameEngine(game_state, rules, max_cost_threshold)
    return engine.play_game()

if __name__ == "__main__":
    random.seed(42)
    num_players = 4
    hyperparameters = {
        'booking_penalties': {
            0: 0,
            1: 5,
            2: 10,
            3: 20
        },
        'max_cost_threshold': 5  # Add max_cost_threshold to hyperparameters
    }
    print(f'-----hps: {hyperparameters}')
    results = [run_game_with_bookings(num_players, hps=hyperparameters) for _ in range(1)]
    print('Average number of cards left:', sum(results) / len(results))
    print(f'Number of wins for {num_players} players: {results.count(0)} in {len(results)} games ({results.count(0) / len(results) * 100}%)')
