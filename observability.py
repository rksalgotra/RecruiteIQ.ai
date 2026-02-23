import logging
import json
import time
import uuid
from contextlib import contextmanager
from datetime import datetime


class StructuredLogger:
    def __init__(self, service_name="recruitiq"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _log(self, level, message, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level,
            "message": message,
            **kwargs
        }
        self.logger.info(json.dumps(log_entry))

    def info(self, message, **kwargs):
        self._log("INFO", message, **kwargs)

    def error(self, message, **kwargs):
        self._log("ERROR", message, **kwargs)


logger = StructuredLogger()


def generate_correlation_id():
    return str(uuid.uuid4())


@contextmanager
def timed_stage(stage_name, correlation_id):
    start = time.time()
    try:
        yield
        duration = round((time.time() - start) * 1000, 2)
        logger.info(
            "stage_completed",
            stage=stage_name,
            duration_ms=duration,
            correlation_id=correlation_id
        )
    except Exception as e:
        duration = round((time.time() - start) * 1000, 2)
        logger.error(
            "stage_failed",
            stage=stage_name,
            duration_ms=duration,
            correlation_id=correlation_id,
            error=str(e)
        )
        raise