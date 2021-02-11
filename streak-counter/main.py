from h2o_wave import site, ui, Q, app, main
import time
import pandas as pd
from datetime import datetime


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

    async def start(self, q: Q):
        await self.stop(q)
        self.active = True
        self.total_streaks += 1
        q.page['UserStreaks'].data.streak_start = self.last_start = time.strftime("%Y-%m-%d  %H:%M:%S")
        q.page['UserStreaks'].data.streak_end = 'Streak on progress...'
        q.page['UserStreaks'].data.total_streaks = self.total_streaks

        q.page['stopwatch'].items[1].text_l.content = f"<center>You are amazing, keep up your good work...</center>"

        while self.minutes != 60 and self.active:
            if self.seconds == 59:
                self.minutes += 1
                self.seconds = 0
                q.page['stopwatch'].items[0].text_xl.content = f"<h1><center>{str(self.minutes).zfill(2)} : \
                    {str(self.seconds).zfill(2)}</center></h1>"

                await q.page.save()
            else:
                self.seconds += 1
                q.page['stopwatch'].items[0].text_xl.content = f"<h1><center>{str(self.minutes).zfill(2)} : \
                    {str(self.seconds).zfill(2)}</center></h1>"
                await q.page.save()
            time.sleep(1)

        q.page['stopwatch'].items[1].text_l.content = "<center>Awesome you have completed a streak!</center>"
        await self.stop(q)

    async def stop(self, q: Q):
        if self.active:
            self.active = False
            q.page['UserStreaks'].data.streak_end = self.last_stop = time.strftime("%Y-%m-%d  %H:%M:%S")
            self.update_total_time()
            self.minutes = self.seconds = 0
            q.page['stopwatch'].items[0].text_xl.content = f"<h1><center>{str(self.minutes).zfill(2)} : \
                {str(self.seconds).zfill(2)}</center></h1>"

            q.page['UserStreaks'].data.total_time = f"{str(self.total_hours).zfill(2)} :\
                            {str(self.total_minutes).zfill(2)} : {str(self.total_seconds).zfill(2)}"

            await q.page.save()

    def update_total_time(self):
        time_hr = time.strftime(
            "%H:%M:%S",
            time.gmtime(self.total_hours * 360 + self.total_minutes * 60 + self.total_seconds
                        + self.minutes * 60 + self.seconds)
        )
        self.total_hours = int(time_hr[0:2])
        self.total_minutes = int(time_hr[3:5])
        self.total_seconds = int(time_hr[6:])

    async def update_df(self, q: Q):
        duration = int((datetime.strptime(self.last_stop, '%Y-%m-%d %H:%M:%S') -
                        datetime.strptime(self.last_start, '%Y-%m-%d %H:%M:%S')).total_seconds())
        df2 = pd.DataFrame({
            'Started': [self.last_start],
            'Ended': [self.last_stop],
            'Duration': [duration],
            'Scores': [round(duration / 3600, 2)]
        })

        self.df = self.df.append(df2, ignore_index=True)
        q.page['history'].items[0].table.rows = [ui.table_row(
                name=str(row.Index + 1),
                cells=[str(row.Index + 1), row.Started, row.Ended, str(row.Duration), str(row.Scores)]
            ) for row in self.df.itertuples()]

        q.page['LeaderBoard'].items[0].text_xl.content = f"Your Total Score: {self.df['Scores'].sum()}"
        await q.page.save()


@app('/demo')
async def serve(q: Q):
    if not q.user.columns:
        q.user.columns = [
            ui.table_column(name='Index', label='Index', searchable=True, sortable=True, data_type='number'),
            ui.table_column(name='Started', label='Started', searchable=True),
            ui.table_column(name='Ended', label='Ended', searchable=True),
            ui.table_column(name='Duration', label='Duration (sec)', data_type='number'),
            ui.table_column(name='Scores', label='Scores', data_type='number'),
        ]

    if not q.client.LB_columns:
        q.client.LB_columns = [
            ui.table_column(name='User', label='User', searchable=True, max_width='100px'),
            ui.table_column(name='Scores', label='Scores', searchable=True, max_width='100px', sortable=True),
        ]

    if not q.user.stop_watch:
        q.user.stop_watch = StopWatch()

    if q.args.start and not q.user.stop_watch.active:
        await q.user.stop_watch.start(q)
    elif q.args.stop and q.user.stop_watch.active:
        await q.user.stop_watch.stop(q)
        await q.user.stop_watch.update_df(q)

    if not q.client.initialized:
        q.client.initialized = True
        await responsive_layout(q)
    await q.page.save()


