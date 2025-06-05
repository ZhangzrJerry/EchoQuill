import os
import time
import logging
import tempfile
import shutil

from equill import Logger
from equill.logger import PrependFileHandler


def test_logger():
    # Use a temporary directory for testing
    temp_dir = tempfile.mkdtemp()
    print(temp_dir)
    log_file_path = os.path.join(temp_dir, "test.log")

    try:
        # Patch the logger to write to our custom path
        logger = Logger(directory=temp_dir)
        logger.file_path = log_file_path  # override for test
        logger.logger.handlers.clear()

        # Replace handler with one pointing to test file
        fh = PrependFileHandler(log_file_path)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        logger.logger.addHandler(fh)

        # Test logging sequence
        logger.param("param1")
        logger.param("param2")
        logger.info("info1")
        logger.result("result1")
        logger.param("param3")
        logger.result("result2")
        logger.error("error1")

        time.sleep(0.1)  # Ensure timestamps differ

        # Read the file content
        with open(log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Assertions
        assert any("[PARAM] param1" in line for line in lines)
        assert any("[PARAM] param2" in line for line in lines)
        assert any("[PARAM] param3" in line for line in lines)
        assert any("[INFO] info1" in line for line in lines)
        assert any("[RESULT] result1" in line for line in lines)
        assert any("[RESULT] result2" in line for line in lines)
        assert any("[ERROR] error1" in line for line in lines)

        # Check ordering: params first
        param_indices = [i for i, line in enumerate(lines) if "[PARAM]" in line]
        assert param_indices == sorted(
            param_indices
        ), "PARAM entries should be grouped at the top"

        # Check ordering: results come after params
        result_indices = [i for i, line in enumerate(lines) if "[RESULT]" in line]
        last_param_index = max(param_indices)
        first_result_index = min(result_indices)
        assert (
            first_result_index > last_param_index
        ), "RESULT entries should come after PARAM entries"

        # Info and error should appear where logged
        info_index = next(i for i, line in enumerate(lines) if "[INFO] info1" in line)
        assert info_index > last_param_index, "INFO should appear after PARAMs"
        error_index = next(
            i for i, line in enumerate(lines) if "[ERROR] error1" in line
        )
        assert error_index > info_index, "ERROR should appear after INFO"

    finally:
        shutil.rmtree(temp_dir)
