import random

class GameState:
    def __init__(self, num_players):
        self.deck = self.initialize_deck()
        self.hands = self.deal_hands(num_players)
        self.piles = {
            'asc1': 1,
            'asc2': 1,
            'desc1': 100,
            'desc2': 100
        }
        self.played_cards = []
        self.current_player = 0

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
        top_card = self.piles[pile]
        if pile.startswith('asc'):
            return card > top_card or card == top_card - 10
        elif pile.startswith('desc'):
            return card < top_card or card == top_card + 10
        return False

    def play_card(self, player, card, pile):
        # Play a card on the specified pile if the move is valid
        if self.is_valid_move(card, pile):
            self.piles[pile] = card
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

    def get_possible_moves(self, player):
        # Generate all possible moves for a player
        possible_moves = []
        for card in self.hands[player]:
            for pile in self.piles:
                if self.is_valid_move(card, pile):
                    possible_moves.append((card, pile))
        return possible_moves

    def find_closest_move(self, player):
        # Find the optimal move based on the smallest distance to the piles
        possible_moves = self.get_possible_moves(player)
        if not possible_moves:
            return None
        possible_moves.sort(key=lambda move: self.calculate_distance(move[0], move[1]))
        return possible_moves[0]

    def calculate_distance(self, card, pile):
        top_card = self.piles[pile]
        if pile.startswith('asc'):
            return card - top_card
        elif pile.startswith('desc'):
            return top_card - card 

    def end_turn(self, player, cards_played):
        self.draw_cards(player, cards_played)
        self.current_player = (self.current_player + 1) % len(self.hands)
        return self

    def reset(self):
        # Reset the state of the environment to an initial state
        self.deck = self.initialize_deck()
        self.hands = self.deal_hands(len(self.hands))
        self.piles = {'asc1': 1, 'asc2': 1, 'desc1': 100, 'desc2': 100}
        self.played_cards = []
        self.current_player = 0

    def __repr__(self):
        return (f"Piles: {self.piles}, Hands: {self.hands}, Deck: {len(self.deck)} cards, "
                f"Current Player: {self.current_player}")

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


results = [basic_game(3) for game in range(1000)]

print('Average number of cards left:', sum(results) / len(results))
print(f'Number of wins: {results.count(0)} in {len(results)} games ({results.count(0)/len(results) * 100 })')
# 0.5% wins with 23 cards left on average for a 3 player basic game