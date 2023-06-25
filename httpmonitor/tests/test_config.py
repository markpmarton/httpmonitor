import os
import pytest

from configparser import MissingSectionHeaderError, NoOptionError, NoSectionError
from httpmonitor.errors import ValidatorException, InvalidFilenameException, FilePathAlreadyTakenException, WrongUserTypeException, EmptyParameterException

from httpmonitor.config_handler import ConfigHandler
from httpmonitor.enums import DbUserType

def test_config_wrong_config_path():
    with pytest.raises(MissingSectionHeaderError) as e:
        ConfigHandler(config_path="jobs.json")

def test_config_missing_section():
    with open("bad_config.ini", "w") as writer:
        writer.write("""
            [general]
            working_dir = /var/lib/httpmonitor

            [database]
            db_url = localhost
            db_port = 5432
            db_name = httpmonitor
            db_name_default = dbdefault

            [log]
            out_path = /var/lib/httpmonitor/log.log
            level = info
        """)
    with pytest.raises(NoSectionError):
        ConfigHandler(config_path="bad_config.ini")
    os.remove("bad_config.ini")


def test_config_missing_key():
    with open("bad_config.ini", "w") as writer:
        writer.write("""
            [general]
            working_dir =

            [database]
            db_url = localhost
            db_port = 5432
            db_name = httpmonitor
            db_name_default = dbdefault

            [keyring]
            service_name = httpmonitor

            [log]
            out_path = /var/lib/httpmonitor/log.log
            level = info
        """)
    with pytest.raises(ValidatorException):
        ConfigHandler(config_path="bad_config.ini")
    os.remove("bad_config.ini")

def test_config_bad_key():
    with open("bad_config.ini", "w") as writer:
        writer.write("""
            [general]
            working_dir = /var/lib/httpmonitor

            [database]
            db_uras = localhost
            db_port = 5432
            db_name = httpmonitor
            db_name_default = dbdefault

            [keyring]
            service_name = httpmonitor

            [log]
            out_path = /var/lib/httpmonitor/log.log
            level = info
        """)
    with pytest.raises(NoOptionError):
        ConfigHandler(config_path="bad_config.ini")
    os.remove("bad_config.ini")

def test_job_empty_path():
    with pytest.raises(InvalidFilenameException):
        config_handler = ConfigHandler()
        config_handler.deploy_default_jobs_config("")

def test_config_empty_path():
    with pytest.raises(FilePathAlreadyTakenException):
        config_handler = ConfigHandler()
        config_handler.deploy_default_app_config("")

def test_keyring_get_username_invalid_type():
    bad_user_type = DbUserType
    with pytest.raises(WrongUserTypeException):
        config_handler = ConfigHandler()
        config_handler.get_username(user_type=bad_user_type)

def test_keyring_get_username_valid_type():
    user_type = DbUserType.Loader
    config_handler = ConfigHandler()
    username = config_handler.get_username(user_type=user_type)
    assert(type(username) is str)

def test_keyring_get_password_with_invalid_type():
    bad_user_type = DbUserType
    with pytest.raises(WrongUserTypeException):
        config_handler = ConfigHandler()
        config_handler.get_password(user_type=bad_user_type)

def test_keyring_get_password_valid_type():
    user_type = DbUserType.Loader
    config_handler = ConfigHandler()
    password = config_handler.get_password(user_type=user_type)
    assert(type(password) is str)

def test_keyring_set_username_invalid_type():
    bad_user_type = DbUserType.Connector
    with pytest.raises(WrongUserTypeException):
        config_handler = ConfigHandler()
        config_handler.set_username(user_type=bad_user_type, username="bad_username")

def test_keyring_set_password_invalid_type():
    bad_user_type = DbUserType.Connector
    with pytest.raises(WrongUserTypeException):
        config_handler = ConfigHandler()
        config_handler.set_password(user_type=bad_user_type, password="bad_password")

def test_keyring_set_username_valid_type_empty_username():
    user_type = DbUserType.Loader
    with pytest.raises(EmptyParameterException):
        config_handler = ConfigHandler()
        config_handler.set_username(user_type=user_type, username="")

def test_keyring_set_password_valid_type():
    user_type = DbUserType.Loader
    config_handler = ConfigHandler()
    recent_password = config_handler.get_password(user_type)
    config_handler.set_password(user_type=user_type, password="new_password")
    config_handler.set_password(user_type=user_type, password=recent_password)
    password = config_handler.get_password(user_type)
    assert(password == recent_password)

def test_keyring_set_username_valid_type():
    user_type = DbUserType.Loader
    config_handler = ConfigHandler()
    recent_username = config_handler.get_username(user_type)
    config_handler.set_username(user_type=user_type, username="new_username")
    config_handler.set_username(user_type=user_type, username=recent_username)
    username = config_handler.get_username(user_type)
    assert(username == recent_username)
