# DIASTEMA Orchestrator

## Description
DIASTEMA uses a system to manage all analytical procedures performed by its users [[1]](http).

This system receives a JSON graph that mentions in it all the necessary information for the execution of all procedures. This information refers to which jobs should run first before others, what job each one is, various variables, ids, and more.

The Orchestrator communicates with the DIASTEMA services which are only responsible for blindly performing the tasks given to them. Such services are, for example, the ingestion service for collecting data sets, the cleaning service for cleaning data, and others.

The orchestration system is capable of accessing and executing any graph that has specified starting and ending nodes. It does not matter how many starting or ending nodes there are. As it does not matter how many branchings or couplings there are within the graph. The Orchestrator algorithm is capable of executing even graphs that are essentially more than one graph (for example two starting and ending nodes that are connected directly respectively).

## Repository Contents
- diastema-orchestrator/orchestrator
  - The source code of the Orchestrator. It also contains a python virtual environment with all the needed libraries.
- diastema-orchestrator/dummy/diastema-services
  - Some dummy Diastema services in case that someone want to test the service locally. It also contains a python virtual environment with all the needed libraries.
- diastema-orchestrator/dummy/kubernetes-component
  - A dummy Kubernetes component for the analytics that the Orchestration system can call, in case that someone want to test the service locally. It also contains a python virtual environment with all the needed libraries.
- testing/JSONs
  - A repository with some JSONs that are given in case that someone wants to test the service locally.
- testing/Mongo
  - A repository containing a file to execute in a Mongo Database in case that someone wants to test the service locally.

The two below have Dockerfiles, giving the opportunity to use them with Docker if needed.
- diastema-orchestrator/orchestrator
- diastema-orchestrator/dummy/diastema-services

## Example of use
In this section, an example of how to use the source code of this repository is shown, using the files from the dummy and helping repositories.

### Prerequisites
Below is an example of prerequisites:
- Python
- Python Virtual Environment
- Linux OS
- MongoDB
- Postman
- MinIO

You can execute the functionality with other prerequisites and commands as well!

#### MongoDB Initialization
1. Open the MongoDB shell by typing "mongo" on a CMD and run the following commands:
```
use UIDB
db.dropDatabase()
use UIDB
db.datasets.insert( { "organization": "metis", "user": "panagiotis", "label": "ships" } )
db.datasets.insert( { "organization": "metis", "user": "panagiotis", "label": "boats" } )
cls
db.datasets.find()

```
The above can by copy and pasted from top to bottom and it will run automatically.
The commands exist in the testing folder.

#### Service Startup
2. Open three terminals inside the directories below:
- diastema-orchestrator/dummy/diastema-services/
- diastema-orchestrator/dummy/kubernetes-component/
- diastema-orchestrator/orchestrator/
3. Run the command below in all the Directories:
```
source venv/bin/activate
```
Now you have activated all the virtual environments.
4. Run the commands below on each respective directories:
- diastema-orchestrator/dummy/diastema-services/
```
python3 app.py
```
- diastema-orchestrator/orchestrator/
```
python3 app.py
```
- diastema-orchestrator/dummy/kubernetes-component/
```
python3 server.py
```

#### MinIO Initialization
5. Make sure that you have your MinIO running.

#### Usage
Now the Orchestrator and its dummy services are running. While you have some datasets ready for ingestion in MongoDB.

The next step is to call the Orchestrator to ingest them. Then you can start calling for analyzes from it.

6. Open Postman and execute the following requests:
- First Ingestion:
   - POST
   - URL: http://localhost:5000/ingestion
   - JSON BODY: The "ingestion_boats.json" from the repository named "testing/JSONs/"
- Second Ingestion:
   - POST
   - URL: http://localhost:5000/ingestion
   - JSON BODY: The "ingestion_ships.json" from the repository named "testing/JSONs/"

By executing the above request and getting a "STATUS CODE 202 CREATED" you know that the Orchestrator got your requests and has started processing them. It will call the Ingestion Service from the dummy services while organizing every result in MongoDB and in MinIO.

Your results will be ready when you will see the features of your dummy datasets by typing the command below in MongoDB shell:
```
use UIDB
db.datasets.find()
```

7. Start giving graphs in the Orchestrator to handle:
- First example graph:
   - POST
   - URL: http://localhost:5000/analysis
   - JSON BODY: The "join_test.json" from the repository named "testing/JSONs/"
- Second example graph:
   - POST
   - URL: http://localhost:5000/analysis
   - JSON BODY: The "function_test.json" from the repository named "testing/JSONs/"

By executing the above request and getting a "STATUS CODE 202 CREATED" you know that the Orchestrator got your requests and has started processing them. It will call every needed service from the dummy services while organizing every result in MongoDB and in MinIO.

In DIASTEMA it is also giving notifications to the Web Application.

By looking in the logs of each service you will be able to understand how it works in a better way.

You can also view your buckets in MinIO to see how the Orchestrator is organizing your results.

## References
- [1] https://diastema.gr/
