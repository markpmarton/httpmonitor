import schedule
import time

from multiprocessing import Process
from typing import List

from .config_handler import ConfigHandler
from .job_handler import JobHandler
from .models import Job
from .scanner import HTTPScanner

class Scheduler:
    job_handler: JobHandler
    config_handler: ConfigHandler
    scheduled_jobs: List[Job]
    scan_process: Process

    def __init__(self, from_file: bool):
        self.job_handler = JobHandler(from_file=from_file)
        self.config_handler = ConfigHandler()
        self.scheduled_jobs = self.get_scheduled_jobs()

    def get_scheduled_jobs(self) -> List[Job]:
        return self.job_handler.jobs

    def schedule_jobs(self):
        #Scheduling jobs with using the 'schedule' package (https://github.com/dbader/schedule)
        for act_job in self.scheduled_jobs:
            scan_job = HTTPScanner(job=act_job)
            schedule.every(int(act_job.scheduled_interval)).seconds.do(scan_job.run)

        scan_process = Process(target=self.process_task)
        self.scan_process = scan_process

    def process_task(self):
        while True:
            schedule.run_pending()
            time.sleep(1)

