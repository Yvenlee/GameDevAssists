from unittest.mock import MagicMock, patch
from Notebooks.scraping import scrapingfusion

@patch("Notebooks.scraping.scrapingfusion.webdriver.Chrome")
def test_setup_driver(mock_chrome):
    driver = scrapingfusion.setup_driver()
    assert mock_chrome.called