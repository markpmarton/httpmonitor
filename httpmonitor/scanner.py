import re
import requests

from datetime import datetime

from .db_connector import DbConnector
from .logger import Logger
from .models import Job, Check

class HTTPScanner:
    job: Job
    check: Check
    response: requests.Response

    def __init__(self, job: Job):
        self.job = job

    def run(self, upload=True):
        self.scan_site()
        Logger.info(f"Job {self.job.name} started with params: {self.job.to_dict()}")
        
        if self.job.expected_regex:
            self.check_regex()

        if upload:
            self.send_check_for_upload()
            Logger.info(f"Job '{self.job.name}' finished with response: {self.check.to_dict()}")

    def scan_site(self):
        start_time = datetime.now()
        response = requests.request(
            method=str(self.job.method),
            headers=self.job.headers,
            url=self.job.url,
            data=self.job.body
        )

        self.response = response

        self.check = Check(
            job_name=self.job.name,
            start_time=start_time,
            end_time=start_time+response.elapsed,
            status_code=response.status_code,
            regex_result=""
        )

        Logger.info(f"Response received for job '{self.job.name}': {self.check.to_dict()}")

    def check_regex(self):
        re_pattern = r"{}".format(self.job.expected_regex)
        match = re.search(re_pattern, self.response.text)
        if match:
            self.check.regex_result = match.group(0)

    def send_check_for_upload(self):
        db_connector = DbConnector()
        db_connector.save_check_into_db(check=self.check)

        Logger.info(f"Response for job '{self.job.name}' uploaded to the database.")

