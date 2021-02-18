import pytest
from utils.StopWatch import StopWatch
import time
from typing import Callable

callback_flag = False


@pytest.fixture(scope="function")
def stopwatch() -> StopWatch:
    return StopWatch()


@pytest.fixture(scope="function")
def callback() -> Callable:
    async def on_update(minutes: int, seconds: int):
        pass

    return on_update


@pytest.mark.asyncio
async def test_stopwatch_ends_at_expected_time(stopwatch, callback):
    start_time = time.time()
    await stopwatch.start(on_update=callback, sec=5)
    end_time = time.time()

    assert int(end_time - start_time) == 5


@pytest.mark.asyncio
async def test_stopwatch_start_callback(stopwatch):
    global callback_flag

    async def on_update(minutes: int, seconds: int):
        global callback_flag
        callback_flag = True

    await stopwatch.start(on_update=on_update, sec=2)
    assert callback_flag is True

    # reset callback_flag
    callback_flag = False


@pytest.mark.asyncio
async def test_stopwatch_updates_data_on_stop(stopwatch, callback):
    assert stopwatch.total_hours == 0
    assert stopwatch.total_minutes == 0
    assert stopwatch.total_seconds == 0
    assert stopwatch.total_streaks == 0

    await stopwatch.start(on_update=callback, sec=2)
    assert stopwatch.total_hours == 0
    assert stopwatch.total_minutes == 0
    assert stopwatch.total_seconds == 2
    assert stopwatch.total_streaks == 1


def test_stopwatch_stop(stopwatch):
    stopwatch.active = True
    stopwatch.stop()

    assert stopwatch.active is False
    assert stopwatch.seconds == 0
    assert stopwatch.minutes == 0


def test_stopwatch_update_df(stopwatch):
    stopwatch.last_start = time.strftime("%Y-%m-%d  %H:%M:%S")
    time.sleep(3)
    stopwatch.last_stop = time.strftime("%Y-%m-%d  %H:%M:%S")

    stopwatch.update_df()

    assert stopwatch.df['Started'][0] == stopwatch.last_start
    assert stopwatch.df['Ended'][0] == stopwatch.last_stop
    assert stopwatch.df['Duration'][0] == 0.05
    assert stopwatch.df['Scores'][0] == 1
