from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from .enums import DbUserType
from .errors import ValidatorException
from .validators import CheckValidator, DbCredentialValidator, JobValidator, ConfigValidator


@dataclass
class BaseModel:
    def to_dict(self) -> dict:
        return self.__dict__

#Configuration models
@dataclass
class DbCredentials(BaseModel):
    username: str
    password: str
    type: DbUserType

    def to_dict(self) -> dict:
        return {
            'username': self.username,
            'password': self.password,
            'type': str(self.type.value)
        }
    
    def __post_init__(self):
        if self.type != DbUserType.Connector:
            validator = DbCredentialValidator(self)
            if not validator.validate():
                raise ValidatorException(model_type="DbCredentials", errors=",".join(validator.errors))


#Database models
@dataclass
class Job(BaseModel):
    name: str
    url: str
    method: str
    headers: Dict
    body: Dict
    expected_regex: str | None
    scheduled_interval: int
    
    def __post_init__(self):
        validator = JobValidator(self)
        if not validator.validate():
            raise ValidatorException(model_type="Job", errors=",".join(validator.errors))


@dataclass
class Check(BaseModel):
    job_name: str
    start_time: datetime
    end_time: datetime
    status_code: int
    regex_result: str
    
    def __post_init__(self):
        validator = CheckValidator(self)
        if not validator.validate():
            raise ValidatorException(model_type="Check", errors=",".join(validator.errors))

@dataclass
class AppConfig(BaseModel):
    general_working_dir: str
    database_db_url: str
    database_db_port: int | str
    database_db_name: str
    database_db_name_default: str
    keyring_service_name: str
    log_out_path: str
    log_level: str

    def __post_init__(self):
        validator = ConfigValidator(self)
        if not validator.validate():
            raise ValidatorException(model_type="AppConfig", errors=",".join(validator.errors))


