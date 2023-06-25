import getpass
import keyring

from typing import List

from .config_handler import ConfigHandler
from .const import CONFIG_PATH, JOBS_PATH
from .db_connector import DbConnector
from .enums import DbUserType
from .errors import ValuesDoNotMatchException, WrongUserTypeException
from .logger import Logger
from .models import DbCredentials


class SetupScript:
    credentials: List[DbCredentials] = []

    @staticmethod
    def collect_user_data(user_type: DbUserType, message: str):
        print(message)
        password = ""
        username = input("Username:")
        match user_type:
            case DbUserType.Connector:
                password = getpass.getpass("Password:")
            case _:
                password = getpass.getpass("Password(min. 8 chars, with at least one number and one special character):")

        password_conf = getpass.getpass("Confirm password:")

        if password == password_conf:
            SetupScript.credentials.append(DbCredentials(username=username, password=password, type=user_type))
            Logger.debug(f"User'{username}' created.")
        else:
            Logger.error(f"User '{username}' registration: Passwords do not match.")
            raise ValuesDoNotMatchException

    @staticmethod
    def check_user_existence(db_connector: DbConnector, user_credentials: DbCredentials):
        db_connector.user_exists(username=user_credentials.username)

def setup():
    """
    Setup script to collect all the credentials required and deploy the default config.
    """

    # Deploy default app config and jobs file
    config_handler = ConfigHandler(config_path=CONFIG_PATH)
    config_handler.deploy_default_jobs_config(out_filepath=JOBS_PATH)

    # Collecting credentials for user creaton.
    print("""
    This is the first-run script for the httpmonitor tool.
    For the proper operation this will need to set up a 'Data retriever' and a 'Data loader' user in the database.
    Please provide the required information as the prompt asks!
    """)
    user_setups = [
        lambda: SetupScript.collect_user_data(DbUserType.Connector, f"\nTo execute database schaffolding the scripts needs the credentials of the admin database user."),
        lambda: SetupScript.collect_user_data(DbUserType.Retriever, f"\nEnter credentials for the user '{DbUserType.Retriever.value}':"),
        lambda: SetupScript.collect_user_data(DbUserType.Loader, f"\nEnter credentials for the user '{DbUserType.Loader.value}':"),
    ]

    for act_action in user_setups:
        while True:
            try:
                act_action()
                break
            except ValuesDoNotMatchException:
                continue

    # Storing credentials in keyring
    for act_user_cred in SetupScript.credentials:
        match act_user_cred.type:
            case DbUserType.Loader:
                keyring.set_password(config_handler.keyring_service_name, "dmluser_username", act_user_cred.username)
                keyring.set_password(config_handler.keyring_service_name, "dmluser_password", act_user_cred.password)
            case DbUserType.Retriever:
                keyring.set_password(config_handler.keyring_service_name, "dqluser_username", act_user_cred.username)
                keyring.set_password(config_handler.keyring_service_name, "dqluser_password", act_user_cred.password)
            case DbUserType.Connector:
                keyring.set_password(config_handler.keyring_service_name, "connector_username", act_user_cred.username)
                keyring.set_password(config_handler.keyring_service_name, "connector_password", act_user_cred.password)
            case _:
                raise WrongUserTypeException(given_type=act_user_cred.type) 

    Logger.debug("Credentials registered in keyring.")

    # Initialize database
    db_connector = DbConnector()
    db_connector.init_database()


    # Creating database users
    for act_user_cred in SetupScript.credentials:
        if act_user_cred.type is not DbUserType.Connector:
            db_connector.create_user(user_creds=act_user_cred)

    Logger.debug("Database initialized.")
    # Remove admin password
    keyring.delete_password(config_handler.keyring_service_name, "connector_username")
    keyring.delete_password(config_handler.keyring_service_name, "connector_password")

    Logger.debug("Setup finished.")
    
    print("Setup finished! Enter 'httpmonitor -h' for available commands.")


if __name__ == "__main__":
    setup()
