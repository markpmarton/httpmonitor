from cerberus import Validator

from dataclasses import dataclass, field

from .errors import AbstractInstantiationException

@dataclass
class AbstractValidator:
    data: object | None
    schema: dict = field(init=False)
    errors: dict = field(init=False)

    def __post_init__(self):
        if self.__class__ == AbstractValidator:
            raise AbstractInstantiationException(class_to_instantiate='AbstractInstantiationException')
        self.errors = {}

    def validate(self) -> bool:
        validator = Validator()
        validator.require_all = True
        
        if validator.validate(self.data.to_dict(), self.schema):
            return True
        else:
            self.errors = validator.errors
            return False

@dataclass
class DbCredentialValidator(AbstractValidator):
    schema = {
        'username': {
            'type': 'string',
            'minlength': 3,
            'maxlength':50,
            'regex': '[a-z0-9]+'
        },
        'password': {
            'type': 'string',
            #Minimum 8 characters, at least one letter, one number, and one special character [Source: https://stackoverflow.com/a/21456918]
            'regex': r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&_])[A-Za-z\d@$!%*#?_&]{8,}$',             
            'minlength': 8
        },
        'type': {
            'type': 'string',
            'allowed': ['Retriever', 'Loader', 'Connector']
        }
    }

@dataclass
class JobValidator(AbstractValidator):
    schema = {
        'name': {
            'type': 'string',
            'minlength': 5,
            'maxlength': 50,
            'regex': '[a-zA-Z0-9_!]+'
        },
        'url': {
            'type': 'string',
            #URL regex [Source: https://uibakery.io/regex-library/url-regex-python]
            'regex':'^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$',
            'maxlength': 200
        },
        'method': {
            'type': 'string',
            'allowed': ['CONNECT','DELETE','GET','HEAD','OPTIONS','PATCH','POST','PUT','TRACE']
        },
        'headers': {
            'type': 'dict',
            'keysrules':{
                'type': 'string'
            },
            'valuesrules':{
                'type': 'string'
            },
            'empty': True
        },
        'body': {
            'type': 'dict',
            'keysrules':{
                'type': 'string'
            },
            'valuesrules':{
                'type': 'string',
                'type': 'integer'
            },
            'empty': True
        },
        'expected_regex': {
            'type': 'string',
            'maxlength': 100,
            'empty': True
        },
        'scheduled_interval': {
            'type': 'integer',
            'min': 5,
            'max': 300
        }
    }

@dataclass
class CheckValidator(AbstractValidator):
    schema = {
        'job_name': {
            'type': 'string',
            'minlength': 5,
            'maxlength': 50,
            'regex': '[a-zA-Z0-9_!]+'
        },
        'start_time': {
            'type': 'datetime'
        },
        'end_time': {
            'type': 'datetime'
        },
        'status_code': {
            'type': 'integer',
            'min': 100,
            'max': 599,
        },
        'regex_result': {
            'type': 'string',
            'empty': True
        }
        
    }


@dataclass
class ConfigValidator(AbstractValidator):
    schema = {
        'general_working_dir': {
            'type': 'string',
            'empty': False
        },
        'database_db_url': {
            'type': 'string',
            'empty': False
        },
        'database_db_port': {
            'type': 'integer',
            'min': 0,
            'max': 65535
        },
        'database_db_name': {
            'type': 'string',
            'regex': '[a-zA-Z0-9]+',
            'empty': False
        },
        'database_db_name_default': {
            'type': 'string',
            'regex': '[a-zA-Z0-9]+',
            'empty': False
        },
        'keyring_service_name': {
            'type': 'string',
            'minlength': 3,
            'maxlength': 50
        },
        'log_out_path': {
            'type': 'string',
            'empty': False
        },
        'log_level': {
            'type': 'string',
            'allowed': ['debug', 'info', 'warning', 'error', 'critical']
        }
    }
