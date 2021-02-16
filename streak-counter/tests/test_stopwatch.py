import pytest
from utils.StopWatch import StopWatch
from h2o_wave import Q


@pytest.mark.asyncio
async def test_start():
    sw = StopWatch()
    q = None

    total_streaks = sw.total_streaks

    await sw.start(q, test=True)
    assert sw.active is False
    assert sw.seconds == 0
    assert sw.minutes == 0
    assert sw.total_streaks == total_streaks + 1


def test_stop():
    sw = StopWatch()
    sw.active = True
    sw.seconds = 5
    sw.minutes = 5

    sw.stop()

    assert sw.active is False
    assert sw.seconds == 0
    assert sw.minutes == 0
    assert sw.total_minutes == 5
    assert sw.total_seconds == 5


def test_update_total_time():
    sw = StopWatch()
    sw.seconds = 10
    sw.minutes = 60

    sw.update_total_time()

    assert sw.total_hours == 1
    assert sw.total_minutes == 0
    assert sw.total_seconds == 10
