from httpmonitor.models import Job
from httpmonitor.scanner import HTTPScanner

def test_scan_site():
    job = Job(name="test_job",
            url="https://example.org",
            method="GET",
            headers={},
            body={},
            scheduled_interval=50,
            expected_regex="")

    scanner = HTTPScanner(job)
    scanner.scan_site()
    assert(scanner.check.status_code > 100)

def test_check_regex():
    job = Job(name="test_job",
            url="https://wikipedia.org",
            method="GET",
            headers={},
            body={},
            scheduled_interval=50,
            expected_regex="<.+?The Free Encyclopedia.+?>")

    scanner = HTTPScanner(job)
    scanner.run(upload=False)
    assert(len(str(scanner.check.regex_result)) > 0)
