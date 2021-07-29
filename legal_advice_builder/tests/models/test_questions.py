import datetime

import pytest
from freezegun import freeze_time

from legal_advice_builder.models import Condition
from legal_advice_builder.models import Question

from ..helpers import get_date_question
from ..helpers import get_single_option_question
from ..helpers import get_text_question
from ..helpers import get_yes_no_question


@pytest.mark.django_db
def test_save(questionaire_factory):
    qn = questionaire_factory()
    q1 = Question.add_root(
        **(get_yes_no_question(
            questionaire=qn)))
    q1.save()
    assert list(q1.options.keys()) == ['yes', 'no']


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

    law_case_2 = law_case_factory()
    questionaire_3 = questionaire_factory(
        law_case=law_case_2,
        order=1
    )

    q2 = Question.add_root(
        **(get_single_option_question(
            questionaire=questionaire_3)))

    Condition.objects.create(
        question=q2,
        if_option='is',
        if_value='unsure',
        then_value='success'
    )

    assert q2.next(option='unsure') is None

    law_case_3 = law_case_factory()
    questionaire_4 = questionaire_factory(
        law_case=law_case_3,
        order=1
    )
    questionaire_5 = questionaire_factory(
        law_case=law_case_3,
        order=2
    )

    q3 = Question.add_root(
        **(get_single_option_question(
            questionaire=questionaire_4)))

    q4 = Question.add_root(
        **(get_single_option_question(
            questionaire=questionaire_5)))

    assert q3.next() == q4


@pytest.mark.django_db
def test_get_status(law_case_factory, questionaire_factory, ):
    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        success_message='Success'
    )

    question = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1
        ))
    )

    assert question.get_status(option='yes') == {
        'success': True,
        'message': 'Success',
        'next': None
    }


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


@pytest.mark.django_db
def test_prepare_for_delete():

    q1 = Question.add_root(
        **(get_text_question()))
    q1.add_child(
        **(get_text_question()))

    q1.prepare_for_delete()
    assert not q1.get_children()

    q2 = Question.add_root(
        **(get_text_question()))
    q3 = q2.add_child(
        **(get_text_question()))
    q4 = q3.add_child(
        **(get_text_question()))

    q3.prepare_for_delete()
    assert not q3.get_children()
    assert q2.get_children().last() == q4
    assert Question.objects.get(id=q4.id).get_parent() == q2


@pytest.mark.django_db
def test_get_unsure_message(questionaire_factory):
    qn = questionaire_factory(
        unsure_message='unsure'
    )
    q = Question.add_root(
        **(get_text_question(questionaire=qn)))
    assert q.get_unsure_message() == 'unsure'


@pytest.mark.django_db
def test_get_options_by_type():
    q1 = Question.add_root(**get_single_option_question())
    for type in q1.FIELD_TYPES:
        q1.field_type = type[0]
        q1.save()
        assert q1.get_options_by_type() is not None

    for field_type in [q1.SINGLE_OPTION, q1.MULTIPLE_OPTIONS, q1.YES_NO]:
        q1.field_type = field_type
        q1.save()
        assert list(q1.get_options_by_type().keys()) == ['is']


@pytest.mark.django_db
def test_get_if_text_by_type():
    q1 = Question.add_root(**get_single_option_question())
    for type in q1.FIELD_TYPES:
        q1.field_type = type[0]
        q1.save()
        assert not q1.get_if_text_by_type() == ''

    q1.field_type = 'test'
    q1.save()
    assert q1.get_if_text_by_type() == ''


@pytest.mark.django_db
def test_get_options_names():
    q1 = Question.add_root(**get_single_option_question())
    assert q1.get_options_names() == 'yes, no, maybe'


@pytest.mark.django_db
def test_icon():
    q1 = Question.add_root(**get_single_option_question())
    for type in q1.FIELD_TYPES:
        q1.field_type = type[0]
        q1.save()
        assert q1.icon is not None


@pytest.mark.django_db
def test_erros():
    q1 = Question.add_root(**get_single_option_question())
    q1.options = {}
    q1.save()
    assert q1.has_error


@pytest.mark.django_db
def test_clean_up_conditions():
    q1 = Question.add_root(**get_single_option_question())

    Condition.objects.create(
        question=q1,
        if_option='is',
        if_value='maybe',
        then_value='success'
    )
    assert q1.conditions.count() == 1
    q1.options = {
        'yes': 'yes',
        'no': 'no',
    }
    q1.save()
    q1.clean_up_conditions(list(q1.options.keys()))
    assert q1.conditions.count() == 0


@pytest.mark.django_db
def test_get_dict_key(questionaire_factory):
    qn = questionaire_factory(
        short_title='qn'
    )
    q1 = Question.add_root(**get_single_option_question(
        questionaire=qn
    ))

    assert q1.get_dict_key(option='yes') == ('qn_question_1', 'Yes')

    q1.field_type = q1.MULTIPLE_OPTIONS
    q1.save()

    assert q1.get_dict_key(option=['yes', 'maybe']) == ('qn_question_1', ['Yes', 'Maybe'])

    q2 = Question.add_root(**get_date_question(
        questionaire=qn
    ))

    assert q2.get_dict_key(date='2021-05-10') == ('qn_question_2', '2021-05-10')


@pytest.mark.django_db
def test_string():
    q1 = Question.add_root(**get_single_option_question())
    assert str(q1) == '{} {} ({})'.format('', q1.text, q1.get_options_names())
    q1.short_title = 'question'
    q1.field_type = q1.TEXT
    q1.save()
    assert str(q1) == '{}: {}'.format('question', q1.text)
