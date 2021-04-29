import pytest

from legal_advice_builder.models import Question, Questionaire

from .helpers import get_single_option_question, get_text_question


@pytest.mark.django_db
def test_lawcase(law_case_factory, questionaire_factory):

    law_case = law_case_factory()
    questionaire_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    questionaire_factory(
        law_case=law_case,
        order=2
    )
    assert law_case.get_first_questionaire() == questionaire_1


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


@pytest.mark.django_db
def test_questions(law_case_factory, questionaire_factory):

    law_case = law_case_factory()
    questionaire_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    questionaire_2 = questionaire_factory(
        law_case=law_case,
        order=2
    )
    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=questionaire_1)))
    q1.success_options = ['unsure']
    q1_yes = q1.add_child(
        **(get_single_option_question(
            questionaire=questionaire_1,
            parent_option='yes')))
    q1_no = q1.add_child(
        **(get_single_option_question(
            questionaire=questionaire_1,
            parent_option='no')))

    assert questionaire_1.get_first_question() == q1
    assert questionaire_1.questions.count() == 3
    assert q1.next(option='yes') == q1_yes
    assert q1.next(option='no') == q1_no
    assert q1.next(option='unsure') is None

    q2 = Question.add_root(
        **(get_text_question(
            questionaire=questionaire_2
        )))

    assert q1.next(option='unsure') == q2
    assert q2.next() is None
    assert q2.next(option='test') is None
