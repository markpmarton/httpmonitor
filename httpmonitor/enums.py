from enum import Enum

class DbUserType(Enum):
    Retriever = "Retriever"
    Loader = "Loader"
    Connector = "Connector"

