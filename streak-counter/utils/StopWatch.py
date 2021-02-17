from h2o_wave import site, ui, Q, app, main
import time
import pandas as pd
from datetime import datetime
from . import ui_updates as U
from typing import Callable


class StopWatch:
    def __init__(self):
        self.minutes = 0
        self.seconds = 0
        self.total_minutes = 0
        self.total_seconds = 0
        self.total_hours = 0
        self.active = False
        self.total_streaks = 0
        self.last_start = None
        self.last_stop = None
        self.df = pd.DataFrame(columns=['Started', 'Ended', 'Duration', 'Scores'])

    async def start(self, on_update: Callable, sec: int = 60):
        self.stop()
        self.active = True
        self.total_streaks += 1

        while self.minutes < 60 and self.active and self.seconds < sec:
            if self.seconds >= 59:
                self.minutes += 1
                self.seconds = 0

                await on_update(self.minutes, self.seconds)
            else:
                self.seconds += 1
                await on_update(self.minutes, self.seconds)

            time.sleep(1)

        self.stop()

    def stop(self):
        if self.active:
            self.active = False
            self.update_total_time()
            self.minutes = self.seconds = 0

    def update_total_time(self):
        time_hr = time.strftime(
            "%H:%M:%S",
            time.gmtime(self.total_hours * 360 + self.total_minutes * 60 + self.total_seconds
                        + self.minutes * 60 + self.seconds)
        )
        self.total_hours = int(time_hr[0:2])
        self.total_minutes = int(time_hr[3:5])
        self.total_seconds = int(time_hr[6:])

    def update_df(self):
        duration = round(int((datetime.strptime(self.last_stop, '%Y-%m-%d %H:%M:%S') -
                              datetime.strptime(self.last_start, '%Y-%m-%d %H:%M:%S')).total_seconds()) / 60, 2)
        df2 = pd.DataFrame({
            'Started': [self.last_start],
            'Ended': [self.last_stop],
            'Duration': [duration],
            'Scores': [duration if duration > 1 else 1]
        })

        self.df = self.df.append(df2, ignore_index=True)
