# Import custom Libraries
from normalizing import normalised

from MinIO_Class import MinIO_Class
from Diastema_Service import Diastema_Service

# Import Libraries
import io

def data_ingestion(playbook):
    # Bucket to Ingest data inside
    load_bucket = normalised(playbook["database-id"])+"/datasets/"+normalised(playbook["dataset-label"])

    # Make the load Bucket directory
    minio_obj = MinIO_Class()
    minio_obj.make_bucket(normalised(playbook["database-id"]))
    minio_obj.put_object(normalised(playbook["database-id"]), "datasets/"+normalised(playbook["dataset-label"])+"/", io.BytesIO(b""), 0,)

    # Make call for the Data Ingestion Service
    ingestion_info = {
        "minio-output" : load_bucket, 
        "job-id" : normalised(playbook["ingestion-id"]),
        "url" : playbook["link"],
        "method" : playbook["method"],
        "token" : playbook["token"]
    }

    # Start Ingestion Service
    service_obj = Diastema_Service()
    service_obj.startService("data-ingesting", ingestion_info)

    # Wait for Ingestion to end
    service_obj.waitForService("data-ingesting", playbook["ingestion-id"])

    # Get Ingestion results (List of the Dataset's features)
    features = service_obj.getServiceResults("data-ingesting", playbook["ingestion-id"])

    return features