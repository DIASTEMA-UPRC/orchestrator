# Import Libraries
import os
import requests
import time

AUTOML_HOST = os.getenv("AUTOML_HOST", "localhost")
AUTOML_PORT = int(os.getenv("AUTOML_PORT", 5001))

def execute_automl(minio_input, ml_task, job_id, column, parameters):
    # Make the AutoML URL
    automl_url = "http://"+AUTOML_HOST+":"+str(AUTOML_PORT)+"/automl"

    # AutoML Body
    automl_body = {
        "minio-input" : minio_input,
        "ml-task" : ml_task,
        "job-id" : job_id,
        "column" : column,
        "parameters" : parameters
    }

    # Execute AutoML
    requests.post(automl_url, json=automl_body)

    # Wait for AutoML to finish
    while True:
        time.sleep(2)
        url = automl_url+"/progress?id="+str(job_id)
        progress_responce = requests.get(url)
        if ((progress_responce.json())["status"] != "progress"):
            break
        print("[INFO] Again for: AutoML")

    return progress_responce.json()