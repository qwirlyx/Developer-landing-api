import json
import os
from typing import Any


class FileRepository:
    def __init__(self) -> None:
        self.storage_dir = os.path.join("app", "storage")
        self.metrics_file = os.path.join(self.storage_dir, "metrics.json")
        self.rate_limit_file = os.path.join(self.storage_dir, "rate_limit.json")
        os.makedirs(self.storage_dir, exist_ok=True)

    def read_json(self, path: str, default: Any) -> Any:
        if not os.path.exists(path):
            return default

        try:
            with open(path, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return default

    def write_json(self, path: str, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def get_metrics(self) -> dict:
        default_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "ai_success": 0,
            "ai_fallback": 0,
        }
        return self.read_json(self.metrics_file, default_metrics)

    def save_metrics(self, metrics: dict) -> None:
        self.write_json(self.metrics_file, metrics)

    def increment_metric(self, key: str) -> None:
        metrics = self.get_metrics()
        metrics[key] = metrics.get(key, 0) + 1
        self.save_metrics(metrics)

    def get_rate_limit_data(self) -> dict:
        return self.read_json(self.rate_limit_file, {})

    def save_rate_limit_data(self, data: dict) -> None:
        self.write_json(self.rate_limit_file, data)