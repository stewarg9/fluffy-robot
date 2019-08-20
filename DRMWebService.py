###############################
#
#    Read a template and substitute with data values from a CSV file. 
#    Use a Queue and multi-thread the calls to the web service.  

import csv
import requests

from queue import Queue
from threading import Thread
from mako.template import Template


# Constants for the DRM Web Server
DEV_WSDL = 'http://HOST+NAME+HERE'
DEV_SERVER_URL = "HOST+NAME+HERE"


# Base directories. 
DATA_DIR = "C:\\Users\\kbzg512\\AnacondaProjects\\DRMWebService\\Data"
TEMPLATE_DIR = "C:\\Users\\kbzg512\\AnacondaProjects\\DRMWebService\\Templates"

# Specific files to process. 
data_file = DATA_DIR + '\Product_Move_Planning_Apps.csv'
template_file = TEMPLATE_DIR + '\Product_Move_Planning_Apps.xml'


# Set the size of the thread pool
num_threads = 5


def call_drm(q):
  while True:
    
    # Need to force the proxy to none, soince it's now an environment variable... 
    proxies = {
      "http": None,
      "https": None,
    }

    # Force no SSL validation. 
    session = requests.Session()
    session.verify = False

    # Read the tremplate data from the template file... 
    # Produces one big string. 
    with open(template_file, 'r') as temp_file:
      template_text = temp_file.read()        
    
    # Read in the template text from the file
    mytemplate = Template(template_text)    
    
    # Update the template with the parameters. 
    message_text = mytemplate.render(**q.get())    
    
    # Set the message headers up. 
    encoded_request = message_text.encode('utf-8')
    headers = {"Content-Type": "text/xml;charset=utf-8", 'SOAPAction': ""}
    
    # Call web service and output the response. 
    response = requests.post(url=DEV_WSDL, data=encoded_request, headers=headers,  proxies=proxies, timeout=100)
    print(response.content)    
    
    q.task_done()

    
# Set up the Queue structure   
q = Queue(maxsize=0)


# Create the thread objects and map them to the function. 
for i in range(num_threads):
  worker = Thread(target=call_drm, args=(q,), daemon=True)
  worker.start()



# Extract the parameter data from a CSV file; 
#    store it in an OrderedList of Dictionaries
# Templates can just use the key name (column name) 
#    for each row of data. 
reader = csv.DictReader(open(data_file, 'r'))

for data_row in reader: 
    
    # Output the rendered template using the data from the current row. 
    q.put(data_row)

    
q.join()