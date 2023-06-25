from httpmonitor.scheduler import Scheduler

def test_schedule_jobs():
    scheduler = Scheduler(from_file=False)
    scheduler.schedule_jobs()
    assert(len(scheduler.get_scheduled_jobs()) > 0)
