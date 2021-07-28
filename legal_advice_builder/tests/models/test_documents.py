import pytest

from legal_advice_builder.models import Question

from ..helpers import get_text_question


@pytest.mark.django_db
def test_string(document_factory):
    document = document_factory(name='Document')
    assert str(document) == 'Document'


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
        name='Letter',
        document_template='<div>{{ first_name }} {{ last_name }}</div>'
    )

    assert str(document_type) == 'Letter'

    field_type_1 = document_field_type_factory(
        document_type=document_type,
        name='First Name'
    )
    field_type_1.slug = ''
    field_type_1.save()

    assert str(field_type_1) == 'First Name'
    assert field_type_1.slug == 'first_name'

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

    df = document_field_factory(
        document=document,
        field_type=field_type_1,
        content='{{ qn_1_first_name }}'
    )

    assert str(df) == '{{ qn_1_first_name }}'

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='{{ qn_1_last_name }} {{ qn_1_city }}'
    )

    assert len(document.get_initial_questions_dict()) == 3
    assert document.get_initial_questions_dict()[0].get('question') == str(q1.id)
    assert document.get_initial_questions_dict()[0].get('text') == 'Mickey'

    assert document.get_initial_questions_dict()[1].get('question') == str(q2.id)
    assert document.get_initial_questions_dict()[1].get('text') == 'Mouse'


@pytest.mark.django_db
def test_fields_for_context(document_type_factory,
                            document_field_type_factory,
                            document_field_factory,
                            document_factory):

    document_type = document_type_factory()
    field_type_1 = document_field_type_factory(
        slug='field_type_1'
    )

    document = document_factory(document_type=document_type)
    document_field_factory(
        document=document,
        field_type=field_type_1,
        content='<strong>{{ something }}</strong>'
    )

    assert len(document.fields_for_context().keys()) == 1
    assert document.fields_for_context().get('field_type_1') == '<strong>{{ something }}</strong>'


@pytest.mark.django_db
def test_template(document_type_factory,
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

    document_field_factory(
        document=document,
        field_type=field_type_1,
        content='<p>{{ qn_1_first_name }}</p>'
    )

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='<p>{{ qn_1_last_name }}</p>'
    )

    assert document.template == '<div><p>{{ qn_1_first_name }}</p> <p>{{ qn_1_last_name }}</p></div>'


@pytest.mark.django_db
def test_template_with_answers(law_case_factory,
                               questionaire_factory,
                               document_type_factory,
                               document_field_type_factory,
                               document_field_factory,
                               document_factory,
                               answer_factory):

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

    answer = answer_factory(
        law_case=law_case,
        answers=[
            {"question": str(q1.id), "text": "Mickey"},
            {"question": str(q2.id), "text": "Mouse"}
        ]
    )

    document_field_factory(
        document=document,
        field_type=field_type_1,
        content='{{ answers.qn_1_first_name }}'
    )

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='{{ answers.qn_1_last_name }}'
    )

    document.sample_answers = [
        {"question": str(q1.id), "text": "Donald"},
        {"question": str(q2.id), "text": "Duck"}
    ]
    document.save()

    assert document.template_with_answers(answer.answers) == '<div>Mickey Mouse</div>'
    assert document.template_with_sample_answers == '<div>Donald Duck</div>'
