import sys
import logging

# Create logger
email_api_loggers = logging.getLogger(__name__)
email_api_loggers.setLevel(logging.DEBUG)

# Create Handler for logging data to stderr
logger_handler = logging.StreamHandler(sys.stderr)
logger_handler.setLevel(logging.DEBUG)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
email_api_loggers.addHandler(logger_handler)
