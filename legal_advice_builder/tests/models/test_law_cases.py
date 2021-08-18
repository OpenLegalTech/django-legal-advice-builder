import pytest

from legal_advice_builder.models import Question

from ..helpers import get_date_question
from ..helpers import get_single_option_question
from ..helpers import get_text_question


@pytest.mark.django_db
def test_str(law_case_factory):
    law_case = law_case_factory(
        title='Law Case'
    )
    assert str(law_case) == 'Law Case'


@pytest.mark.django_db
def test_get_first_questionaire(law_case_factory, questionaire_factory):

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
    assert law_case.first_questionaire == questionaire_1


@pytest.mark.django_db
def test_get_index_of_questionaire(law_case_factory, questionaire_factory):

    law_case = law_case_factory()
    questionaire_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    questionaire_2 = questionaire_factory(
        law_case=law_case,
        order=5
    )
    questionaire_3 = questionaire_factory(
        law_case=law_case,
        order=3
    )
    assert law_case.get_index_of_questionaire(questionaire_1) == 0
    assert law_case.get_index_of_questionaire(questionaire_2) == 2
    assert law_case.get_index_of_questionaire(questionaire_3) == 1


@pytest.mark.django_db
def test_questionaire_count(law_case_factory, questionaire_factory):

    law_case = law_case_factory()
    questionaire_factory(
        law_case=law_case,
        order=1
    )
    questionaire_factory(
        law_case=law_case,
        order=5
    )
    questionaire_factory(
        law_case=law_case,
        order=3
    )
    assert law_case.questionaire_count() == 3


@pytest.mark.django_db
def test_generate_default_questionaires(law_case_factory, document_factory):

    law_case = law_case_factory()
    law_case.generate_default_questionaires()
    assert law_case.questionaire_count() == 1

    document = document_factory()
    law_case = law_case_factory(document=document)
    law_case.generate_default_questionaires()
    assert law_case.questionaire_count() == 1


@pytest.mark.django_db
def test_placeholders_for_template(law_case_factory, questionaire_factory):
    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1,
        short_title=''
    )
    qn_2 = questionaire_factory(
        law_case=law_case,
        order=2,
        short_title=''
    )

    q1_1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))

    q1_2 = q1_1.add_child(
        **(get_single_option_question(
            questionaire=qn_1)))

    q2_1 = Question.add_root(
        **(get_date_question(
            questionaire=qn_2)))

    q2_2 = q2_1.add_child(
        **(get_text_question(
            questionaire=qn_2)))

    variables = law_case.placeholders_for_template

    q1_1_string = 'questionaire_{}_question_{}'.format(qn_1.id, q1_1.id)
    q1_2_string = 'questionaire_{}_question_{}'.format(qn_1.id, q1_2.id)
    q2_1_string = 'questionaire_{}_question_{}'.format(qn_2.id, q2_1.id)
    q2_2_string = 'questionaire_{}_question_{}'.format(qn_2.id, q2_2.id)

    assert q1_1_string in variables.keys()
    assert variables[q1_1_string] == Question.objects.get(id=q1_1.id).text

    assert q1_2_string in variables.keys()
    assert variables[q1_2_string] == Question.objects.get(id=q1_2.id).text

    assert q2_1_string in variables.keys()
    assert variables[q2_1_string] == Question.objects.get(id=q2_1.id).text

    assert q2_2_string in variables.keys()
    assert variables[q2_2_string] == Question.objects.get(id=q2_2.id).text
    assert len(variables.keys()) == 4


@pytest.mark.django_db
def test_placeholders_for_template_with_short_titles(law_case_factory, questionaire_factory):
    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1,
        short_title='qn_1'
    )
    qn_2 = questionaire_factory(
        law_case=law_case,
        order=2,
        short_title='qn_2'
    )

    q1_1 = Question.add_root(
        **(get_single_option_question(
            short_title='q1_1',
            questionaire=qn_1)))

    q1_2 = q1_1.add_child(
        **(get_single_option_question(
            questionaire=qn_1)))

    q2_1 = Question.add_root(
        **(get_date_question(
            questionaire=qn_2)))

    q2_2 = q2_1.add_child(
        **(get_text_question(
            questionaire=qn_2)))

    variables = law_case.placeholders_for_template

    q1_1_string = 'qn_1_q1_1'
    q1_2_string = 'qn_1_question_{}'.format(q1_2.id)
    q2_1_string = 'qn_2_question_{}'.format(q2_1.id)
    q2_2_string = 'qn_2_question_{}'.format(q2_2.id)

    assert q1_1_string in variables.keys()
    assert variables[q1_1_string] == Question.objects.get(id=q1_1.id).text

    assert q1_2_string in variables.keys()
    assert variables[q1_2_string] == Question.objects.get(id=q1_2.id).text

    assert q2_1_string in variables.keys()
    assert variables[q2_1_string] == Question.objects.get(id=q2_1.id).text

    assert q2_2_string in variables.keys()
    assert variables[q2_2_string] == Question.objects.get(id=q2_2.id).text
    assert len(variables.keys()) == 4