async def responsive_layout(q: Q):
    q.page['meta'] = ui.meta_card(box='', layouts=[
        ui.layout(
            # If the viewport width >= 0:
            breakpoint='xs',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for content
                ui.zone('content')
            ]
        ),
        ui.layout(
            # If the viewport width >= 768:
            breakpoint='m',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    # 250px wide sidebar
                    ui.zone('sidebar', size='250px'),
                    # Use remaining space for content
                    ui.zone('content'),
                ]),
                ui.zone('footer'),
            ]
        ),
        ui.layout(
            # If the viewport width >= 1200:
            breakpoint='xl',
            width='1200px',
            zones=[
                # 80px high header
                ui.zone('header', size='80px'),
                # Use remaining space for body
                ui.zone('body', direction=ui.ZoneDirection.ROW, zones=[
                    # 300px wide sidebar
                    ui.zone('sidebar', size='300px'),
                    # Use remaining space for other widgets
                    ui.zone('other', zones=[
                        # Use one half for charts
                        ui.zone('charts', direction=ui.ZoneDirection.ROW),
                        # Use other half for content
                        ui.zone('content', size='500px'),
                    ]),
                ]),
                ui.zone('footer'),
            ]
        )
    ])

    q.page['header'] = ui.header_card(
        # Place card in the header zone, regardless of viewport size.
        box='header',
        title='Code Streak Counter',
        subtitle='Count your programming Streak while staying healthy !!!',
    )
    q.page['LeaderBoard'] = ui.form_card(
        # If the viewport width >= 0, place in content zone.
        # If the viewport width >= 768, place in sidebar zone.
        # If the viewport width >= 1200, place in sidebar zone.
        box=ui.boxes('content', 'sidebar', 'sidebar'),
        # title='Leader Board',
        items=[
            ui.text_l(
                content=f"Hi {q.auth.username.capitalize()}..!"
            ),
            ui.text_xl(
                content=f"Your Total Score: {q.user.stop_watch.df['Scores'].sum()}"
            ),
            ui.table(
                name='leaderboard',
                columns=q.client.LB_columns,
                rows=[],
                # rows=[ui.table_row(
                #     name=str(row.Index + 1),
                #     cells=[str(row.Index + 1), row.Started, row.Ended, str(row.Duration), str(row.Scores)]
                # ) for row in q.user.stop_watch.df.itertuples()],
                groupable=False,
                downloadable=True,
                resettable=False,
                height='425px'
            )
        ],
    )
    q.page['stopwatch'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as second item in content zone.
            ui.box(zone='content', order=2),
            # If the viewport width >= 768, place in content zone.
            'content',
            # If the viewport width >= 1200, place as first item in charts zone, use 2 parts of available space.
            ui.box(zone='charts', order=1, size=2),
        ),
        items=[
            ui.text_xl(
                content=f"<h1><center>{str(q.user.stop_watch.minutes).zfill(2)} : {str(q.user.stop_watch.seconds).zfill(2)}</center></h1>"
            ),
            ui.text_l(
                content=f"<center>Lets creak some code!</center>"
            ),
            ui.buttons([
                ui.button(name='start', label='Start', primary=True),
                ui.button(name='stop', label='Stop', primary=False)
            ], justify='center')
        ],
    )
    q.page['UserStreaks'] = ui.markdown_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 768, place as second item in content zone.
            ui.box(zone='content', order=2),
            # If the viewport width >= 1200, place as second item in charts zone, use 1 part of available space.
            ui.box(zone='charts', order=2, size=1),
        ),
        title='User Streaks',
        content="""=Last Streak Started: {{streak_start}}
        
Last Streak Ended: {{streak_end}}

Total Streaks: {{total_streaks}}

Total Coding Time: {{total_time}}
""",
        data=dict(streak_start=q.user.stop_watch.last_start,
                  streak_end=q.user.stop_watch.last_stop,
                  total_streaks=q.user.stop_watch.total_streaks,
                  total_time=f"{str(q.user.stop_watch.total_hours).zfill(2)} :\
                            {str(q.user.stop_watch.total_minutes).zfill(2)} : \
                            {str(q.user.stop_watch.total_seconds).zfill(2)}")
    )
    q.page['history'] = ui.form_card(
        box=ui.boxes(
            # If the viewport width >= 0, place as fourth item in content zone.
            ui.box(zone='content', order=4),
            # If the viewport width >= 768, place as third item in content zone.
            ui.box(zone='content', order=3),
            # If the viewport width >= 1200, place in content zone.
            'content'
        ),
        items=[
            ui.table(
                name='streaks_table',
                columns=q.user.columns,
                rows=[ui.table_row(
                    name=str(row.Index + 1),
                    cells=[str(row.Index + 1), row.Started, row.Ended, str(row.Duration), str(row.Scores)]
                ) for row in q.user.stop_watch.df.itertuples()],
                groupable=False,
                downloadable=True,
                resettable=False,
                height='425px'
            )
        ],
        title='History',
    )
    q.page['footer'] = ui.footer_card(box='footer', caption='(c) 2021 H2O.ai ')
