import sys
import logging
from .api.query_objects import (
    ServerQuery,
    UserQuery,
    FlavorQuery,
    ProjectQuery,
    ImageQuery,
    HypervisorQuery,
)

# Create logger
openstack_query_loggers = logging.getLogger(__name__)
openstack_query_loggers.setLevel(logging.DEBUG)

# Create Handler for logging data to stderr
logger_handler = logging.StreamHandler(sys.stderr)
logger_handler.setLevel(logging.DEBUG)

# Create a Formatter for formatting the log messages
logger_formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

# Add the Formatter to the Handler
logger_handler.setFormatter(logger_formatter)

# Add the Handler to the Logger
openstack_query_loggers.addHandler(logger_handler)
