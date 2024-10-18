import random
from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class Card:
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Card({self.value})"

class Pile(ABC):
    def __init__(self, initial_value: int):
        self.value = initial_value
        self.cards: List[Card] = []

    @abstractmethod
    def can_play(self, card: Card) -> bool:
        pass

    def play(self, card: Card) -> None:
        if self.can_play(card):
            self.cards.append(card)
            self.value = card.value
        else:
            raise ValueError("Invalid move")

class AscendingPile(Pile):
    def can_play(self, card: Card) -> bool:
        return card.value > self.value or card.value == self.value - 10

class DescendingPile(Pile):
    def can_play(self, card: Card) -> bool:
        return card.value < self.value or card.value == self.value + 10

class Deck:
    def __init__(self):
        self.cards = [Card(i) for i in range(2, 100)]
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

    def is_empty(self) -> bool:
        return len(self.cards) == 0

class Player:
    def __init__(self, name: str):
        self.name = name
        self.hand: List[Card] = []

    def add_card(self, card: Card) -> None:
        self.hand.append(card)

    def play_card(self, card: Card) -> None:
        self.hand.remove(card)

    def has_cards(self) -> bool:
        return len(self.hand) > 0

class Game:
    def __init__(self, num_players: int):
        self.deck = Deck()
        self.players = [Player(f"Player {i+1}") for i in range(num_players)]
        self.piles = {
            'asc1': AscendingPile(1),
            'asc2': AscendingPile(1),
            'desc1': DescendingPile(100),
            'desc2': DescendingPile(100)
        }
        self.current_player_index = 0
        self.deal_initial_hands()

    def deal_initial_hands(self) -> None:
        cards_per_player = 8 if len(self.players) == 1 else 7 if len(self.players) == 2 else 6
        for player in self.players:
            for _ in range(cards_per_player):
                player.add_card(self.deck.draw())

    def play_turn(self) -> bool:
        player = self.players[self.current_player_index]
        cards_played = 0
        min_cards_to_play = 2 if not self.deck.is_empty() else 1

        while cards_played < min_cards_to_play or (player.has_cards() and self.can_play(player)):
            move = self.find_best_move(player)
            if move is None:
                return False
            card, pile = move
            self.piles[pile].play(card)
            player.play_card(card)
            print(player.name, card, pile)
            cards_played += 1

        self.draw_cards(player, cards_played)
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        return True

    def can_play(self, player: Player) -> bool:
        return any(self.find_best_move(player) is not None for pile in self.piles.values())

    def find_best_move(self, player: Player) -> Tuple[Card, str]:
        best_move = None
        best_distance = float('inf')

        for card in player.hand:
            for pile_name, pile in self.piles.items():
                if pile.can_play(card):
                    distance = abs(card.value - pile.value)
                    if distance < best_distance:
                        best_distance = distance
                        best_move = (card, pile_name)

        return best_move

    def draw_cards(self, player: Player, num_cards: int) -> None:
        for _ in range(num_cards):
            if not self.deck.is_empty():
                player.add_card(self.deck.draw())

    def is_game_over(self) -> bool:
        return all(not player.has_cards() for player in self.players) or not self.can_play(self.players[self.current_player_index])

    def play_game(self) -> int:
        while not self.is_game_over():
            if not self.play_turn():
                break

        return sum(len(player.hand) for player in self.players) + len(self.deck.cards)

def run_games(num_games: int, num_players: int) -> None:
    results = []
    for game_number in range(num_games):
        print(f"Starting game {game_number + 1}")
        game = Game(num_players)
        
        def log_move(player, card, pile):
            print(f"Game {game_number + 1}: {player.name} played {card} on pile {pile}")
        
        game.print = log_move
        
        result = game.play_game()
        results.append(result)
        print(f"Game {game_number + 1} finished with {result} cards left")
    avg_cards_left = sum(results) / len(results)
    num_wins = results.count(0)
    win_percentage = (num_wins / len(results)) * 100

    print(f"Average number of cards left: {avg_cards_left:.2f}")
    print(f"Number of wins: {num_wins} in {len(results)} games ({win_percentage:.2f}%)")

if __name__ == "__main__":
    random.seed(42)
    run_games(2, 4)
