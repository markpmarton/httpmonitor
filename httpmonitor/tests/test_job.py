import json
import os
import pytest

from httpmonitor.errors import InvalidFilenameException, ValidatorException

from httpmonitor.job_handler import JobHandler 
from httpmonitor.config_handler import ConfigHandler

def test_init_from_database():
    job_handler = JobHandler()
    assert(len(job_handler.jobs) > 0)

def test_init_from_file():
    job_file_path = "../temp_job.json"
    config_handler = ConfigHandler()
    config_handler.deploy_default_jobs_config(out_filepath=job_file_path)
    job_handler = JobHandler(jobs_path=job_file_path, from_file=True)
    assert(len(job_handler.jobs) > 0)
    os.remove("temp_job.json")

def test_init_from_file_bad_jobs_path():
    with pytest.raises(InvalidFilenameException):
        JobHandler(jobs_path="bad_jobs.json", from_file=True)

def test_read_from_bad_file():
    bad_jobs = {
        "jobs": [
            {
                "name1": "example_job",
                "url": "https://cnn.com",
                "method": "GET",
                "headers": {},
                "body": {},
                "expected_regex": "",
                "scheduled_interval": 30
            }
        ]
    }
    with open("../bad_jobs.json", "w") as writer:
        json.dump(bad_jobs, writer)

    with pytest.raises(ValidatorException):
        JobHandler(jobs_path="../bad_jobs.json", from_file=True) 
    os.remove("../bad_jobs.json")
