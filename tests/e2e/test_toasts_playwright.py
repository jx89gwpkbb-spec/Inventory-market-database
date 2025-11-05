import pytest
from playwright.sync_api import sync_playwright

@pytest.mark.skip(reason="Run in CI where app is started")
def test_homepage_loads():
    # This is a placeholder E2E test; CI should start the app before running.
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto('http://127.0.0.1:8000/')
        assert page.title() is not None
        browser.close()
