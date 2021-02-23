from playwright.sync_api import Page
from .helper import click, has_text, see
import time


def test_streak_ui(page: Page):
    page.goto("http://localhost:10101/demo")

    click(page, "start")
    time.sleep(2)
    has_text(page, "UserStreaks_Last_Ended", 'Last Streak Ended: Streak on progress...')
    has_text(page, "stopwatch", 'You are amazing, keep up your good work...')
    time.sleep(8)
    has_text(page, "stopwatch", 'Awesome you have completed a streak!')
    has_text(page, "UserStreaks_Total_Streaks", "Total Streaks: 1")