from . import StopWatch
import time
from h2o_wave import Q, ui


async def update_start_streak(sw: StopWatch, q: Q):
    q.page['UserStreaks'].data.streak_start = sw.last_start = time.strftime("%Y-%m-%d  %H:%M:%S")
    q.page['UserStreaks'].data.streak_end = 'Streak on progress...'

    await q.page.save()


async def update_clock_msg(q: Q, msg):
    if msg.upper() == 'ON_GOING':
        q.page['stopwatch'].items[1].text_l.content = "<center>You are amazing, keep up your good work...</center>"
    elif msg.upper() == 'END':
        q.page['stopwatch'].items[1].text_l.content = "<center>Awesome you have completed a streak!</center>"

    await q.page.save()


async def update_clock(q: Q, current_minute: int, current_sec: int):
    q.page['stopwatch'].items[0].text_xl.content = f"<h1><center>{str(current_minute).zfill(2)} : \
                        {str(current_sec).zfill(2)}</center></h1>"
    await q.page.save()


async def update_stop_streak(sw: StopWatch, q: Q):
    q.page['UserStreaks'].data.streak_end = sw.last_stop = time.strftime("%Y-%m-%d  %H:%M:%S")

    q.page['stopwatch'].items[0].text_xl.content = f"<h1><center>{str(sw.minutes).zfill(2)} : \
                    {str(sw.seconds).zfill(2)}</center></h1>"

    q.page['UserStreaks'].data.total_time = f"{str(sw.total_hours).zfill(2)} :\
                                {str(sw.total_minutes).zfill(2)} : {str(sw.total_seconds).zfill(2)}"
    q.page['UserStreaks'].data.total_streaks = sw.total_streaks
    await q.page.save()


async def update_streak_history(sw: StopWatch, q: Q):
    q.page['history'].items[0].table.rows = [ui.table_row(
        name=str(row.Index + 1),
        cells=[str(row.Index + 1), row.Started, row.Ended, str(row.Duration), str(row.Scores)]
    ) for row in sw.df.itertuples()]

    q.page['LeaderBoard'].items[0].text_xl.content = f"Your Total Score: {sw.df['Scores'].sum()}"

    q.app.lb_dict[q.auth.username] = sw.df['Scores'].sum()

    await q.page.save()


async def update_leaderboard(q: Q):
    q.page['LeaderBoard'].items[2].table.rows = [ui.table_row(
        name=user,
        cells=[user, str(score)]
    ) for user, score in q.app.lb_dict.items()]

    await q.page.save()


async def start_clock(sw: StopWatch, q: Q):
    async def on_clock_update(current_minute: int, current_sec: int):
        await update_clock(q, current_minute, current_sec)

    await update_start_streak(sw, q)
    await update_clock_msg(q, 'ON_GOING')
    await sw.start(on_update=on_clock_update, sec=10)
    await update_stop_streak(sw, q)
    await update_clock_msg(q, 'END')


async def responsive_layout(q: Q):
    if not q.user.columns:
        q.user.columns = [
            ui.table_column(name='Index', label='Index', searchable=True, sortable=True, data_type='number'),
            ui.table_column(name='Started', label='Started', searchable=True),
            ui.table_column(name='Ended', label='Ended', searchable=True),
            ui.table_column(name='Duration', label='Duration (mins)', data_type='number'),
            ui.table_column(name='Scores', label='Scores', data_type='number'),
        ]

    if not q.client.LB_columns:
        q.client.LB_columns = [
            ui.table_column(name='User', label='User', searchable=True, max_width='100px'),
            ui.table_column(name='Scores', label='Scores', searchable=True, max_width='100px', sortable=True),
        ]

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
                rows=[ui.table_row(
                    name=user,
                    cells=[user, str(score)]
                ) for user, score in q.app.lb_dict.items()],
                groupable=False,
                downloadable=True,
                resettable=False,
                height='425px',
            ),
            ui.link(name='logout', label='Log Out', button=True, path=f'/_logout', target='_current')
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
