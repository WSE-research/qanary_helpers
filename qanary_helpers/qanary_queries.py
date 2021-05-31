import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from urllib.parse import urlparse
from pprint import pprint
import re


def get_text_question_in_graph(triplestore_endpoint, graph):
    """
    Retrieves the questions from the triplestore returns an array

    Keyword arguments:
    triplestore_endpoint -- URL of the triplestore endpoint
    graph -- URI of the graph to query inside of the triplestore
    """
    questions = list()
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (?s AS ?questionURI) (URI(CONCAT(STR(?s),"/raw")) AS ?questionURIraw)
        FROM <{uri}> 
        WHERE {{
            ?s ?p ?o . 
            ?s rdf:type <http://www.wdaqua.eu/qa#Question> .
        }}
    """.format(uri=graph)

    results = select_from_triplestore(triplestore_endpoint, query)
    for result in results["results"]["bindings"]:
        logging.info("found: questionURI={0}  questionURIraw={1}".format(
            result['questionURI']['value'],
            result['questionURIraw']['value']
        ))
        question_text = requests.get(result['questionURIraw']['value'].replace(
            "localhost", urlparse(triplestore_endpoint).hostname)
        )
        logging.info("found question: \"{0}\"".format(question_text.text))
        questions.append({"uri": result['questionURI']['value'], "text": question_text.text})
    
    pprint(questions)
    return questions


def select_from_triplestore(triplestore_endpoint, sparql_query):
    """
    Executes SELECT query on triplestore and returns the result object

    Keyword arguments:
    triplestore_endpoint -- URL of the triplestore endpoint
    sparql_query -- a query to execute on the endpoint
    """ 
    # required for Stardog
    return query_triplestore(triplestore_endpoint+"/query", sparql_query)


def insert_into_triplestore(triplestore_endpoint, sparql_query):
    """
    Executes INSERT query on triplestore and returns the result object

    Keyword arguments:
    triplestore_endpoint -- URL of the triplestore endpoint
    sparql_query -- a query to execute on the endpoint
    """ 
    # required for Stardog
    return query_triplestore(triplestore_endpoint+"/update", sparql_query)


def query_triplestore(triplestore_endpoint, sparql_query):
    """
    Executes query on the triplestore and returns the result object

    Keyword arguments:
    triplestore_endpoint -- URL of the triplestore endpoint
    sparql_query -- a query to execute on the endpoint
    """
    triplestore_endpoint_parsed = urlparse(triplestore_endpoint)
    triplestore_endpoint_parsed_split = re.split("^(\w+):(\w+)@(.*)$", triplestore_endpoint_parsed.netloc)
    username = triplestore_endpoint_parsed_split[1]
    password = triplestore_endpoint_parsed_split[2]
    triplestore_endpoint_new = triplestore_endpoint_parsed.scheme + "://" + triplestore_endpoint_parsed_split[3] + \
                               triplestore_endpoint_parsed.path
    logging.info("found: endpoint=%s,  username=%s,  password=%s" % (triplestore_endpoint_new, username, password))
    logging.info("execute SPARQL query:\n%s" % sparql_query)
    sparql = SPARQLWrapper(triplestore_endpoint_new)
    sparql.setCredentials(username, password)
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    results = sparql.query().convert()
    logging.debug(results)
    return results
