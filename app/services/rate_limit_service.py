import time

from app.config import get_settings
from app.core.exceptions import RateLimitException
from app.repositories.file_repository import FileRepository


class RateLimitService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.repository = FileRepository()

    def check(self, client_ip: str) -> None:
        now = int(time.time())
        window_start = now - self.settings.rate_limit_window_seconds

        data = self.repository.get_rate_limit_data()
        requests = data.get(client_ip, [])

        requests = [timestamp for timestamp in requests if timestamp > window_start]

        if len(requests) >= self.settings.rate_limit_max_requests:
            raise RateLimitException(
                "Too many requests. Please try again later."
            )

        requests.append(now)
        data[client_ip] = requests

        self.repository.save_rate_limit_data(data)