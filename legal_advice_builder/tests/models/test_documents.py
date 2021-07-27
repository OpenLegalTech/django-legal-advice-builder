import pytest

from legal_advice_builder.models import Question

from ..helpers import get_text_question


@pytest.mark.django_db
def test_get_value_for_field(document_type_factory,
                             document_field_type_factory,
                             document_field_factory,
                             document_factory):

    document_type = document_type_factory()
    field_type_1 = document_field_type_factory()
    field_type_2 = document_field_type_factory()

    document = document_factory(document_type=document_type)
    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='{{ something }}'
    )

    assert document.get_value_for_field(field_type_1) == ''
    assert document.get_value_for_field(field_type_2) == '{{ something }}'


@pytest.mark.django_db
def test_get_initial_fields_dict(document_type_factory,
                                 document_field_type_factory,
                                 document_field_factory,
                                 document_factory):

    document_type = document_type_factory()

    field_type_1 = document_field_type_factory(
        document_type=document_type,
        name='First Name',
        slug='first_name'
    )

    field_type_2 = document_field_type_factory(
        document_type=document_type,
        name='Last Name',
        slug='last_name'
    )

    document = document_factory(document_type=document_type)
    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='{{ something }}'
    )

    assert len(document.get_initial_fields_dict()) == 2
    assert document.get_initial_fields_dict()[0].get('field_slug') == 'first_name'
    assert document.get_initial_fields_dict()[0].get('field_type') == field_type_1.id
    assert document.get_initial_fields_dict()[0].get('field_name') == 'First Name'
    assert document.get_initial_fields_dict()[0].get('document') == document.id
    assert document.get_initial_fields_dict()[0].get('content') == ''

    assert document.get_initial_fields_dict()[1].get('field_slug') == 'last_name'
    assert document.get_initial_fields_dict()[1].get('field_type') == field_type_2.id
    assert document.get_initial_fields_dict()[1].get('field_name') == 'Last Name'
    assert document.get_initial_fields_dict()[1].get('document') == document.id
    assert document.get_initial_fields_dict()[1].get('content') == '{{ something }}'


@pytest.mark.django_db
def test_get_initial_questions_dict(law_case_factory,
                                    questionaire_factory,
                                    document_type_factory,
                                    document_field_type_factory,
                                    document_field_factory,
                                    document_factory):

    document_type = document_type_factory(
        document_template='<div>{{ first_name }} {{ last_name }}</div>'
    )

    field_type_1 = document_field_type_factory(
        document_type=document_type,
        name='First Name',
        slug='first_name'
    )

    field_type_2 = document_field_type_factory(
        document_type=document_type,
        name='Last Name',
        slug='last_name'
    )

    document = document_factory(document_type=document_type)

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

    document.sample_answers = [
        {"question": str(q1.id), "text": "Mickey"},
        {"question": str(q2.id), "text": "Mouse"}
    ]
    document.save()

    document_field_factory(
        document=document,
        field_type=field_type_1,
        content='{{ qn_1_first_name }}'
    )

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='{{ qn_1_last_name }}'
    )

    assert len(document.get_initial_questions_dict()) == 2
    assert document.get_initial_questions_dict()[0].get('question') == str(q1.id)
    assert document.get_initial_questions_dict()[0].get('text') == 'Mickey'

    assert document.get_initial_questions_dict()[1].get('question') == str(q2.id)
    assert document.get_initial_questions_dict()[1].get('text') == 'Mouse'
