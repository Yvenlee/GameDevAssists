import pytest
from Notebooks.cleaner import traitement

def test_parse_hours_played():
    assert traitement.parse_hours_played("12.5 hrs") == 12.5
    assert traitement.parse_hours_played("3 h") == 3
    assert traitement.parse_hours_played("abc") is None

def test_clean_recommended():
    assert traitement.clean_recommended("Recommended") == 1
    assert traitement.clean_recommended("Non recommandé") == 0
    assert traitement.clean_recommended("unknown") is None