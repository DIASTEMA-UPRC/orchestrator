# Import custom Libraries
from normalizing import normalised

# Import custom Libraries
from MongoDB_Class import MongoDB_Class
from MinIO_Class import MinIO_Class
from FrontEnd_Class import FrontEnd_Class
from Diastema_Service import Diastema_Service

# Import Libraries
import io

DIASTEMA_VISUALIZATION_BUCKET = "diastemaviz"

def visualize(playbook, job, last_bucket):
    last_job_from_step = job["from"]

    # Use all the playbook to find the last job
    jobs = playbook["jobs"]

    for i_job in jobs:
        if(i_job["step"] == last_job_from_step):
            last_job_id = i_job["id"]
            break

    # Make the MinIO object
    minio_obj = MinIO_Class()

    # Insert the visualization data in MongoDB
    job_record = {"minio-path": DIASTEMA_VISUALIZATION_BUCKET+"/"+str(last_job_id), "directory-kind":"visualization", "job-json":job}

    mongo_obj = MongoDB_Class()
    mongo_obj.insertMongoRecord(normalised(playbook["database-id"]), "analysis_"+normalised(playbook["analysis-id"]), job_record)

    # Get object names from MinIO Storage
    graph_names = minio_obj.getObjectsOfPath(DIASTEMA_VISUALIZATION_BUCKET, str(last_job_id)+"/")
    path_names = []
    for graph_name in graph_names:
        path_names.append(DIASTEMA_VISUALIZATION_BUCKET+"/"+str(last_job_id)+"/"+graph_name)

    # Update Mongo Web Application metadata
    mongo_obj.updateMongoVisualization("UIDB", "pipelines", { "analysisid" :  playbook["analysis-id"]}, {"label": job["label"], "value": path_names})

    # Contact front end to make a visualization
    front_obj = FrontEnd_Class()
    front_obj.diastema_call(message = "update", update = "Visualization Executed for the analysis with ID: "+playbook["analysis-id"])
    
    # dummy return
    return "visualization-from: "+last_bucket, False