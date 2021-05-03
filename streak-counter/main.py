from h2o_wave import site, ui, Q, app, main
from utils import ui_updates as U
from utils.StopWatch import StopWatch


@app('/demo')
async def serve(q: Q):
    if not q.app.lb_dict:
        q.app.lb_dict = dict()

    if not q.user.stop_watch:
        q.user.stop_watch = StopWatch()

    if q.args.start and not q.user.stop_watch.active:
        await U.start_clock(q.user.stop_watch, q)

        q.user.stop_watch.update_df()
        await U.update_streak_history(q.user.stop_watch, q)

        await U.update_leaderboard(q)
    elif q.args.stop and q.user.stop_watch.active:
        q.user.stop_watch.stop()
        await U.update_stop_streak(q.user.stop_watch, q)

        # q.user.stop_watch.update_df()
        # await U.update_streak_history(q.user.stop_watch, q)
        #
        # await U.update_leaderboard(q)

    if not q.client.initialized:
        q.client.initialized = True
        await U.responsive_layout(q)
        await U.update_leaderboard(q)
    await q.page.save()