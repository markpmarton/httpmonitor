import logging
import os

from .config_handler import ConfigHandler

class LoggerFactory:
    """
    [Source: https://medium.com/geekculture/create-a-reusable-logger-factory-for-python-projects-419ad408665d]
    """

    @staticmethod
    def __create_logger(log_path, level, working_dir):
        format = "%(asctime)s|%(levelname)s|%(message)s"
        formatter = logging.Formatter(format)

        full_log_path = os.path.join(working_dir, log_path)
        
        LoggerFactory._level = level
        LoggerFactory._log_path = full_log_path
        LoggerFactory._logger = logging.getLogger("httpmonitor_logger")
        
        logging.basicConfig(level=logging.INFO, format=format, datefmt="%Y-%m-%d %H:%M:%S")

        match level:
            case "INFO":
                LoggerFactory._logger.setLevel(logging.INFO)
            case "ERROR":
                LoggerFactory._logger.setLevel(logging.ERROR)
            case "DEBUG":
                LoggerFactory._logger.setLevel(logging.DEBUG)
            case "WARNING":
                LoggerFactory._logger.setLevel(logging.WARNING)
            case "CRITICAL":
                LoggerFactory._logger.setLevel(logging.CRITICAL)


        file_handler = logging.FileHandler(full_log_path)
        file_handler.setLevel(LoggerFactory._logger.level)
        file_handler.setFormatter(formatter)
        LoggerFactory._logger.addHandler(file_handler)

        return LoggerFactory._logger

    @staticmethod
    def get_logger():
        config_handler = ConfigHandler()
        log_path = config_handler.log_path
        level = config_handler.log_level
        working_dir = config_handler.working_dir
        logger = LoggerFactory.__create_logger(log_path, level, working_dir)
        return logger

Logger = LoggerFactory.get_logger()
