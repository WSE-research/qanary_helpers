import pytest
from qanary_helpers.qanary_queries import query_triplestore, select_from_triplestore

@pytest.mark.network
def test_query_triplestore():
    triplestore_endpoint = "https://dbpedia.org/sparql"
    
    sparql_query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>

    SELECT DISTINCT ?s { 
    dbr:Angela_Merkel dbo:birthPlace ?s
    }
    """

    query_triplestore(triplestore_endpoint, sparql_query)
    query_triplestore(triplestore_endpoint + '/query', sparql_query)
    query_triplestore(triplestore_endpoint + '/update', sparql_query)

@pytest.mark.network
def test_select_from_triplestore():
    triplestore_endpoint = "https://dbpedia.org/sparql"
    
    sparql_query = """
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbr: <http://dbpedia.org/resource/>

    SELECT DISTINCT ?s { 
    dbr:Angela_Merkel dbo:birthPlace ?s
    }
    """

    select_from_triplestore(triplestore_endpoint, sparql_query)

if __name__ == "__main__":
    test_query_triplestore()