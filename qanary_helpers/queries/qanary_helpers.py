import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
from urllib.parse import urlparse
from pprint import pprint
import re
import uuid


def get_text_question_in_graph(triplestore_endpoint, graph):
    """
        retrieves the questions from the triplestore returns an array
    """
    questions = []
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT (?s AS ?questionURI) (URI(CONCAT(STR(?s),"/raw")) AS ?questionURIraw)
        FROM <%s> 
        WHERE {
            ?s ?p ?o . 
            ?s rdf:type <http://www.wdaqua.eu/qa#Question> .
        }
    """ % graph
    results = select_from_triplestore(triplestore_endpoint, graph, query)
    for result in results["results"]["bindings"]:
        logging.info("found: questionURI=%s  questionURIraw=%s" % (result['questionURI']['value'], result['questionURIraw']['value']) )
        questionText = requests.get(result['questionURIraw']['value'])
        logging.info("found question: \""+questionText.text+"\"")
        questions.append({"uri": result['questionURI']['value'], "text": questionText.text})
    
    pprint(questions)
    return questions


def get_computed_sparql_query_as_answer(triplestore_endpoint, graph):
    """
        retrieves the SPARQL query from the triplestore that should be executed to get the answer from the knowledge graph
    """
    query = """
        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
        PREFIX qa: <http://www.wdaqua.eu/qa#> 
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT *
        FROM <%s> 
        WHERE {
            ?s ?p ?o . 
            ?s rdf:type qa:AnnotationOfAnswerSPARQL .
        }
    """ % graph 
    results = select_from_triplestore(triplestore_endpoint, graph, query)
    
    for result in results["results"]["bindings"]:
        logging.info("found triple: %s %s %s " % (result['s']['value'], result['p']['value'], result['o']['value']) )
    
    return results


def getTextSelectors(triplestore_endpoint, graph):
    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        SELECT * 
        FROM <%s>
        WHERE {
            ?annotation rdf:type <http://www.wdaqua.eu/qa#AnnotationOfInstance>.
            ?annotation ?p ?o 

            OPTIONAL {
                ?o ?p2 ?o2
                OPTIONAL {
                    ?o2 ?p3 ?o3
                }
            }
        }
    """ % graph
    results = select_from_triplestore(triplestore_endpoint, graph, query)
    return results


def select_from_triplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute SELECT query on triplestore and returns the result object
    """ 
    # required for Stardog
    return query_triplestore(triplestore_endpoint+"/query", graph, SPARQLquery)


def insert_into_triplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute INSERT query on triplestore and returns the result object
    """ 
    # required for Stardog
    return query_triplestore(triplestore_endpoint+"/update", graph, SPARQLquery)


def query_triplestore(triplestore_endpoint, graph, SPARQLquery):
    """
        execute query on the triplestore and returns the result object
    """
    triplestore_endpoint_parsed=urlparse(triplestore_endpoint)
    triplestore_endpoint_parsed_split=re.split("^(\w+):(\w+)@(.*)$", triplestore_endpoint_parsed.netloc)
    username = triplestore_endpoint_parsed_split[1]
    password = triplestore_endpoint_parsed_split[2]
    triplestore_endpoint_new=triplestore_endpoint_parsed.scheme+"://"+triplestore_endpoint_parsed_split[3]+triplestore_endpoint_parsed.path
    logging.info("found: endpoint=%s,  username=%s,  password=%s" % (triplestore_endpoint_new, username, password))
    logging.info("execute SPARQL query:\n%s" % SPARQLquery)
    sparql = SPARQLWrapper(triplestore_endpoint_new)
    sparql.setCredentials(username, password)
    sparql.setQuery(SPARQLquery);
    sparql.setReturnFormat(JSON)
    sparql.setMethod("POST")
    results = sparql.query().convert()
    logging.debug(results)
    return results


"""@myservice.route("/annotatequestion", methods=['POST'])
def qanaryService():

    triplestore_endpoint = request.json["values"]["urn:qanary#endpoint"]
    triplestore_ingraph = request.json["values"]["urn:qanary#inGraph"]
    triplestore_outgraph = request.json["values"]["urn:qanary#outGraph"]

    logging.info("endpoint: %s, ingraph: %s, outGraph: %s" % (triplestore_endpoint, triplestore_ingraph, triplestore_outgraph))

    print("\n")
    print("\n")
    print(request.get_json())
    print("\n")
    print("\n")


    # use this if you want to get the textual input of the user (i.e., the question)
    questions = getTextQuestionInGraph( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("found questions (actually there should only be one) in current graph: %s" % triplestore_ingraph)
    pprint(questions )

    # use this if you want to retrieve the SPARQL query that might be generated by a QueryBuilder component
    results = getComputedSparqlQueryAsAnswer( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("results of getComputedSparqlQueryAsAnswer in current graph: %s" % triplestore_ingraph)
    pprint(results)

    # use this if you want to get the markers in a text (e.g., from DBpedia Spotlight)
    results = getTextSelectors( triplestore_endpoint=triplestore_endpoint, graph=triplestore_ingraph )
    pprint("results of getTextQuestionInGraph in current graph: %s" % triplestore_ingraph)
    pprint(results)


    return jsonify(request.get_json())"""

