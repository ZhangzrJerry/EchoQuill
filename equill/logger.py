import os
import logging
import time
from threading import Lock


class PrependFileHandler(logging.FileHandler):
    def __init__(self, filename, mode="a", encoding=None, delay=False):
        super().__init__(filename, mode, encoding, delay)
        self._prepend_lock = Lock()

    def emit(self, record):
        msg = self.format(record)
        if record.levelname not in ("PARAM", "RESULT"):
            super().emit(record)
            return

        try:
            with self._prepend_lock:
                if not os.path.exists(self.baseFilename):
                    with open(self.baseFilename, "w", encoding=self.encoding) as f:
                        f.write(msg + "\n")
                    return

                with open(self.baseFilename, "r+", encoding=self.encoding) as f:
                    content = f.readlines()

                    if record.levelname == "PARAM":
                        # Insert after all existing PARAMs but before first non-PARAM line
                        insert_idx = 0
                        for i, line in enumerate(content):
                            if "[PARAM]" in line:
                                insert_idx = i + 1
                            else:
                                break
                        content.insert(insert_idx, msg + "\n")

                    elif record.levelname == "RESULT":
                        # Insert after all existing RESULTs but before first non-RESULT line
                        insert_idx = len(content)
                        for i, line in enumerate(content):
                            if "[RESULT]" in line:
                                insert_idx = i + 1
                        content.insert(insert_idx, msg + "\n")

                    f.seek(0)
                    f.writelines(content)
                    f.truncate()
        except Exception as e:
            print(f"Error writing log: {e}")


class BetterLogger:
    LEVELS = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "param": 24,
        "result": 25,
    }

    def __init__(self, directory="log", console_output=True):
        self.directory = directory
        file_name = f"{time.strftime('%Y%m%d_%H%M%S')}.log"
        self.file_path = os.path.join(directory, file_name)

        # Register custom levels only once
        logging.addLevelName(self.LEVELS["param"], "PARAM")
        logging.addLevelName(self.LEVELS["result"], "RESULT")

        self.logger = logging.getLogger("equill_logger")
        self.logger.setLevel(logging.DEBUG)

        # Avoid duplicate handlers
        self.logger.handlers.clear()

        # Ensure log directory exists
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        # File handler
        fh = PrependFileHandler(self.file_path)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # Optional console handler
        if console_output:
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def debug(self, *args, sep=" ", end=""):
        self.logger.debug(sep.join(str(arg) for arg in args) + end)

    def info(self, *args, sep=" ", end=""):
        self.logger.info(sep.join(str(arg) for arg in args) + end)

    def warn(self, *args, sep=" ", end=""):
        self.logger.warning(sep.join(str(arg) for arg in args) + end)

    def error(self, *args, sep=" ", end=""):
        self.logger.error(sep.join(str(arg) for arg in args) + end)

    def param(self, *args, sep=" ", end=""):
        self.logger.log(self.LEVELS["param"], sep.join(str(arg) for arg in args) + end)

    def result(self, *args, sep=" ", end=""):
        self.logger.log(self.LEVELS["result"], sep.join(str(arg) for arg in args) + end)
