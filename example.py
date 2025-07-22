from equill import (
    log_info,
    log_trace,
    log_debug,
    log_warn,
    log_error,
    log_fatal,
    log_set_level,
    log_add_file,
    log_set_quiet,
    LOG_DEBUG,
    LOG_INFO,
    LOG_WARN,
    LOG_ERROR,
    LOG_FATAL,
)
import os

# Basic usage
log_info("This is an info message")
log_trace("Current working directory: %s", os.getcwd())

# Configure logger
log_set_level(LOG_DEBUG)
log_add_file("./output.log")
log_set_quiet(True)

log_info("This is an info message")
log_info("Current working directory: %s", os.getcwd())
