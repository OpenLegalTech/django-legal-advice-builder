import pytest

from legal_advice_builder.models import Questionaire


@pytest.mark.django_db
def test_questionaires(law_case_factory, questionaire_factory):

    law_case = law_case_factory()
    questionaire_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    questionaire_2 = questionaire_factory(
        law_case=law_case,
        order=2
    )
    questionaire_factory()
    assert Questionaire.objects.all().count() == 3
    assert questionaire_1.next() == questionaire_2
    assert questionaire_2.next() is None
