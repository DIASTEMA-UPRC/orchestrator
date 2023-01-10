# Import custom Libraries
from normalizing import normalised

# Import custom Libraries
from MongoDB_Class import MongoDB_Class
from MinIO_Class import MinIO_Class
from FrontEnd_Class import FrontEnd_Class
from Diastema_Service import Diastema_Service

# Import Libraries
import io

def visualize(playbook, job, last_bucket):
    '''
    The following data must be send to the visualization service
    {
        "analysis-id" : <analysis-id>,
        "job-id" : <job-id>,
        "last-job-id" : <last-job-id>,
        "last-job-title" : <last-job-title>,
        "minio-output" : <minio-output>,
        "minio-input" : <minio-input>
    }
    '''

    # The Data to be visualised are saved in the bucket below
    analysis_id = playbook["analysis-id"]
    job_id = job["id"]
    last_job_id = job["from"]
    last_job_title = "" # To be found
    minio_output = normalised(playbook["database-id"]) + "/analysis-" + normalised(playbook["analysis-id"]) + "/visualization-" + normalised(job["step"])
    minio_input = last_bucket

    # Use all the playbook to find the last job
    jobs = playbook["jobs"]

    for i_job in jobs:
        if(i_job["id"] == last_job_id):
            last_job_title = i_job["title"]
            break
    
    # Make the MinIO Analysis buckers
    minio_obj = MinIO_Class()
    minio_obj.put_object(normalised(playbook["database-id"]), "analysis-"+normalised(playbook["analysis-id"])+"/visualization-"+normalised(job["step"])+"/", io.BytesIO(b""), 0,)

    form_data = {
        "analysis-id" : analysis_id,
        "job-id" : job_id,
        "last-job-id" : last_job_id,
        "last-job-title" : last_job_title,
        "minio-output" : minio_output,
        "minio-input" : minio_input
    }

    # Start Loading Service
    service_obj = Diastema_Service()
    service_obj.startService("visualization", form_data)

    # Wait for loading to End
    job_res = service_obj.waitForService("visualization", job["id"])

    if job_res["status"] == "error":
        # Contact front end for the error of the job
        front_obj = FrontEnd_Class()
        front_obj.diastema_call(message = "error", update = job_res["message"]+" for the analysis with ID: "+playbook["analysis-id"])
        return minio_output, True

    # Insert the visualization data in MongoDB
    job_record = {"minio-path": minio_output, "directory-kind":"visualization", "job-json":job}

    mongo_obj = MongoDB_Class()
    mongo_obj.insertMongoRecord(normalised(playbook["database-id"]), "analysis_"+normalised(playbook["analysis-id"]), job_record)

    # Update Mongo Web Application metadata
    mongo_obj.updateMongoVisualization("UIDB", "pipelines", { "analysisid" :  playbook["analysis-id"]}, {"label": job["label"], "value": minio_output})

    # Contact front end to make a visualization
    front_obj = FrontEnd_Class()
    front_obj.diastema_call(message = "update", update = "Visualization Executed for the analysis with ID: "+playbook["analysis-id"])
    
    # dummy return
    return "visualization-from: "+last_bucket, False