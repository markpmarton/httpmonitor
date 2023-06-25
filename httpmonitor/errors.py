from dataclasses import dataclass, field

@dataclass
class BaseException(Exception):
    message = ""

    def __post_init__(self):
        from .logger import Logger
        Logger.error(f"Exception: {self.message}")

    def __repr__(self):
        return self.message

@dataclass
class FilePathAlreadyTakenException(BaseException):
    """ If the given filepath is already taken, creates this exception instead of replacing the file. """
    
    path: str = field()
    message: str = "The given file path is alreafy taken!"

@dataclass
class ValuesDoNotMatchException(BaseException):
    """ Used for comparing entered password values. """
    message: str = "Password values do not match."

@dataclass
class WrongUserTypeException(BaseException):
    given_type: str = field()
    message: str = f"The user type {given_type} is not registered."

@dataclass
class NoPermissionToCreateFileException(BaseException):
    path: str = field()
    message: str = f"File on path {path} could not be created."

@dataclass
class UserAlreadyExistsException(BaseException):
    given_username: str = field()
    message: str = f"User '{given_username}' does not exist"

@dataclass
class AbstractInstantiationException(BaseException):
    class_to_instantiate: str = field()
    message: str = f"Abstract class '{class_to_instantiate}' can not be initialized"

@dataclass
class ValidatorException(BaseException):
    model_type: str = field()
    errors: str = field()
    message: str = f"Validation error on '{model_type}' object. Errors: {errors}"

@dataclass
class FieldMissingException(BaseException):
    class_name: str = field()
    missing_fields: list = field()
    message: str = f"Missing fields while using '{class_name}' class: {missing_fields}"

@dataclass
class SetupRequiredException(BaseException):
    message: str = f"Required resource are not properly installed. Please run the setup (check the help for more info)."

@dataclass
class InvalidFilenameException(BaseException):
    file_name: str = field()
    message: str = f"Given file name '{file_name}' is invalid."

@dataclass
class EmptyParameterException(BaseException):
    method_name: str = field()
    message: str = f"Empty parameter found in method '{method_name}'"
