import json
from datetime import datetime

dt = datetime.now()
print(dt)

json_dt = json.dumps(dt.isoformat())
with open("result.json", "wb") as f:
    f.write(json_dt)
