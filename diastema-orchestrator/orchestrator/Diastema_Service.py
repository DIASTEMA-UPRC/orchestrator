import requests
import os
import time

class Diastema_Service:
    DIASTEMA_SERVICES_HOST = os.getenv("DIASTEMA_SERVICES_HOST", "localhost")
    DIASTEMA_SERVICES_PORT = int(os.getenv("DIASTEMA_SERVICES_PORT", 5001))

    FUNCTION_SERVICE_HOST = os.getenv("FUNCTION_SERVICE_HOST", "localhost")
    FUNCTION_SERVICE_PORT = int(os.getenv("FUNCTION_SERVICE_PORT", 5001))

    def __init__(self):
        self.diastema_services_url = "http://"+Diastema_Service.DIASTEMA_SERVICES_HOST+":"+str(Diastema_Service.DIASTEMA_SERVICES_PORT)+"/"
        pass
    
    def is_func_service(self):
        self.diastema_services_url = "http://"+Diastema_Service.FUNCTION_SERVICE_HOST+":"+str(Diastema_Service.FUNCTION_SERVICE_PORT)+"/"
        return
    
    def startService(self, service_name, json_body):
        url = self.diastema_services_url+service_name
        requests.post(url, json=json_body)
        return
    
    def waitForService(self, service_name, job_id):
        url = self.diastema_services_url+service_name+"/progress?id="+str(job_id)
        responce = requests.get(url)
        while True:
            time.sleep(2)
            if ((responce.json())["status"] != "progress"):
                break
            print("[INFO] Again for:", service_name)
            responce = requests.get(url)
        return responce.json()
    
    def getServiceResults(self, service_name, job_id):
        url = self.diastema_services_url+service_name+"/"+str(job_id)
        responce = requests.get(url)
        return responce.json()

    def simpleServiceCall(self, service_name, json_body):
        url = self.diastema_services_url+service_name
        responce = requests.post(url, json=json_body)
        return responce.text, responce.status_code