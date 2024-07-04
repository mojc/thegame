import random
from tg_str import Player

class GameState:
    def __init__(self, num_players, hps=None):
        self.deck = self.initialize_deck()
        self.hands = self.deal_hands(num_players)
        self.players = [Player(i) for i in range(num_players)]
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
        self.draw_cards(player.idx, cards_played)
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



def game(num_players):
    game_state = GameState(num_players)
    game_lost = False

    while not game_state.is_winning_state() and not game_lost:
        current_player_idx = game_state.current_player
        current_player = game_state.players[current_player_idx]
        cards_played = 0
        player_pass = False

        while not player_pass:
            name, card, pile_name = current_player.query_action(hand=game_state.hands[current_player_idx],
                                                           piles=game_state.piles,
                                                           cards_played=cards_played)

            if name == 'pass':
                player_pass = True
                if cards_played < 2:
                    game_lost = True
                game_state.end_turn(current_player, cards_played)

            if name == 'play':
                game_state.play_card(current_player.idx, card, pile_name)
                cards_played += 1
                print(current_player.idx, card, pile_name)
                print(game_state.hands)
                print(game_state.piles)

                # Only discuss if smtg was played?
                for player in game_state.players:
                    player.discuss(game_state.hands[player.idx], game_state.piles)

                pass



    if game_state.is_winning_state():
        print("You won!")
    else:
        print("No more valid moves available. You lost.")
    print(f"Cards left: {len(game_state.deck) + sum([len(hand) for hand in game_state.hands])}")
    return len(game_state.deck) + sum([len(hand) for hand in game_state.hands])



if __name__ == "__main__":
    random.seed(42)
    num_players = 4
    results = [game(num_players) for _ in range(100)]
    print('Average number of cards left:', sum(results) / len(results))
    print(f'Number of wins for {num_players} players: {results.count(0)} in {len(results)} games ({results.count(0) / len(results) * 100})')
