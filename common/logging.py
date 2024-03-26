import os
import sys

from loguru import logger

from common.enums.log_level import LogLevel

# Define the format with colorized output
log_format = "{level}: <green>{message}</green>"

# Configure the loggers
stdout_logger = logger.bind(output="stdout")
stdout_logger.remove()  # Remove any default handlers
stdout_logger.add(sys.stdout, format=log_format, colorize=True)
file_logger = logger.bind(output="file")
file_logger.remove()  # Remove any default handlers
file_logger.add("logs/logfile.log", format=log_format)


def log(msg: str, level: LogLevel, also_log_to_file: bool = False):
    os.system('cls' if os.name in ('nt', 'dos') else 'clear')
    if level == LogLevel.INFO:
        stdout_logger.info(msg)
        if also_log_to_file:
            file_logger.info(msg)
    elif level == LogLevel.WARNING:
        stdout_logger.warning(msg)
        if also_log_to_file:
            file_logger.warning(msg)
    elif level == LogLevel.CRITICAL:
        stdout_logger.critical(msg)
        if also_log_to_file:
            file_logger.critical(msg)
    input()


def log_to_file(msg: str, level: LogLevel):
    if level == LogLevel.INFO:
        file_logger.info(msg)
    elif level == LogLevel.WARNING:
        file_logger.warning(msg)
    elif level == LogLevel.CRITICAL:
        file_logger.critical(msg)
