import json

import pytest
from django.forms.models import model_to_dict

from legal_advice_builder.forms import PrepareDocumentForm
from legal_advice_builder.forms import QuestionConditionForm
from legal_advice_builder.forms import QuestionCreateForm
from legal_advice_builder.forms import QuestionForm
from legal_advice_builder.forms import QuestionUpdateForm
from legal_advice_builder.forms import RenderedDocumentForm
from legal_advice_builder.models import Condition
from legal_advice_builder.models import Document
from legal_advice_builder.models import Question

from .helpers import get_question
from .helpers import get_single_option_question
from .helpers import get_text_question


@pytest.mark.django_db
def test_rendered_document_form(answer_factory):

    answer = answer_factory()
    form = RenderedDocumentForm(instance=answer)

    assert 'answer_id' in form.fields
    assert 'rendered_document' in form.fields
    assert form.fields['answer_id'].widget.input_type == 'hidden'


@pytest.mark.django_db
def test_prepare_docuement_form(document_factory,
                                document_type_factory):

    dt = document_type_factory()
    document = document_factory(
        document_type=dt
    )
    assert 'document_type' in PrepareDocumentForm(document=None).fields
    assert 'document_type' not in PrepareDocumentForm(document=document).fields
    assert PrepareDocumentForm(document=document).initial == model_to_dict(document)

    data = {'document_type': dt.id, 'name': 'Document'}

    assert Document.objects.all().count() == 1
    update_document_form = PrepareDocumentForm(document=document, data=data)
    update_document_form.is_valid()
    update_document_form.save()

    assert document.name == 'Document'

    new_document_form = PrepareDocumentForm(document=None, data=data)
    new_document_form.is_valid()
    new_document_form.save()
    assert Document.objects.all().count() == 2


@pytest.mark.django_db
def test_question_form():

    question = Question.add_root(
        **get_question()
    )
    initial = {'question': question.id}

    question.field_type = question.MULTIPLE_OPTIONS
    question.save()
    assert 'option' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['option'].widget.input_type == 'checkbox'

    question.field_type = question.SINGLE_OPTION
    question.save()
    assert 'option' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['option'].widget.input_type == 'radio'

    question.field_type = question.YES_NO
    question.save()
    assert 'option' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['option'].widget.input_type == 'radio'

    question.field_type = question.SINGLE_LINE
    question.save()
    assert 'text' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['text'].widget.input_type == 'text'

    question.field_type = question.TEXT
    question.save()
    assert 'text' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['text'].widget.__class__.__name__ == 'Textarea'

    question.field_type = question.DATE
    question.save()
    assert 'date' in QuestionForm(initial=initial).fields
    assert QuestionForm(initial=initial).fields['date'].widget.input_type == 'date'

    data = {'date': '2021-10-10', 'question': question.id}
    form = QuestionForm(initial=initial, data=data)
    form.is_valid()
    assert form.cleaned_data.get('date') == '10.10.2021'


@pytest.mark.django_db
def test_question_condition_form():
    question = Question.add_root(
        **get_single_option_question()
    )

    question2 = Question.add_root(
        **get_single_option_question()
    )

    Condition.objects.create(
        question=question,
        if_option='is',
        if_value='yes',
        then_value='success'
    )

    con = Condition.objects.create(
        question=question,
        if_option='is',
        if_value='no',
        then_value='failure'
    )

    form = QuestionConditionForm(instance=question)
    assert 'conditions' in form.fields
    assert question.conditions.count() == 2

    conditions = [
        {'question': [],
         'id': con.id,
         'if_option': 'is',
         'if_value': 'no',
         'then_value': 'failure'}
    ]

    data = {"conditions": json.dumps(conditions)}

    form = QuestionConditionForm(instance=question, data=data)
    form.is_valid()
    form.save()
    assert question.conditions.count() == 1

    conditions = [
        {'question': [],
         'id': con.id,
         'if_option': 'is',
         'if_value': 'no',
         'then_value': 'question',
         'then_question': question2.id}
    ]

    data = {"conditions": json.dumps(conditions)}

    form = QuestionConditionForm(instance=question, data=data)
    form.is_valid()
    form.save()
    assert question.conditions.count() == 1
    assert Condition.objects.all().first().then_question == question2

    conditions = [
        {'question': [],
         'id': con.id,
         'if_option': 'is',
         'if_value': 'no',
         'then_value': 'success',
         'then_question': question2.id
         }
    ]

    data = {"conditions": json.dumps(conditions)}

    form = QuestionConditionForm(instance=question, data=data)
    form.is_valid()
    form.save()
    assert question.conditions.count() == 1
    assert Condition.objects.all().first().then_question is None


@pytest.mark.django_db
def test_question_update_form():

    question = Question.add_root(
        **get_text_question()
    )
    assert 'options' not in QuestionUpdateForm(instance=question).fields
    assert QuestionUpdateForm(instance=question).fields['text'].widget.attrs == {'class': 'form-control'}

    question_2 = Question.add_root(
        **get_single_option_question()
    )

    Condition.objects.create(
        question=question_2,
        if_option='is',
        if_value='yes',
        then_value='success'
    )

    Condition.objects.create(
        question=question_2,
        if_option='is',
        if_value='no',
        then_value='failure'
    )

    assert question_2.conditions.count() == 2

    data = {
        'text': question_2.text,
        'field_type': question_2.field_type,
        'information': 'Information',
        'options': json.dumps({'options_1': 'option 1', 'options_2': 'option 2'})

    }

    assert 'options' in QuestionUpdateForm(instance=question_2).fields
    assert QuestionUpdateForm(instance=question_2).fields['options'].widget.attrs == {}
    form = QuestionUpdateForm(instance=question_2, data=data)

    form.is_valid()
    form.save()
    assert question_2.conditions.count() == 0


@pytest.mark.django_db
def test_question_createForm_form():

    question = Question.add_root(
        **get_text_question()
    )

    assert QuestionCreateForm(parent_question=question).fields['parent_question'].initial == question
    assert QuestionCreateForm().fields['parent_question'].initial is None
