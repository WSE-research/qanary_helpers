"""Deterministic unit tests for qanary_queries (no live SPARQL endpoint).

SPARQLWrapper and requests are faked so the endpoint-parsing, credential and
query-routing logic can be exercised offline.
"""
from unittest.mock import MagicMock

import pytest

from qanary_helpers import qanary_queries as qq


class FakeSPARQL:
    """Records how query_triplestore configured the SPARQLWrapper."""

    last = None

    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.credentials = None
        self.query_str = None
        self.return_format = None
        self.method = None
        FakeSPARQL.last = self

    def setCredentials(self, user, password):
        self.credentials = (user, password)

    def setQuery(self, q):
        self.query_str = q

    def setReturnFormat(self, fmt):
        self.return_format = fmt

    def setMethod(self, method):
        self.method = method

    def query(self):
        result = MagicMock()
        result.convert.return_value = {"results": {"bindings": []}}
        return result


@pytest.fixture(autouse=True)
def fake_sparql(monkeypatch):
    monkeypatch.setattr(qq, "SPARQLWrapper", FakeSPARQL)


def test_query_triplestore_v3_strips_query_suffix():
    qq.query_triplestore("http://triplestore:8080/query", "SELECT * WHERE {?s ?p ?o}")
    assert FakeSPARQL.last.endpoint == "http://triplestore:8080"
    assert FakeSPARQL.last.credentials is None
    assert FakeSPARQL.last.method == "POST"


def test_query_triplestore_extracts_embedded_credentials():
    qq.query_triplestore("http://user:secret@triplestore:8080/", "SELECT * WHERE {?s ?p ?o}")
    # the user:pass@ portion is parsed out and applied as credentials
    assert FakeSPARQL.last.credentials == ("user", "secret")
    assert "user:secret@" not in FakeSPARQL.last.endpoint


def test_select_and_insert_route_to_query_and_update(monkeypatch):
    calls = []
    monkeypatch.setattr(qq, "query_triplestore", lambda ep, q: calls.append(ep))
    qq.select_from_triplestore("http://ts", "SELECT 1")
    qq.insert_into_triplestore("http://ts", "INSERT 1")
    assert calls == ["http://ts/query", "http://ts/update"]


def test_get_text_question_from_uri_requires_hostname():
    with pytest.raises(ValueError):
        qq.get_text_question_from_uri(triplestore_endpoint="not-a-url", question_uri="urn:q")


def test_get_text_question_from_uri_fetches_raw(monkeypatch):
    captured = {}

    def fake_get(url):
        captured["url"] = url
        resp = MagicMock()
        resp.text = "What is the capital of France?"
        return resp

    monkeypatch.setattr(qq.requests, "get", fake_get)
    text = qq.get_text_question_from_uri(
        triplestore_endpoint="http://ts-host:8080/query",
        question_uri="http://localhost:8080/question/1",
    )
    assert text == "What is the capital of France?"
    # the "localhost" in the question URI is rewritten to the endpoint host
    assert "ts-host" in captured["url"]
    assert captured["url"].endswith("/raw")


def test_get_text_question_in_graph_collects_questions(monkeypatch):
    monkeypatch.setattr(
        qq, "select_from_triplestore",
        lambda ep, q: {"results": {"bindings": [{"questionURI": {"value": "urn:q1"}}]}},
    )
    monkeypatch.setattr(qq, "get_text_question_from_uri", lambda triplestore_endpoint, question_uri: "Q text")
    questions = qq.get_text_question_in_graph("http://ts", "urn:graph")
    assert questions == [{"uri": "urn:q1", "text": "Q text"}]
