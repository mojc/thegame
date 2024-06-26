
from tg import GameState
import random



def test_update_bookings():
    gs = GameState(2)
    gs.hands = [[44, 45], [3, 65]]
    gs.piles['desc2'] = {'value': 55, 'bookings': [0, 0]}
    gs.update_bookings()

    assert gs.piles['asc1']['bookings'] == [0, 2]
    assert gs.piles['asc2']['bookings'] == [0, 2]
    assert gs.piles['desc1']['bookings'] == [0, 0]
    assert gs.piles['desc2']['bookings'] == [1, 3]

    gs = GameState(2)
    gs.hands = [[57, 56], [75, 65]]
    gs.piles['desc2'] = {'value': 55, 'bookings': [0, 0]}
    gs.update_bookings()

    assert gs.piles['asc1']['bookings'] == [0, 0]
    assert gs.piles['asc2']['bookings'] == [0, 0]
    assert gs.piles['desc1']['bookings'] == [0, 0]
    assert gs.piles['desc2']['bookings'] == [0, 3] # could be 4!


def test_calculate_distance():
    random.seed(42)
    gs = GameState(2)
    assert 1 == gs.calculate_distance(card=2, pile='asc1')
    gs.piles['desc2'] = {'value': 55, 'bookings': [0, 0]}
    assert -10 == gs.calculate_distance(card=65, pile='desc2')
    gs.piles['desc2'] = {'value': 96, 'bookings': [0, 0]}
    assert -1 == gs.calculate_distance(card=97, pile='desc2')
