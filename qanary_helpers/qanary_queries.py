import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from urllib.parse import urlparse
import re


def get_text_question_from_uri(triplestore_endpoint: str, question_uri: str) -> str:
    """Retrieves the textual representation for a question identified by a URI

    Keyword arguments:
    triplestore_endpoint (str) -- URL of the triplestore endpoint
    question_uri (str) -- URI of the question

    Returns:
    str -- The question text

    """
    question_raw = question_uri + "/raw"
    logging.info("found: questionURI={0}  questionURIraw={1}".format(
        question_uri,
        question_raw
    ))
    hostname = urlparse(triplestore_endpoint).hostname
    if hostname == None:
        raise ValueError("No valid host name could be extracted from the supplied triplestore_endpoint: {0}"
                         .format(triplestore_endpoint))
    question_text = requests.get(question_raw.replace("localhost", hostname))
    return question_text.text


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
        SELECT DISTINCT ?questionURI
        FROM <{uri}>
        WHERE {{
            ?questionURI rdf:type <http://www.wdaqua.eu/qa#Question> .
        }}
    """.format(uri=graph)

    results = select_from_triplestore(triplestore_endpoint, query)
    for result in results["results"]["bindings"]:
        question_uri = result['questionURI']['value']
        question_text = get_text_question_from_uri(triplestore_endpoint, question_uri)
        logging.info("found question: \"{0}\"".format(question_text))
        questions.append({"uri": question_uri, "text": question_text})

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
    triplestore_endpoint_parsed_split = re.split(
        "^(\w+):(\w+)@(.*)$", triplestore_endpoint_parsed.netloc)
    if len(triplestore_endpoint_parsed_split) > 1:
        # qanary v2 and lower
        username = triplestore_endpoint_parsed_split[1]
        password = triplestore_endpoint_parsed_split[2]
        triplestore_endpoint_new = triplestore_endpoint_parsed.scheme + "://" + triplestore_endpoint_parsed_split[3] + \
            triplestore_endpoint_parsed.path
        sparql = SPARQLWrapper(triplestore_endpoint_new)
        sparql.setCredentials(username, password)
        logging.info("found: endpoint=%s,  username=%s,  password=%s" %
                     (triplestore_endpoint_new, username, password))
    else:
        # qanary v3
        triplestore_endpoint_new = re.sub('/query$', '', triplestore_endpoint)
        triplestore_endpoint_new = re.sub(
            '/update$', '', triplestore_endpoint_new)
        sparql = SPARQLWrapper(triplestore_endpoint_new)
        logging.info("found: endpoint=%s" % triplestore_endpoint_new)

    logging.info("execute SPARQL query:\n%s" % sparql_query)

    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    results = sparql.query().convert()
    logging.debug(results)
    return results
