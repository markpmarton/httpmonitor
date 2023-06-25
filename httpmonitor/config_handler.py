import json
import keyring
import os

from http import HTTPMethod
from configparser import ConfigParser
from dataclasses import dataclass, field

from .models import AppConfig
from .enums import DbUserType
from .errors import EmptyParameterException, FilePathAlreadyTakenException, InvalidFilenameException, WrongUserTypeException

@dataclass
class ConfigHandler:
    #Path of the config file
    config_path: str = "config.ini"

    #Data from config file
    working_dir: str = field(init=False)
    db_url: str = field(init=False)
    db_port: str = field(init=False)
    db_name: str = field(init=False)
    db_name_default: str = field(init=False)

    keyring_service_name: str = field(init=False)
    log_path: str = field(init=False)
    log_level: str = field(init=False)

    def deploy_default_app_config(self, out_filepath: str):
        """ The default config is:
        [general]
        working_dir = <current_working_dir>

        [database]
        db_url = localhost
        db_port = 5432
        db_name = httpmonitor
        db_name_default = defaultdb

        [keyring]
        service_name = httpmonitor

        [log]
        out_path = ./log.log
        level = info
        """

        self.working_dir = os.path.abspath(".")
        
        parser = ConfigParser()
        
        parser.add_section("general")
        parser.set("general", "working_dir", self.working_dir)

        parser.add_section("database")
        parser.set("database", "db_url", "localhost")
        parser.set("database", "db_port", "5432")
        parser.set("database", "db_name", "httpmonitor")
        parser.set("database", "db_name_default", "defaultdb")

        parser.add_section("keyring")
        parser.set("keyring", "service_name", "httpmonitor")

        parser.add_section("log")
        parser.set("log", "out_path" ,os.path.join(self.working_dir,"log.log"))
        parser.set("log", "level", "info")

        out_fullpath = os.path.join(self.working_dir, out_filepath)
        if not os.path.exists(out_fullpath):
            with open(out_filepath, 'w') as conf_file:
                parser.write(conf_file)
            self.config_path = out_filepath
        else:
            raise FilePathAlreadyTakenException(path=out_filepath)

    def deploy_default_jobs_config(self, out_filepath: str):
        """JSON structure:
        jobs:[
            {
                name: str(max. size: 50),
                url: str(max. size: 100),
                method: str(GET/POST/PUT/DELETE/...),
                headers: dict,
                body: dict,
                (opt)expected_regex: str(max. size 100)
                scheduled_interval: int(0-300)
            }
        ]
        """
        if not out_filepath or out_filepath == "":
            raise InvalidFilenameException(file_name=str(out_filepath))   

        job_fullpath = os.path.join(self.working_dir, out_filepath)
        if not os.path.exists(job_fullpath):
            jobs = {
                "jobs": [
                    {
                        "name": "example_job",
                        "url": "https://cnn.com",
                        "method": HTTPMethod.GET,
                        "headers": {},
                        "body": {},
                        "expected_regex": "",
                        "scheduled_interval": 30
                    }
                ]
            }
            with open(job_fullpath, "w") as writer:
                json.dump(jobs, writer)


    def __init__(self, config_path = None):
        if config_path:
            self.config_path = config_path
        if not os.path.exists(self.config_path):
            self.deploy_default_app_config(self.config_path)

        parser = ConfigParser()
        parser.read(self.config_path)

        config = AppConfig(
            general_working_dir=parser.get('general', 'working_dir'),
            database_db_url=parser.get('database', 'db_url'),
            database_db_port=int(parser.get('database', 'db_port')),
            database_db_name=parser.get('database', 'db_name'),
            database_db_name_default=parser.get('database', 'db_name_default'),
            keyring_service_name=parser.get('keyring','service_name'),
            log_out_path=parser.get('log', 'out_path'),
            log_level=parser.get('log', 'level')
        )

        #validate appconfig!
        self.working_dir =  config.general_working_dir
        self.db_url = config.database_db_url
        self.db_port = str(config.database_db_port)
        self.db_name = config.database_db_name
        self.db_name_default = config.database_db_name_default
        self.keyring_service_name = config.keyring_service_name
        self.log_path = config.log_out_path
        self.log_level = config.log_level

    def get_username(self, user_type: DbUserType):
        match user_type:
            case DbUserType.Retriever:
                return keyring.get_password(self.keyring_service_name, "dqluser_username")
            case DbUserType.Loader:
                return keyring.get_password(self.keyring_service_name, "dmluser_username")
            case DbUserType.Connector:
                return keyring.get_password(self.keyring_service_name, "connector_username")
            case _:
                raise WrongUserTypeException(given_type=str(user_type))


    def get_password(self, user_type: DbUserType):
        match user_type:
            case DbUserType.Retriever:
                return keyring.get_password(self.keyring_service_name, "dqluser_password")
            case DbUserType.Loader:
                return keyring.get_password(self.keyring_service_name, "dmluser_password")
            case DbUserType.Connector:
                return keyring.get_password(self.keyring_service_name, "connector_password")
            case _:
                raise WrongUserTypeException(given_type=str(user_type))

    def set_username(self, user_type: DbUserType, username: str):
        if not username or username == "":
            raise EmptyParameterException(method_name="set_username")
        match user_type:
            case DbUserType.Retriever:
                return keyring.set_password(self.keyring_service_name, "dqluser_username", username)
            case DbUserType.Loader:
                return keyring.set_password(self.keyring_service_name, "dmluser_username", username)
            case _:
                raise WrongUserTypeException(given_type=str(user_type))

    def set_password(self, user_type: DbUserType, password: str):
        if not password or password == "":
            raise EmptyParameterException(method_name="set_username")
        match user_type:
            case DbUserType.Retriever:
                return keyring.set_password(self.keyring_service_name, "dqluser_password", password)
            case DbUserType.Loader:
                return keyring.set_password(self.keyring_service_name, "dmluser_password", password)
            case _:
                raise WrongUserTypeException(given_type=str(user_type))
