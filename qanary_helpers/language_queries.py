from qanary_helpers.qanary_queries import select_from_triplestore


class question_text_with_language:

    def __init__(self, uri: str, text: str, lang: str):
        self.uri = uri
        self.text = text
        self.lang = lang

    def get_uri(self):
        return self.uri

    def get_text(self):
        return self.text

    def get_language(self):
        return self.lang


def get_texts_with_detected_language_in_triplestore(triplestore_endpoint: str, graph_uri: str, lang: str) -> list[question_text_with_language]:
    source_texts = list()
    sparql_find_ld = """
        PREFIX qa: <http://www.wdaqua.eu/qa#>
        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT *
        FROM <{graph}>
        WHERE {{
        ?annotationId a qa:AnnotationOfQuestionLanguage .
        ?annotationId oa:hasTarget ?hasTarget ;
          oa:hasBody ?hasBody ;
          oa:annotatedBy ?annotatedBy ;
          oa:annotatedAt ?annotatedAt .
        FILTER(STR(?hasBody) = {lang})
        }}
    """.format(
        graph = graph_uri,
        lang=lang
    )
    results = select_from_triplestore(triplestore_endpoint, sparql_find_ld)
    for result in results["results"]["bindings"]:
        question_uri = result["hasTarget"]["value"]
        question_text = get_question_text_from_uri(question_uri, triplestore_endpoint)
        source_texts.append(question_text_with_language(uri=question_uri, text=question_text, lang=lang))

    return source_texts


def get_translated_texts_in_triplestore(triplestore_endpoint: str, graph_uri: str, lang: str) -> list[question_text_with_language]:
    source_texts = list()
    sparql_find_ld = """
        PREFIX qa: <http://www.wdaqua.eu/qa#>
        PREFIX oa: <http://www.w3.org/ns/openannotation/core/>

        SELECT *
        FROM <{graph}>
        WHERE {{
            ?annotationId a qa:AnnotationOfQuestionTranslation .
            ?annotationId oa:hasTarget ?hasTarget ;
                          oa:hasBody ?hasBody ;
                          oa:annotatedBy ?annotatedBy ;
                          oa:annotatedAt ?annotatedAt .
            FILTER(lang(?hasBody) = {lang}).
        }}
    """.format(
        graph = graph_uri,
        lang=lang
    )
    results = select_from_triplestore(triplestore_endpoint, sparql_find_ld)
    for result in results["results"]["bindings"]:
        question_uri = result["hasTarget"]["value"]
        question_text = result["hasBody"]["value"]
        source_texts.append(question_text_with_language(question_uri, question_text, lang))

    return source_texts
