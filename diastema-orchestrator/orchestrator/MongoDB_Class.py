import os
from pymongo import MongoClient

class MongoDB_Class:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))

    def __init__(self):
        mongo_host = MongoDB_Class.MONGO_HOST+":"+str(MongoDB_Class.MONGO_PORT)
        self.mongo_client = MongoClient("mongodb://"+mongo_host+"/")
        return
    
    def insertMongoRecord(self, client, collection, record):
        mongo_db = self.mongo_client[client]
        analysis_collection = mongo_db[collection]
        analysis_collection.insert_one(record)
        return
    
    def updateMongoFeatures(self, client, collection, filters, features):
        mongo_db = self.mongo_client[client]
        analysis_collection = mongo_db[collection]
        analysis_collection.update_one(filters, {"$set": {'features': features}})
        return
    
    def updateMongoVisualization(self, client, collection, filters, metadata):
        mongo_db = self.mongo_client[client]
        analysis_collection = mongo_db[collection]

        # Get the current metadata
        metadata_dict = analysis_collection.find_one(filters)
        if "visualization" in metadata_dict:
            metadata_dict = metadata_dict["visualization"]
        else:
            metadata_dict = {}

        metadata_dict[metadata["label"]] = metadata["value"]
            
        # Update the metadata
        analysis_collection.update_one(filters, {"$set": {'visualization': metadata_dict}})
        return

    def updateMetadataStatus(self, client, collection, analysis_id):
        mongo_db = self.mongo_client[client]
        analysis_collection = mongo_db[collection]
        analysis_collection.update_one({"analysisid" : analysis_id}, {"$set": {'status': "completed"}})
        return
    
    def updateMongoPerformanceMetrics(self, client, collection, filters, metadata):
        mongo_db = self.mongo_client[client]
        analysis_collection = mongo_db[collection]

        # Get the current metadata
        metadata_dict = analysis_collection.find_one(filters)
        if "performance" in metadata_dict:
            metadata_dict = metadata_dict["performance"]
        else:
            metadata_dict = {}

        metadata_dict[metadata["label"]] = metadata["value"]
            
        # Update the metadata
        analysis_collection.update_one(filters, {"$set": {'performance': metadata_dict}})
        return
    
    def insertDataToolkitParams(self, job_id, params):
        mongo_db = self.mongo_client["Diastema"]
        datatoolkit_collection = mongo_db["datatoolkit"]

        # Make the record to insert in MongoDB

        toolkit_record = {"job-id": str(job_id)}

        # Insert the params
        for param in params:
            toolkit_record[param] = params[param]

        # Remove not needed params
        if "max-trials" in toolkit_record:
            del toolkit_record["max-trials"]
        
        if "meta-learning" in toolkit_record:
            del toolkit_record["meta-learning"]

        # Insert the record
        datatoolkit_collection.insert_one(toolkit_record)
        return
