# Qanary Helpers library
[![PyPI](https://img.shields.io/pypi/v/qanary-helpers.svg)](https://pypi.org/project/qanary-helpers/)
[![Tests](https://github.com/Perevalov/qanary_helpers/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Perevalov/qanary_helpers/actions/workflows/python-tests.yml)
![Downloads](https://img.shields.io/pypi/dm/qanary_helpers)
![Repo size](https://img.shields.io/github/repo-size/perevalov/qanary_helpers)

Qanary Helpers implements registration and querying functionality for [the Qanary framework](https://github.com/WDAqua/Qanary).

This library is used within a Python Qanary Component.

## Install

### Via PIP

```bash
pip install qanary_helpers
```

### Latest version from GitHub

```bash
git clone https://github.com/Perevalov/qanary_helpers.git
cd qanary_helpers
pip install .
```

## Usage

For the "Hello world example" create a file named `component.py` in your working directory. Then, fill the file with the
following code (pay attention to the `TODO` comments):

```python
import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
import uvicorn

from qanary_helpers.registration import Registration
from qanary_helpers.registrator import Registrator
from qanary_helpers.qanary_queries import insert_into_triplestore, get_text_question_in_graph
from qanary_helpers.logging import MLFlowLogger

if not os.getenv("PRODUCTION"):
    from dotenv import load_dotenv
    load_dotenv() # required for debugging outside Docker

SPRING_BOOT_ADMIN_URL = os.environ['SPRING_BOOT_ADMIN_URL']    
SPRING_BOOT_ADMIN_USERNAME = os.environ['SPRING_BOOT_ADMIN_USERNAME']
SPRING_BOOT_ADMIN_PASSWORD = os.environ['SPRING_BOOT_ADMIN_PASSWORD']
SERVICE_HOST = os.environ['SERVICE_HOST']
SERVICE_PORT = os.environ['SERVICE_PORT']
SERVICE_NAME_COMPONENT = os.environ['SERVICE_NAME_COMPONENT']
SERVICE_DESCRIPTION_COMPONENT = os.environ['SERVICE_DESCRIPTION_COMPONENT']
URL_COMPONENT = f"{SERVICE_HOST}" # While using server with permanent external IP address: URL_COMPONENT = f"http://{SERVICE_HOST}:{SERVICE_PORT}"

app = FastAPI()


@app.post("/annotatequestion")
async def qanary_service(request: Request):
    request_json = await request.json()
    triplestore_endpoint_url = request_json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph_uuid = request_json["values"]["urn:qanary#inGraph"]
    
    # get question text from triplestore
    question_text = get_text_question_in_graph(triplestore_endpoint_url, triplestore_ingraph_uuid)[0]['text']

    # Start TODO: configure your business logic here and adjust the sparql query
    
    # here we simulate that our component created this sparql query:
    sparql_query = """
        PREFIX dbr: <http://dbpedia.org/resource/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        SELECT * WHERE {
        dbr:Angela_Merkel dbo:birthPlace ?uri .
        }
    """
    # and this "generated" query is stored in the triplestore with this INSERT query:
    SPARQLquery = """
                    PREFIX dbr: <http://dbpedia.org/resource/>
                    PREFIX dbo: <http://dbpedia.org/ontology/>
                    PREFIX qa: <http://www.wdaqua.eu/qa#>
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
                    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                    INSERT {{
                    GRAPH <{uuid}> {{
                        ?newAnnotation rdf:type qa:AnnotationOfAnswerSPARQL .
                        ?newAnnotation oa:hasTarget <{question_uri}> .
                        ?newAnnotation oa:hasBody \"{sparql_query}\"^^xsd:string .
                        ?newAnnotation qa:score \"1.0\"^^xsd:float .
                        ?newAnnotation oa:annotatedAt ?time .
                        ?newAnnotation oa:annotatedBy <urn:qanary:{component}> .
                        }}
                    }}
                    WHERE {{
                        BIND (IRI(str(RAND())) AS ?newAnnotation) .
                        BIND (now() as ?time) 
                    }}
                """.format(
                    uuid=triplestore_ingraph_uuid,
                    question_uri=triplestore_endpoint_url,
                    component=SERVICE_NAME_COMPONENT.replace(" ", "-"),
                    sparql_query=sparql_query.replace("\n", "\\n").replace("\"", "\\\""))

    insert_into_triplestore(triplestore_endpoint_url,
                            SPARQLquery)  # inserting new data to the triplestore
    
    # Initializing logging with MLFlow
    # TODO: Update connection settings, if necessary
    logger = MLFlowLogger()
    
    # logging the annotation of the component
    # TODO: replace "sparql_query" with your annotation data
    logger.log_annotation(SERVICE_NAME_COMPONENT, question_text, sparql_query, triplestore_ingraph_uuid)
    
    # End TODO

    return JSONResponse(content=request_json)


@app.get("/health")
def health():
    return PlainTextResponse(content="alive") 


metadata = {
    "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "description": SERVICE_DESCRIPTION_COMPONENT,
    "written in": "Python"
}

print(metadata)

registration = Registration(
    name=SERVICE_NAME_COMPONENT,
    serviceUrl=f"{URL_COMPONENT}",
    healthUrl=f"{URL_COMPONENT}/health",
    metadata=metadata
)

reg_thread = Registrator(SPRING_BOOT_ADMIN_URL, SPRING_BOOT_ADMIN_USERNAME,
                        SPRING_BOOT_ADMIN_PASSWORD, registration)
reg_thread.setDaemon(True)
reg_thread.start()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(SERVICE_PORT))
```

As you may see, several environment variables has to be set before the script execution:
* `SPRING_BOOT_ADMIN_URL` -- URL of the Qanary pipeline (see Step 1 and Step 2 of the [tutorial](https://github.com/WDAqua/Qanary/wiki/Qanary-tutorial:-How-to-build-a-trivial-Question-Answering-pipeline))
* `SPRING_BOOT_ADMIN_USERNAME` -- the admin username of the Qanary pipeline
* `SPRING_BOOT_ADMIN_PASSWORD` -- the admin password of the Qanary pipeline
* `SERVICE_HOST` -- the host of your component without protocol prefix (e.g. `http://`). It has to be visible to the Qanary pipeline
* `SERVICE_PORT` -- the port of your component (has to be visible to the Qanary pipeline)
* `SERVICE_NAME_COMPONENT` -- the name of your component
* `SERVICE_DESCRIPTION_COMPONENT` -- the description of your component

You may also change the configuration via environment variables to any configuration that you want (e.g. via a `json` file).

To run the component, simply execute `python component.py` in your terminal. 
If the component registration was successful, a corresponding message will appear in the output.
