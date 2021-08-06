import pytest

from legal_advice_builder.models import Question

from ..helpers import get_text_question


@pytest.mark.django_db
def test_string(document_factory):
    document = document_factory(name='Document')
    assert str(document) == 'Document'


@pytest.mark.django_db
def test_get_initial_fields_dict(text_block_factory,
                                 document_factory):

    document = document_factory()
    text_block_factory(
        document=document,
        content='{{ something }}'
    )

    assert len(document.get_initial_fields_dict()) == 1
    assert document.get_initial_fields_dict()[0].get('document') == document.id
    assert document.get_initial_fields_dict()[0].get('content') == '{{ something }}'


@pytest.mark.django_db
def test_get_initial_questions_dict(law_case_factory,
                                    questionaire_factory,
                                    text_block_factory,
                                    document_factory):

    document = document_factory()

    law_case = law_case_factory(
        document=document
    )
    questionaire_1 = questionaire_factory(
        short_title='qn_1',
        law_case=law_case,
        order=1
    )
    q1 = question = Question.add_root(
        **(get_text_question(
            short_title='first_name',
            questionaire=questionaire_1
        ))
    )
    q2 = question.add_child(
        **(get_text_question(
            short_title='last_name',
            questionaire=questionaire_1
        ))
    )

    q2.add_child(
        **(get_text_question(
            short_title='city',
            questionaire=questionaire_1
        ))
    )

    document.sample_answers = [
        {"question": str(q1.id), "text": "Mickey"},
        {"question": str(q2.id), "text": "Mouse"}
    ]
    document.save()

    tb = text_block_factory(
        document=document,
        content='{{ qn_1_first_name }}',
        order=0
    )

    assert str(tb) == '{{ qn_1_first_name }}'

    text_block_factory(
        document=document,
        content='{{ qn_1_last_name }} {{ qn_1_city }}',
        order=1
    )

    assert len(document.get_initial_questions_dict()) == 3
    assert document.get_initial_questions_dict()[0].get('question') == str(q1.id)
    assert document.get_initial_questions_dict()[0].get('text') == 'Mickey'

    assert document.get_initial_questions_dict()[1].get('question') == str(q2.id)
    assert document.get_initial_questions_dict()[1].get('text') == 'Mouse'


@pytest.mark.django_db
def test_template(text_block_factory,
                  document_factory):

    document = document_factory()

    text_block_factory(
        document=document,
        order=1,
        content='<p>{{ qn_1_first_name }}</p>'
    )

    text_block_factory(
        document=document,
        order=2,
        content='<p>{{ qn_1_last_name }}</p>'
    )

    assert document.template == '<p>{{ qn_1_first_name }}</p> <p>{{ qn_1_last_name }}</p>'


@pytest.mark.django_db
def test_template_with_answers(law_case_factory,
                               questionaire_factory,
                               text_block_factory,
                               document_factory,
                               answer_factory):

    document = document_factory()

    law_case = law_case_factory(
        document=document
    )
    questionaire_1 = questionaire_factory(
        short_title='qn_1',
        law_case=law_case,
        order=1
    )
    q1 = question = Question.add_root(
        **(get_text_question(
            short_title='first_name',
            questionaire=questionaire_1
        ))
    )
    q2 = question.add_child(
        **(get_text_question(
            short_title='last_name',
            questionaire=questionaire_1
        ))
    )

    answer = answer_factory(
        law_case=law_case,
        answers=[
            {"question": str(q1.id), "text": "Mickey"},
            {"question": str(q2.id), "text": "Mouse"}
        ]
    )

    text_block_factory(
        document=document,
        content='<p>{{ answers.qn_1_first_name }}</p>',
        order=1
    )

    text_block_factory(
        document=document,
        content='{{ answers.qn_1_last_name }}',
        order=2
    )

    document.sample_answers = [
        {"question": str(q1.id), "text": "Donald"},
        {"question": str(q2.id), "text": "Duck"}
    ]
    document.save()

    assert document.template_with_answers(answer.answers) == '<p>Mickey</p> Mouse'
    assert document.template_with_sample_answers == '<p>Donald</p> Duck'
