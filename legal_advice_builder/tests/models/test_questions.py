import datetime

import pytest
from freezegun import freeze_time

from legal_advice_builder.models import Condition
from legal_advice_builder.models import Question

from ..helpers import get_date_question
from ..helpers import get_single_option_question
from ..helpers import get_text_question


@pytest.mark.django_db
def test_question_next(law_case_factory, questionaire_factory):

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

    Condition.objects.create(
        question=q1,
        if_option='is',
        if_value='unsure',
        then_value='success'
    )
    q1_yes = q1.add_child(
        **(get_single_option_question(
            questionaire=questionaire_1)))
    q1_no = q1_yes.add_child(
        **(get_single_option_question(
            questionaire=questionaire_1)))

    Condition.objects.create(
        question=q1,
        if_option='is',
        if_value='yes',
        then_value='question',
        then_question=q1_yes
    )

    Condition.objects.create(
        question=q1,
        if_option='is',
        if_value='no',
        then_value='question',
        then_question=q1_no
    )

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


@pytest.mark.django_db
def test_question_conditions_date_deadline_running():

    question = Question.add_root(
        **(get_date_question())
    )

    Condition.objects.create(
        question=question,
        if_option='deadline_running',
        if_value='months_+3',
        then_value='failure'
    )

    with freeze_time('2020-05-10'):
        inserted_date = datetime.date(2020, 4, 10)
        assert question.is_status_by_conditions('failure', date=inserted_date)

        inserted_date = datetime.date(2020, 1, 21)
        assert not question.is_status_by_conditions('failure', date=inserted_date)


@pytest.mark.django_db
def test_question_conditions_date_unit():

    question = Question.add_root(
        **(get_date_question())
    )

    Condition.objects.create(
        question=question,
        if_option='deadline_running',
        if_value='days_+10',
        then_value='failure'
    )

    with freeze_time('2020-05-16'):
        inserted_date = datetime.date(2020, 5, 13)
        assert question.is_status_by_conditions('failure', date=inserted_date)

        inserted_date = datetime.date(2020, 5, 1)
        assert not question.is_status_by_conditions('failure', date=inserted_date)


@pytest.mark.django_db
def test_question_conditions_date_deadline_expired():

    question = Question.add_root(
        **(get_date_question())
    )

    Condition.objects.create(
        question=question,
        if_option='deadline_expired',
        if_value='months_+3',
        then_value='failure'
    )

    with freeze_time('2020-05-10'):
        inserted_date = datetime.date(2020, 4, 10)
        assert not question.is_status_by_conditions('failure', date=inserted_date)

        inserted_date = datetime.date(2020, 1, 21)
        assert question.is_status_by_conditions('failure', date=inserted_date)
