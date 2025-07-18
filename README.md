# Echo Quill 📜

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/zhangzrjerry/echoquill/python-package.yml)

A structured, intelligent logger for Python workflows — especially useful for ML experiments, benchmarks, and reproducible research.

Echo Quill enhances Python’s built-in `logging` module by introducing custom log levels like `[PARAM]` and `[RESULT]`, which are automatically organized in the log file to improve readability and traceability.

This makes it easy to:

- Track hyperparameters at a glance
- Compare results across runs
- Maintain clean separation from standard logs (`INFO`, `WARNING`, etc.)

## Installation

```bash
pip install git+https://github.com/ZhangzrJerry/EchoQuill.git
```

## Example Output

```py
from equill import Logger
logger = Logger(directory="logs", console_output=True)

logger.info("Training started...")

logger.param("learning_rate=0.01")
logger.param("batch_size=32")

param = {
    "radius_normal": 0.005,
    "radius_feature": 0.01
}
logger.param(param)

logger.warn("Low GPU memory")

logger.result("accuracy=98.7%")
logger.result("loss=0.05")
```

Although the log file contains both custom and standard log levels, Echo Quill ensures that parameters and results are clearly highlighted and easy to find.

```paintxt
2025-04-05 12:34:56,789 [PARAM] learning_rate=0.01
2025-04-05 12:34:56,790 [PARAM] batch_size=32
2025-04-05 12:34:56,791 [PARAM] radius_normal: 0.005
2025-04-05 12:34:56,792 [PARAM] radius_feature: 0.01
2025-04-05 12:34:57,772 [RESULT] accuracy=98.7%
2025-04-05 12:34:57,773 [RESULT] loss=0.05
2025-04-05 12:34:56,780 [INFO] Training started...
2025-04-05 12:34:56,793 [WARNING] Low GPU memory
```
