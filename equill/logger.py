import os
import logging
import time
from threading import Lock
from typing import Optional, Callable, Any, List, Dict
import sys
from datetime import datetime
import io

MAX_CALLBACKS = 32

# Log levels
LOG_TRACE = 0
LOG_DEBUG = logging.DEBUG
LOG_INFO = logging.INFO
LOG_WARN = logging.WARNING
LOG_ERROR = logging.ERROR
LOG_FATAL = logging.CRITICAL

level_strings = {
    LOG_TRACE: "TRACE",
    LOG_DEBUG: "DEBUG",
    LOG_INFO: "INFO",
    LOG_WARN: "WARN",
    LOG_ERROR: "ERROR",
    LOG_FATAL: "FATAL",
}

level_colors = {
    LOG_TRACE: "\033[94m",
    LOG_DEBUG: "\033[36m",
    LOG_INFO: "\033[32m",
    LOG_WARN: "\033[33m",
    LOG_ERROR: "\033[31m",
    LOG_FATAL: "\033[35m",
}


class LogEvent:
    def __init__(self):
        self.fmt = ""
        self.file = ""
        self.line = 0
        self.level = LOG_INFO
        self.time: Optional[datetime] = None
        self.udata: Optional[Any] = None
        self.args: Optional[tuple] = None


class LogCallback:
    def __init__(self, fn: Callable[[LogEvent], None], udata: Any, level: int):
        self.fn = fn
        self.udata = udata
        self.level = level


class Logger:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.udata = None
        self.lock_fn = None
        self.level = LOG_TRACE
        self.quiet = False
        self.callbacks: List[LogCallback] = []

        # Register custom levels
        logging.addLevelName(LOG_TRACE, "TRACE")

        # Default stdout callback
        self.add_callback(self.stdout_callback, sys.stderr, LOG_TRACE)

    def lock(self, lock: bool):
        if self.lock_fn:
            self.lock_fn(lock, self.udata)

    def set_lock(self, fn: Callable[[bool, Any], None], udata: Any):
        self.lock_fn = fn
        self.udata = udata

    def set_level(self, level: int):
        self.level = level

    def set_quiet(self, enable: bool):
        self.quiet = enable

    def add_callback(
        self, fn: Callable[[LogEvent], None], udata: Any, level: int
    ) -> bool:
        if len(self.callbacks) >= MAX_CALLBACKS:
            return False
        self.callbacks.append(LogCallback(fn, udata, level))
        return True

    def add_file(self, filename: str, level: int = LOG_TRACE) -> bool:
        for callback in self.callbacks:
            if isinstance(
                callback.udata, io.TextIOWrapper
            ) and callback.udata.name == os.path.abspath(filename):
                return True
        try:
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            fp = open(filename, "a", encoding="utf-8")
            return self.add_callback(self.file_callback, fp, level)
        except Exception as e:
            sys.stderr.write(f"Failed to open log file {filename}: {e}\n")
            sys.stderr.flush()
            return False

    def stdout_callback(self, ev: LogEvent):
        time_str = ev.time.strftime("%H:%M:%S") if ev.time else "00:00:00"
        level_str = level_strings.get(ev.level, "INFO")
        color = level_colors.get(ev.level, "")

        message = ev.fmt
        if ev.args:
            message = message % ev.args

        file_info = f"{os.path.basename(ev.file)}:{ev.line}"

        print(
            f"{time_str} {color}{level_str:<5}\033[0m \033[90m{file_info}:\033[0m {message}",
            file=ev.udata,
        )

    def file_callback(self, ev: LogEvent):
        time_str = ev.time.strftime("%H:%M:%S") if ev.time else "00:00:00"
        level_str = level_strings.get(ev.level, "INFO")

        message = ev.fmt
        if ev.args:
            message = message % ev.args

        print(
            f"{time_str} {level_str:<5} {ev.file}:{ev.line}: {message}", file=ev.udata
        )

    def log(self, level: int, file: str, line: int, fmt: str, *args):
        ev = LogEvent()
        ev.fmt = fmt
        ev.file = file
        ev.line = line
        ev.level = level
        ev.time = datetime.now()
        ev.args = args

        try:
            self.lock(True)

            if self.quiet or level < self.level:
                return

            for callback in self.callbacks:
                if level >= callback.level:
                    ev.udata = callback.udata
                    callback.fn(ev)

        finally:
            self.lock(False)

    # Convenience methods
    def trace(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_TRACE, frame.f_code.co_filename, frame.f_lineno, fmt, *args)

    def debug(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_DEBUG, frame.f_code.co_filename, frame.f_lineno, fmt, *args)

    def info(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_INFO, frame.f_code.co_filename, frame.f_lineno, fmt, *args)

    def warn(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_WARN, frame.f_code.co_filename, frame.f_lineno, fmt, *args)

    def error(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_ERROR, frame.f_code.co_filename, frame.f_lineno, fmt, *args)

    def fatal(self, fmt: str, *args):
        frame = sys._getframe(2)
        self.log(LOG_FATAL, frame.f_code.co_filename, frame.f_lineno, fmt, *args)


# Global logger instance
logger = Logger()


# Shortcut functions
def log_trace(fmt: str, *args):
    logger.trace(fmt, *args)


def log_debug(fmt: str, *args):
    logger.debug(fmt, *args)


def log_info(fmt: str, *args):
    logger.info(fmt, *args)


def log_warn(fmt: str, *args):
    logger.warn(fmt, *args)


def log_error(fmt: str, *args):
    logger.error(fmt, *args)


def log_fatal(fmt: str, *args):
    logger.fatal(fmt, *args)


def log_set_level(level: int):
    logger.set_level(level)


def log_set_quiet(enable: bool):
    logger.set_quiet(enable)


def log_add_file(filename: str, level: int = LOG_TRACE) -> bool:
    return logger.add_file(filename, level)
