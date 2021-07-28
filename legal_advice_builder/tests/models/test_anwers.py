import pytest

from legal_advice_builder.models import Question

from ..helpers import get_text_question


@pytest.mark.django_db
def test_str(answer_factory, law_case_factory):

    law_case = law_case_factory(title='Title')
    answer = answer_factory(
        law_case=law_case
    )
    assert str(answer) == 'Title'


@pytest.mark.django_db
def test_save(answer_factory):

    html_with_script = '<script>alert("hallo")</script>'
    answer = answer_factory(
        rendered_document=html_with_script,
    )

    assert answer.rendered_document == 'alert("hallo")'

    html_with_h1 = '<h1>hallo</h1>'
    answer = answer_factory(
        rendered_document=html_with_h1,
    )

    assert answer.rendered_document == html_with_h1


@pytest.mark.django_db
def test_template(law_case_factory,
                  questionaire_factory,
                  document_type_factory,
                  document_field_type_factory,
                  document_field_factory,
                  document_factory,
                  answer_factory):

    document_type = document_type_factory(
        document_template='<p>{{ first_name }} {{ last_name }}</p>'
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

    assert answer.template == '<p>Mickey Mouse</p>'

    answer.save_rendered_document()

    assert answer.rendered_document == '<p>Mickey Mouse</p>'
