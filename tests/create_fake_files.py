import json
import os
from zipfile import ZipFile

from faker import Faker


def create_fake_result(records: int = 1) -> list:
    fake = Faker()
    result = []

    for i in range(records):
        result.append(
            {
                "id": i + 1,
                "first_name": fake.first_name(),
                "last_name": fake.last_name(),
                "email": fake.email(),
                "ip": fake.ipv4(),
                "number": fake.pyfloat(),
                "boolean": fake.boolean(),
                "datetime": fake.date() + "T" + fake.time(),
            }
        )

    return result


def create_json_file(dir: str, records: int) -> str:
    result = create_fake_result(records)

    json_file_name = f"{dir}/random_json.json"
    with open(json_file_name, "w") as f:
        json.dump(result, f)

    return json_file_name


def create_zip_file(dir: str, records: int) -> str:
    result = create_fake_result(records)

    json_file_name = f"{dir}/random_json.json"
    with open(json_file_name, "w") as f:
        json.dump(result, f)

    zip_file_name = f"{dir}/random_json.zip"
    with ZipFile(zip_file_name, mode="w") as f:
        f.write(json_file_name)

    os.remove(json_file_name)
    return zip_file_name
