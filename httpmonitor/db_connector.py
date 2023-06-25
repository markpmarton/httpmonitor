import json
import psycopg2

from psycopg2 import OperationalError
from psycopg2.sql import SQL, Identifier, Literal
from psycopg2.extensions import cursor
from typing import List, Tuple

from .logger import Logger
from .config_handler import ConfigHandler
from .enums import DbUserType
from .errors import UserAlreadyExistsException, SetupRequiredException
from .models import Check, DbCredentials, Job

class DbConnector:
    def __init__(self):
        self.config = ConfigHandler()

    def __connect(self, user_type: DbUserType, db_name = None) -> cursor:
        try:
            conn = psycopg2.connect(
                host=self.config.db_url,
                database=db_name if db_name else self.config.db_name,
                port=self.config.db_port,
                user=self.config.get_username(user_type=user_type),
                password=self.config.get_password(user_type=user_type),
                sslmode='require'
            )
            conn.autocommit = True
            return conn.cursor()
        except OperationalError as e:
            Logger.error(e)
            raise SetupRequiredException()
        except Exception as e:
            raise NotImplemented(e)
            

    def user_exists(self, username) -> bool:
        cur = self.__connect(user_type=DbUserType.Connector)
        q_exists = SQL("SELECT 1 FROM pg_roles WHERE rolname=%s;")
        cur.execute(q_exists, (username,))
        match cur.fetchone():
            case None:
                return False
            case (1,):
                return True
            case _:
                raise NotImplementedError

    def init_database(self):
        query_create_db = SQL("""
        CREATE DATABASE {db_name};
        """).format(db_name=Identifier(self.config.db_name))
        self.__connect(user_type=DbUserType.Connector, db_name=self.config.db_name_default).execute(query_create_db)

        query_init = SQL("""
        CREATE SCHEMA {db_name}
            CREATE TABLE {db_name}.regex_raw (
                id SERIAL PRIMARY KEY,
                raw_finding TEXT
            )
            CREATE TABLE {db_name}.jobs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                url VARCHAR(200) NOT NULL,
                method VARCHAR(10) NOT NULL,
                headers TEXT,
                body TEXT,
                expected_regex VARCHAR(100),
                scheduled_interval INT DEFAULT 60
            )
            CREATE TABLE {db_name}.checks (
                id SERIAL PRIMARY KEY,
                job_id INT REFERENCES jobs(id),
                start_ts TIMESTAMP NOT NULL,
                end_ts TIMESTAMP NOT NULL,
                status_code INT NOT NULL,
                regex_result_id INT REFERENCES regex_raw(id)
            )
            """).format(db_name=Identifier(self.config.db_name))
        self.__connect(user_type=DbUserType.Connector).execute(query_init)

    def drop_database(self, schema_name: str):
        query_drop_schema = SQL("""
        DROP SCHEMA {schema_name} CASCADE;
        """).format(schema_name=Identifier(schema_name))
        self.__connect(user_type=DbUserType.Connector).execute(query_drop_schema)

    def create_user(self, user_creds: DbCredentials):
        try:
            if not self.user_exists(user_creds.username):
                cursor = self.__connect(user_type=DbUserType.Connector)

                #Creating user
                query_create_user = SQL("CREATE ROLE {username} LOGIN PASSWORD {password};").format(
                    username=Identifier(user_creds.username),
                    password=Literal(user_creds.password)
                )
                cursor.execute(query_create_user)

                #Granting default access
                query_grant_access = SQL("""
                    GRANT CONNECT ON DATABASE {db_name} TO {username};
                    GRANT USAGE ON SCHEMA {db_name} TO {username};
                    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA {db_name} TO {username};
                """).format(
                    db_name=Identifier(self.config.db_name),
                    username=Identifier(user_creds.username)
                )
                cursor.execute(query_grant_access)

                #Granting DQL or DML roles
                query_grant_permissions = ""
                match user_creds.type:
                    case DbUserType.Loader:
                        query_grant_permissions = SQL("""
                            GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA {db_name} TO {username};
                            """).format(
                            db_name=Identifier(self.config.db_name),
                            username=Identifier(user_creds.username)
                        )
                    case DbUserType.Retriever:
                        query_grant_permissions = SQL("""
                            GRANT SELECT ON {db_name}.checks TO {username};
                            GRANT SELECT ON {db_name}.jobs TO {username};
                            GRANT SELECT ON {db_name}.regex_raw TO {username};
                            """).format(
                            db_name=Identifier(self.config.db_name),
                            username=Identifier(user_creds.username)
                        )
                cursor.execute(query_grant_permissions)
            else:
                raise UserAlreadyExistsException(given_username=user_creds.username) 
        except Exception as e:
            #create proper vlaidation
            print(e)

    def save_job_into_db(self, job:Job):
        query_insert_job=SQL("""
            INSERT INTO {db_name}.jobs(name,url,method,headers,body,scheduled_interval,expected_regex)
            VALUES ({name}, {url}, {method}, {headers}, {body}, {scheduled_interval}, {expected_regex})
            ON CONFLICT (name) DO
            UPDATE SET url={url}, method={method}, body={body}, scheduled_interval={scheduled_interval}, expected_regex={expected_regex};
        """).format(
            db_name=Identifier(self.config.db_name),
            name=Literal(job.name),
            url=Literal(job.url),
            method=Literal(job.method),
            headers=Literal(str(job.headers)),
            body=Literal(str(job.body)),
            scheduled_interval=Literal(job.scheduled_interval),
            expected_regex=Literal(job.expected_regex)
        )
        self.__connect(user_type=DbUserType.Loader).execute(query_insert_job)

    def get_jobs_from_db(self) -> List[Job]:
        query_get_jobs=SQL("""
            SELECT * FROM {db_name}.jobs;
        """).format(db_name=Identifier(self.config.db_name))
        cur = self.__connect(user_type=DbUserType.Retriever)
        cur.execute(query_get_jobs)
        results = cur.fetchall()
        jobs = []
        for act_job in results:
            jobs.append(Job(
                name = act_job[1],
                url = act_job[2],
                method = act_job[3],
                headers=json.loads(act_job[4]),
                body=json.loads(act_job[5]),
                expected_regex=act_job[6],
                scheduled_interval=act_job[7]
            ))
        return jobs

    def get_job_from_db(self, job_name: str) -> Tuple[int, Job]:
        query_get_jobs=SQL("""
            SELECT * FROM {db_name}.jobs WHERE name={job_name};
        """).format(
            db_name=Identifier(self.config.db_name),
            job_name=Literal(job_name)
        )
        cur = self.__connect(user_type=DbUserType.Retriever)
        cur.execute(query_get_jobs)
        result = cur.fetchone()
        job = Job(
            name=result[1],
            url=result[2],
            method=result[3],
            headers=json.loads(result[4]),
            body=json.loads(result[5]),
            expected_regex=result[6],
            scheduled_interval=result[7]
        )
        return (result[0],job)

    def save_check_into_db(self, check: Check):
        job_id, job = self.get_job_from_db(job_name=check.job_name)

        regex_id=None
        if job.expected_regex and check.regex_result:
            query_insert_regex_result=SQL("""
            INSERT INTO {db_name}.regex_raw(raw_finding)
            VALUES ({regex_result})
            RETURNING id;
            """).format(
                db_name=Identifier(self.config.db_name),
                regex_result=Literal(check.regex_result)
            )
            cur = self.__connect(user_type=DbUserType.Loader)
            cur.execute(query_insert_regex_result)
            regex_id = cur.fetchone()[0]

        query_insert_check=SQL("""
            INSERT INTO {db_name}.checks(job_id, start_ts, end_ts, status_code, regex_result_id)
            VALUES ({job_id}, {start_ts}, {end_ts}, {status_code}, {regex_result_id});
        """).format(
            db_name=Identifier(self.config.db_name),
            job_id=Literal(job_id),
            start_ts=Literal(check.start_time),
            end_ts=Literal(check.end_time),
            status_code=Literal(int(check.status_code)),
            regex_result_id=Literal(regex_id)
        )
        cur = self.__connect(user_type=DbUserType.Loader)
        cur.execute(query_insert_check)
