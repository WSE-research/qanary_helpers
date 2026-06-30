"""End-to-end smoke test: the installed package exposes its public API.

This guards against import-time regressions (e.g. a dependency bump breaking a
module) for everyone who depends on qanary-helpers to build Qanary components.
"""
import pytest

pytestmark = pytest.mark.e2e


def test_public_api_is_importable():
    from qanary_helpers.registration import Registration
    from qanary_helpers.registrator import Registrator
    from qanary_helpers.qanary_queries import (
        get_text_question_in_graph,
        insert_into_triplestore,
        query_triplestore,
        select_from_triplestore,
    )
    from qanary_helpers.language_queries import (
        QuestionTextWithLanguage,
        create_annotation_of_question_language,
        create_annotation_of_question_translation,
    )

    # the value objects construct and behave as documented
    reg = Registration(name="n", healthUrl="h")
    assert reg.name == "n"
    q = QuestionTextWithLanguage(uri="u", text="t", lang="en")
    assert (q.get_uri(), q.get_text(), q.get_language()) == ("u", "t", "en")

    # every documented helper is exposed as a callable
    for fn in (
        Registrator,
        get_text_question_in_graph,
        insert_into_triplestore,
        query_triplestore,
        select_from_triplestore,
        create_annotation_of_question_language,
        create_annotation_of_question_translation,
    ):
        assert callable(fn)
