# Import custom Libraries
from normalizing import normalised

from MongoDB_Class import MongoDB_Class
from MinIO_Class import MinIO_Class
from FrontEnd_Class import FrontEnd_Class
from Diastema_Service import Diastema_Service

# Import Libraries
import io

def function_job(playbook, job, last_buckets):
    # get the new bucket
    function_bucket = normalised(playbook["database-id"])+"/analysis-"+normalised(playbook["analysis-id"])+"/function-"+normalised(job["step"])

    # Make the MinIO Join bucket
    minio_obj = MinIO_Class()
    minio_obj.put_object(normalised(playbook["database-id"]), "analysis-"+normalised(playbook["analysis-id"])+"/function-"+normalised(job["step"])+"/", io.BytesIO(b""), 0,)

    # Get the needed attributes
    function_data = {
        "job-id" : normalised(job["id"]),
        "inputs" : last_buckets,
        "output" : function_bucket,
        "function" : job["function"],
        "analysis-id" : playbook["analysis-id"]
    }

    # Start Loading Service
    service_obj = Diastema_Service()

    # Make it a function service
    service_obj.is_func_service()
    service_obj.startService("function", function_data)

    # Wait for loading to End
    job_res = service_obj.waitForService("function", job["id"])

    if job_res["status"] == "error":
        # Contact front end for the error of the job
        front_obj = FrontEnd_Class()
        front_obj.diastema_call(message = "error", update = job_res["message"]+" for the analysis with ID: "+playbook["analysis-id"])
        return function_bucket, True

    # Insert the cleaned data in MongoDB
    function_job_record = {"minio-path":function_bucket, "directory-kind":"function-data", "job-json":job, "analysis-id":playbook["analysis-id"]}

    mongo_obj = MongoDB_Class()
    mongo_obj.insertMongoRecord(normalised(playbook["database-id"]), "analysis_"+normalised(playbook["analysis-id"]), function_job_record)

    # Contact front end for the ending of the job
    front_obj = FrontEnd_Class()
    front_obj.diastema_call(message = "update", update = "Function executed for the analysis with ID: "+playbook["analysis-id"])

    # Return the bucket that this job made output to
    return function_bucket, False
