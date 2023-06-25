import json
import os

from http import HTTPMethod
from typing import List

from .errors import InvalidFilenameException
from .config_handler import ConfigHandler
from .const import JOBS_PATH
from .db_connector import DbConnector
from .logger import Logger
from .models import Job


class JobHandler:

    jobs_path: str
    jobs: List[Job] = []
    
    def __init__(self, jobs_path: str = JOBS_PATH, from_file: bool = False):
        config_handler = ConfigHandler()
        self.jobs_path = os.path.join(config_handler.working_dir,jobs_path)

        if from_file:
            if not os.path.exists(self.jobs_path):
                raise InvalidFilenameException(file_name=self.jobs_path)

            self.read_jobs_from_file()
            self.save_to_database()
        else:
            self.load_all_from_database()

    def read_jobs_from_file(self):
        jobs_dict = {}
        with open(self.jobs_path) as reader:
            jobs_dict = json.load(reader)["jobs"] 

        for act_job_dict in jobs_dict:
            self.jobs.append(    
                Job(name=act_job_dict["name"] if "name" in act_job_dict else "",
                    url=act_job_dict["url"] if "url" in act_job_dict else "",
                    method=HTTPMethod(act_job_dict["method"] if "method" in act_job_dict else ""),
                    headers=act_job_dict["headers"] if "headers" in act_job_dict else {},
                    body=act_job_dict["body"] if "url" in act_job_dict else {},
                    scheduled_interval=int(act_job_dict["scheduled_interval"] if "url" in act_job_dict else ""),
                    expected_regex=str(act_job_dict["expected_regex"]) if "expected_regex" in act_job_dict else None
                ))
        Logger.debug("Jobs read from file")

    def save_to_database(self):
        db_connector = DbConnector()
        for act_job in self.jobs:
            db_connector.save_job_into_db(act_job)
        Logger.debug("Jobs saved to the database")

    def load_all_from_database(self):
        db_connector = DbConnector()
        self.jobs = db_connector.get_jobs_from_db()

    def get_by_name(self, job_name: str) -> Job | None:
        if len(self.jobs) == 0:
            self.read_jobs_from_file()
        for act_job in self.jobs:
            if act_job.name == job_name:
                return act_job

