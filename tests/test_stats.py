import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Notebooks')))

from Notebooks.dashboard import stats

def test_get_similar_to_game_name_empty():
    assert stats.get_similar_to_game_name("test", []) == set()

def test_get_similar_to_game_name_no_match():
    assert stats.get_similar_to_game_name("test", ["unrelated comment"]) == set()

def test_get_similar_to_game_name_partial_match():
    assert stats.get_similar_to_game_name("test", ["this is a test comment"]) == {"test"}

def test_get_similar_to_game_name_multiple_matches():
    assert stats.get_similar_to_game_name("test", ["this is a test comment", "another test"]) == {"test"}
