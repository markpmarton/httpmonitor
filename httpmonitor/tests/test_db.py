from datetime import datetime

from httpmonitor.db_connector import DbConnector
from httpmonitor.models import Job, Check
from httpmonitor.job_handler import JobHandler

def test_db_save_and_get_job_from_db():
    db_connector = DbConnector()
    job = Job(name="test_job",
            url="https://google.com",
            method="GET",
            headers={},
            body={},
            scheduled_interval=100,
            expected_regex="")
    db_connector.save_job_into_db(job)
    result = db_connector.get_job_from_db(job_name="test_job")
    assert(result[0] > 0 and result[1] != None)

def test_db_get_jobs_from_db():
    db_connector = DbConnector()
    job = Job(name="test_job",
            url="https://google.com",
            method="GET",
            headers={},
            body={},
            scheduled_interval=100,
            expected_regex="")
    db_connector.save_job_into_db(job)
    job = Job(name="test_job2",
            url="https://google.com",
            method="GET",
            headers={},
            body={},
            scheduled_interval=100,
            expected_regex="")
    db_connector.save_job_into_db(job)
    jobs = db_connector.get_jobs_from_db()
    assert(len(jobs) > 1)

def test_db_save_check_into_db():
    db_connector = DbConnector()
    check = Check(
        job_name="test_job",
        start_time=datetime.now(),
        end_time=datetime.now(),
        status_code=100,
        regex_result=""
    )
    db_connector.save_check_into_db(check=check)

    #Cleaning up the database
    job_handler = JobHandler(from_file=True)
    job_handler.read_jobs_from_file()
