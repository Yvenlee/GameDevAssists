from Notebooks.display import game_selector

def test_paginate_games():
    games = ["a", "b", "c", "d", "e"]
    assert game_selector.paginate_games(games, 0, per_page=2) == ["a", "b"]
    assert game_selector.paginate_games(games, 1, per_page=2) == ["c", "d"]