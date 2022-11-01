import json
import os
import time

import requests

import askanna

train_runs = []

parameters = [
    {"alpha": 0.3, "l1_ratio": 0.1},
    {"alpha": 0.2, "l1_ratio": 0.7},
    {"alpha": 0.4, "l1_ratio": 0.2},
    {"alpha": 0.5, "l1_ratio": 0.7},
    {"alpha": 0.1, "l1_ratio": 0.9},
    {"alpha": 0.2, "l1_ratio": 0.2},
    {"alpha": 0.7, "l1_ratio": 0.4},
]

askanna.track_variable("parameters", parameters)

for param in parameters:
    print(f"Running with param = {param}")
    response = askanna.run.start(job_suuid="2qSS-casN-tc2G-TA2d", data=param)
    train_runs.append(response.short_uuid)
    print(f"Status = {response.status}")

askanna.track_variable("train-runs", json.dumps(train_runs))
time.sleep(10)

for run in train_runs:
    status = "running"
    while status == "running":
        runinfo = askanna.run.status(run)
        print(f"Update: {runinfo.short_uuid} is still running")
        time.sleep(10)
        status = runinfo.status

runs = askanna.runs.get(runs=train_runs, include_metrics=True, include_variables=True)
rmse = 1
for run in runs:
    run_rmse = run.metrics.get("rmse").get("metric").get("value")
    if run_rmse < rmse:
        run_selected = run
        rmse = run_rmse

alpha = run_selected.variables.get("alpha").get("variable").get("value")
l1_ratio = run_selected.variables.get("l1_ratio").get("variable").get("value")

print(f"The optimal run SUUID is {run_selected.short_uuid}")
print(f"It had the parameters: alpha={alpha}, l1_ratio={l1_ratio}")
print(f"And RMSE: {rmse}")

askanna.track_variable(
    "best-model", {"run_suuid": run_selected.short_uuid, "alpha": alpha, "l1_ratio": l1_ratio, "rmse": rmse}
)

url = f"https://api.askanna.eu/v1/result/{run_selected.short_uuid}/"
token = "Token " + os.getenv("AA_TOKEN")
headers = {"Authorization": token}
response = requests.get(url, headers=headers)

with open("model/model.pkl", "wb") as f:
    f.write(response.content)

print("Best model copied to the model directory.")
