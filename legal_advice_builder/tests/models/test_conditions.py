import datetime

import pytest
from freezegun import freeze_time

from legal_advice_builder.models import Question

from ..helpers import get_date_question
from ..helpers import get_text_question


@pytest.mark.django_db
def test_stra(condition_factory):

    q1 = Question.add_root(
        **(get_text_question()))

    condition_1 = condition_factory(
        if_option='is',
        if_value='yes',
        then_value='success',
        question=q1
    )

    assert str(condition_1) == 'if answer is "yes" then success'


@pytest.mark.django_db
def test_evaluate_date(condition_factory):

    q1 = Question.add_root(
        **(get_date_question()))

    q2 = Question.add_root(
        **(get_date_question()))

    condition_1 = condition_factory(
        if_option='deadline_running',
        if_value='months_+3',
        question=q1
    )

    condition_2 = condition_factory(
        if_option='deadline_expired',
        if_value='months_+3',
        question=q2
    )

    condition_3 = condition_factory(
        if_option='is',
        if_value='yes',
        then_value='success',
        question=q1
    )

    with freeze_time('2020-05-10'):
        date_1 = datetime.date(2020, 4, 10)
        assert condition_1.evaluate_date(date_1)

        date_2 = datetime.date(2020, 1, 10)
        assert condition_2.evaluate_date(date_2)
        assert not condition_3.evaluate_date(date_2)
