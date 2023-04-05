from datetime import datetime, timezone

from faker import Faker


class AskAnnaFaker:
    def __init__(self):
        self.fake = Faker()

    def date_time_str(self) -> str:
        return f"{self.fake.date_time(tzinfo=timezone.utc):%Y-%m-%dT%H:%M:%S.%fZ}"


faker = AskAnnaFaker()


def str_to_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
