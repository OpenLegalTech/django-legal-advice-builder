import pytest

from legal_advice_builder.models import Questionaire

from legal_advice_builder.models import Question
from ..helpers import get_text_question
from ..helpers import get_single_option_question


@pytest.mark.django_db
def test_string(questionaire_factory):

    questionaire = questionaire_factory(
        title='Questionaire'
    )
    assert str(questionaire) == 'Questionaire'


@pytest.mark.django_db
def test_last(questionaire_factory):

    questionaire = questionaire_factory(
        title='Questionaire'
    )
    q1 = Question.add_root(
        **get_text_question(
            questionaire=questionaire
        )
    )
    q2 = q1.add_child(
        **get_text_question(
            questionaire=questionaire
        )
    )
    assert questionaire.get_last_question() == q2


@pytest.mark.django_db
def test_add_new_after_question(questionaire_factory):
    qn = questionaire_factory()

    q1 = Question.add_root(
        **get_text_question(
            questionaire=qn
        )
    )
    q2 = q1.add_child(
        **get_text_question(
            questionaire=qn
        )
    )
    data = get_text_question(questionaire=qn)
    qn.add_new_after_question(data, parent_question=q1.id)

    assert q1.get_children().count() == 1
    child = q1.get_children().first()
    assert child.get_children().first() == q2

    qn2 = questionaire_factory()
    data = get_text_question(questionaire=qn2)
    qn.add_new_after_question(data)
    assert qn2.questions.count() == 1


@pytest.mark.django_db
def test_has_error(questionaire_factory):

    qn = questionaire_factory()
    q1 = Question.add_root(
        **get_single_option_question(
            questionaire=qn
        )
    )
    q1.options = {}
    q1.save()
    assert qn.has_error


@pytest.mark.django_db
def test_next(law_case_factory, questionaire_factory):

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
