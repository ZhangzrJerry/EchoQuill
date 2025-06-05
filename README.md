# Echo Quill 📜

A structured, intelligent logger for Python workflows — especially useful for ML experiments, benchmarks, and reproducible research.

Echo Quill enhances Python’s built-in `logging` module by introducing custom log levels like `[PARAM]` and `[RESULT]`, which are automatically organized in the log file to improve readability and traceability.

This makes it easy to:

- Track hyperparameters at a glance
- Compare results across runs
- Maintain clean separation from standard logs (`INFO`, `WARNING`, etc.)

## Example Log Output

```py
from echoquill import Logger
logger = Logger(log_dir="logs", console_output=True)

logger.info("Training started...")

logger.param("learning_rate=0.01")
logger.param("batch_size=32")

logger.warn("Low GPU memory")

logger.result("accuracy=98.7%")
logger.result("loss=0.05")
```

Although the log file contains both custom and standard log levels, Echo Quill ensures that parameters and results are clearly highlighted and easy to find.

```paintxt
2025-04-05 12:34:56,789 [PARAM] learning_rate=0.01
2025-04-05 12:34:56,790 [PARAM] batch_size=32
2025-04-05 12:34:57,772 [RESULT] accuracy=98.7%
2025-04-05 12:34:57,773 [RESULT] loss=0.05
2025-04-05 12:34:56,780 [INFO] Training started...
2025-04-05 12:34:56,793 [WARNING] Low GPU memory
```
