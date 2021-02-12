from h2o_wave import site, ui, Q, app, main
from utils.ui_updates import responsive_layout
from utils.StopWatch import StopWatch


@app('/demo')
async def serve(q: Q):
    if not q.app.lb_dict:
        q.app.lb_dict = dict()

    if not q.user.stop_watch:
        q.user.stop_watch = StopWatch()

    if q.args.start and not q.user.stop_watch.active:
        await q.user.stop_watch.start(q)
    elif q.args.stop and q.user.stop_watch.active:
        await q.user.stop_watch.stop(q)
        await q.user.stop_watch.update_df(q)
        await q.user.stop_watch.update_lb(q)

    if not q.client.initialized:
        q.client.initialized = True
        await responsive_layout(q)
        await q.user.stop_watch.update_lb(q)
    await q.page.save()



