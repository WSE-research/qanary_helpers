# Qanary Helpers library
[![PyPI](https://img.shields.io/pypi/v/qanary-helpers.svg)](https://pypi.org/project/qanary-helpers/)
[![Python package](https://github.com/Perevalov/qanary_helpers/actions/workflows/python-tests.yml/badge.svg)](https://github.com/Perevalov/qanary_helpers/actions/workflows/python-tests.yml)

Qanary Helpers implements registration and configuration functionality for [the Qanary framework](https://github.com/WDAqua/Qanary).

Typically, this library is used within a Qanary component written in Python. Examples of how to use the library are given below.

`app.py` file for your Qanary component:

```
import logging
import argparse
from flask import Flask, render_template
from datetime import datetime

from qanary_helpers.configuration import Configuration
from qanary_helpers.registration import Registration
from qanary_helpers.registrator import Registrator
from answer_type_classifier import answer_type_classifier

# default config file (use -c parameter on command line specify a custom config file)
configfile = "app.conf"

# endpoint for Web page containing information about the service
aboutendpoint = "/about"

# endpoint for health information of the service required for Spring Boot Admin server callback
healthendpoint = "/health"

# initialize Flask app and add the externalized service information
app = Flask(__name__)
app.register_blueprint(answer_type_classifier)

# holds the configuration
configuration = None


@app.route(healthendpoint, methods=['GET'])
def health():
    """required health endpoint for callback of Spring Boot Admin server"""
    return "alive"


@app.route(aboutendpoint)
def about():
    """optional endpoint for serving a web page with information about the web service"""
    return render_template("about.html", configuration=configuration)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

    # allow configuration of the configfile via command line parameters
    argparser = argparse.ArgumentParser(
        description='You might provide a configuration file, otherwise "%s" is used.' % (configfile))
    argparser.add_argument('-c', '--configfile', action='store', dest='configfile', default=configfile,
                           help='overwrite the default configfile "%s"' % (configfile))
    configfile = argparser.parse_args().configfile
    configuration = Configuration(configfile, [
        'springbootadminserverurl',
        'springbootadminserveruser',
        'springbootadminserverpassword',
        'servicehost',
        'serviceport',
        'servicename',
        'servicedescription',
        'serviceversion'
    ])

    try:
        configuration.serviceport = int(configuration.serviceport)  # ensure an int value for the server port
    except Exception as e:
        logging.error(
            "in configfile '%s': serviceport '%s' is not valid (%s)" % (configfile, configuration.serviceport, e))

    # define metadata that will be shown in the Spring Boot Admin server UI
    metadata = {
        "start": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": configuration.servicedescription,
        "about": "%s:%d%s" % (configuration.servicehost, configuration.serviceport, aboutendpoint),
        "written in": "Python"
    }

    # initialize the registation object, to be send to the Spring Boot Admin server
    myRegistration = Registration(
        name=configuration.servicename,
        serviceUrl="%s:%d" % (configuration.servicehost, configuration.serviceport),
        healthUrl="%s:%d%s" % (configuration.servicehost, configuration.serviceport, healthendpoint),
        metadata=metadata
    )

    # start a thread that will contact iteratively the Spring Boot Admin server
    registratorThread = Registrator(
        configuration.springbootadminserverurl,
        configuration.springbootadminserveruser,
        configuration.springbootadminserverpassword,
        myRegistration
    )
    registratorThread.start()

    # start the web service
    app.run(debug=True, port=configuration.serviceport)
```


`my_component.py` file:

```
from flask import Blueprint, jsonify, request
from qanary_helpers.configuration import Configuration
from qanary_helpers.qanary_queries import get_text_question_in_graph, insert_into_triplestore
import requests
import json
import logging


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

answer_type_classifier = Blueprint('answer_type_classifier', __name__, template_folder='templates')

# default config file (use -c parameter on command line specify a custom config file)
configfile = "app.conf"

configuration = Configuration(configfile, [
        'servicename', 
        'serviceversion'
        ])

@answer_type_classifier.route("/annotatequestion", methods=['POST'])
def qanaryService():
    """the POST endpoint required for a Qanary service"""
    
    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph  = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    logging.info("endpoint: %s, inGraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    text = get_text_question_in_graph(triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph)[0]['text']
    
    logging.info(f'Question Text: {text}')
    
    //implement your functionality here

    #building SPARQL query
    SPARQLquery = """
                    PREFIX qa: <http://www.wdaqua.eu/qa#>
                    PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
                    PREFIX dbo: <http://dbpedia.org/ontology/>

                    INSERT {{
                    GRAPH <{uuid}> {{
                        //insert some information here

                        ?a oa:annotatedBy <urn:qanary:{app_name}> .
                        ?a oa:annotatedAt ?time .
                        }}
                    }}
                    WHERE {{
                        BIND (IRI(str(RAND())) AS ?a) .
                        BIND (now() as ?time) 
                    }}
                """.format(
                    uuid=triplestore_ingraph,
                    app_name="{0}:{1}:Python".format(configuration.servicename, configuration.serviceversion)
                )
    
    logging.info(f'SPARQL: {SPARQLquery}')

    insert_into_triplestore(triplestore_endpoint, triplestore_ingraph, SPARQLquery) #inserting new data to the triplestore

    return jsonify(request.get_json())

@answer_type_classifier.route("/", methods=['GET'])
def index():
    """an examplary GET endpoint returning "hello world (String)"""
    logging.info("host_url: %s" % (request.host_url,))
    return "Hi! \n This is Answer Type Classification component, based on DBpedia Ontology."


@answer_type_classifier.route("/", methods=['POST'])
def indexJson():
    """a POST endpoint returning a hello world JSON"""
    data = {'Hello': 'World'}
    return jsonify(data)
```

`app.conf` file:

```
[ServiceConfiguration]
# the URL of the Spring Boot Admin server endpoint (e.g., http://localhost:8080)
springbootadminserverurl = http://localhost:8080/
# Spring Boot Admin server credentials (by default: admin, admin)
springbootadminserveruser = admin
springbootadminserverpassword = admin
# the name of your service (e.g., my service)
servicename = my_component
# the port (integer) of your service (e.g., 5000)
serviceport = 1130
# the host of your service (e.g., http://127.0.0.1)
servicehost = http://127.0.0.1
# a description of your service functionality 
servicedescription = My component description
# version of component
serviceversion = 0.1.0
```
