"""Unit tests for language_queries: the value object, the SPARQL annotation
builders, and the triplestore-reading helpers (with select_from_triplestore
faked)."""
from qanary_helpers import language_queries as lq
from qanary_helpers.language_queries import QuestionTextWithLanguage


def test_question_text_with_language_getters():
    q = QuestionTextWithLanguage(uri="urn:q", text="Hallo", lang="de")
    assert q.get_uri() == "urn:q"
    assert q.get_text() == "Hallo"
    assert q.get_language() == "de"


def test_create_annotation_of_question_translation_contains_fields():
    query = lq.create_annotation_of_question_translation(
        graph_uri="urn:graph",
        question_uri="urn:q",
        translation="Hello",
        translation_language="en",
        app_name="MyTranslator",
    )
    assert "AnnotationOfQuestionTranslation" in query
    assert "urn:graph" in query
    assert "<urn:q>" in query
    assert '"Hello"@en' in query
    assert "urn:qanary:MyTranslator" in query


def test_create_annotation_of_question_language_contains_fields():
    query = lq.create_annotation_of_question_language(
        graph_uri="urn:graph",
        question_uri="urn:q",
        language="en",
        app_name="LangDetect",
    )
    assert "AnnotationOfQuestionLanguage" in query
    assert '"en"^^xsd:string' in query
    assert "urn:qanary:LangDetect" in query


def test_get_texts_with_detected_language(monkeypatch):
    monkeypatch.setattr(
        lq, "select_from_triplestore",
        lambda ep, q: {"results": {"bindings": [{"hasTarget": {"value": "urn:q1"}}]}},
    )
    monkeypatch.setattr(lq, "get_text_question_from_uri", lambda triplestore_endpoint, question_uri: "Bonjour")
    result = lq.get_texts_with_detected_language_in_triplestore("http://ts", "urn:graph", "fr")
    assert len(result) == 1
    assert result[0].get_uri() == "urn:q1"
    assert result[0].get_text() == "Bonjour"
    assert result[0].get_language() == "fr"


def test_get_translated_texts(monkeypatch):
    monkeypatch.setattr(
        lq, "select_from_triplestore",
        lambda ep, q: {"results": {"bindings": [
            {"hasTarget": {"value": "urn:q2"}, "hasBody": {"value": "Hello"}}
        ]}},
    )
    result = lq.get_translated_texts_in_triplestore("http://ts", "urn:graph", "en")
    assert len(result) == 1
    assert result[0].get_text() == "Hello"
    assert result[0].get_language() == "en"
