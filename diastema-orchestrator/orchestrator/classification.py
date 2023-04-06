# Import custom Libraries
from normalizing import normalised
from automl import execute_automl

from MongoDB_Class import MongoDB_Class
from MinIO_Class import MinIO_Class
from FrontEnd_Class import FrontEnd_Class
from Kubernetes_Class import Kubernetes_Class

# Import Libraries
import io

def classification(playbook, job, last_bucket, algorithm=False, tensorfow_algorithm=False):
    algorithms = {
        "false" : "false",                              # Algorithm not selected
        "decision tree classifier" : "decisiontree",
        "random forest classifier" : "randomForest",
        "logistic regression" : "logisticregression",
        "gradient boosted tree classifier" : "gbt",
        "multilayer perceptron" : "mlp",
        "linear support vector machine" : "linearsvc",
        "onevsrest" : "onevsrest",
        "naive bayes" : "naivebayes",
        "factorization machines" : "fm"
    }

    algorithm_to_use = ""
    default_job = "decision tree classifier"
    if algorithm==False:
        algorithm_to_use = algorithms[default_job]
    else:
        if algorithm in algorithms:
            algorithm_to_use = algorithms[algorithm]
            if algorithm_to_use == False:
                algorithm_to_use = algorithms[default_job]
        else:
            algorithm_to_use = algorithms[default_job]
    
    # Path of classification in Diastema docker image
    analysis_path = "/app/src/ClassificationJob.py"

    # Data Bucket = last jobs output bucket
    data_bucket = last_bucket

    #################
    # Call AutoML if the user wants to use it
    automl_results = False
    if job["automl"] == True:
        if algorithm_to_use != "false" : 
            job["params"]["algorithm"] = algorithm_to_use
        automl_results = execute_automl(data_bucket, "classification", job["id"], job["column"], job["params"])
        if automl_results["status"] == "error":
            return automl_results["message"], True
        algorithm_to_use = automl_results["results"]["algorithm"]
        job["params"] = automl_results["results"]
        job["params"].pop("algorithm")
        # automl_execution_time = automl_results["exec-speed"]  ####### In the future we need to handle this As a backend and frontend issue
    ################# Update possible performance metrics as well

    # Update MongoDB with the parameters of the job
    mongo_obj = MongoDB_Class()
    mongo_obj.insertDataToolkitParams(job["id"], job["params"])

    # Analysis Bucket = User/analysis-id/job-step
    analysis_bucket = normalised(playbook["database-id"])+"/analysis-"+normalised(playbook["analysis-id"])+"/classified-"+normalised(job["step"])

    # Jobs arguments
    job_args = [analysis_path, algorithm_to_use, data_bucket, analysis_bucket, job["column"], job["id"], playbook["analysis-id"]]

    # Make the MinIO Analysis buckers
    minio_obj = MinIO_Class()
    minio_obj.put_object(normalised(playbook["database-id"]), "analysis-"+normalised(playbook["analysis-id"])+"/classified-"+normalised(job["step"])+"/", io.BytesIO(b""), 0,)

    # Make the Spark call
    spark_call_obj = Kubernetes_Class()
    spark_call_obj.spark_caller(job_args)
    
    # Remove the _SUCCESS file from the  spark job results
    minio_obj.remove_object(normalised(playbook["database-id"]), "analysis-"+normalised(playbook["analysis-id"])+"/classified-"+normalised(job["step"])+"/_SUCCESS")
    
    # Insert the classified data in MongoDB
    classification_job_record = {"minio-path":analysis_bucket, "directory-kind":"classified-data", "job-json":job}

    mongo_obj.insertMongoRecord(normalised(playbook["database-id"]), "analysis_"+normalised(playbook["analysis-id"]), classification_job_record)

    # Contact front end for the ending of the job
    front_obj = FrontEnd_Class()
    front_obj.diastema_call(message = "update", update = "Classification executed for the analysis with ID: "+playbook["analysis-id"])

    # Return the bucket that this job made output to 
    return analysis_bucket, False