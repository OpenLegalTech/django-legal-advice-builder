from html.parser import HTMLParser
import json

from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import response

import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from legal_advice_builder.models import Answer
from legal_advice_builder.models import Condition
from legal_advice_builder.models import Document
from legal_advice_builder.models import DocumentField
from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Question
from legal_advice_builder.models import Questionaire
from legal_advice_builder.views import DocumentFormView
from legal_advice_builder.views import DocumentPreviewView
from legal_advice_builder.views import FormWizardView
from legal_advice_builder.views import PdfDownloadView
from legal_advice_builder.views import QuestionDelete
from legal_advice_builder.views import QuestionUpdate
from legal_advice_builder.views import QuestionaireDetail
from legal_advice_builder.views import LawCaseList
from legal_advice_builder.views import LawCasePreview
from legal_advice_builder.views import LawCaseEdit
from legal_advice_builder.views import LawCaseDelete

from .helpers import get_single_option_question
from .helpers import get_text_question


def dummy_get_response(request):
    return None


@pytest.mark.django_db
def test_form_wizard_returns_first_question_form(
        rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)
    assert 'legal_advice_builder/form_wizard.html' in response.template_name
    assert response.context_data.get('form').fields['question'].initial == q1.id
    dict_as_choices = [(k, v) for k, v in q1.options.items()]
    assert response.context_data.get('form').fields['option'].choices == dict_as_choices

    praefix = 'legal_advice_builder_{}'.format(law_case.id)

    assert response._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert response._request.session.get(praefix).get('current_question') == q1.id
    assert response._request.session.get(praefix).get('answers') == []


@pytest.mark.django_db
def test_form_wizard_return_next_question_by_option(rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))
    q2 = q1.add_child(
        **(get_single_option_question(
           questionaire=qn_1)))

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()

    data = {
        'question': q1.id,
        'option': 'yes'
    }

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)

    praefix = 'legal_advice_builder_{}'.format(law_case.id)
    request = rf.post('/', data)
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    session_data = response._request.session.get(praefix)
    request.session[praefix] = session_data
    response = TestWizardView.as_view()(request)

    assert response.context_data.get('form').fields['question'].initial == q2.id
    assert response._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert response._request.session.get(praefix).get('current_question') == q2.id
    assert response._request.session.get(praefix).get('answers') == [{
        'option': 'yes', 'question': '1'
    }]

    session_data = response._request.session.get(praefix)


@pytest.mark.django_db
def test_form_wizard_returns_failure_by_option(rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))
    q2 = q1.add_child(
        **(get_single_option_question(
           questionaire=qn_1)))

    Condition.objects.create(
        question=q2,
        if_option='is',
        if_value='no',
        then_value='failure'
    )

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)
    assert 'legal_advice_builder/form_wizard.html' in response.template_name
    assert response.context_data.get('form').fields['question'].initial == q1.id
    dict_as_choices = [(k, v) for k, v in q1.options.items()]
    assert response.context_data.get('form').fields['option'].choices == dict_as_choices

    praefix = 'legal_advice_builder_{}'.format(law_case.id)

    session_data = response._request.session.get(praefix)
    assert response._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert response._request.session.get(praefix).get('current_question') == q1.id
    assert response._request.session.get(praefix).get('answers') == []

    data = {
        'question': q1.id,
        'option': 'yes'
    }

    request = rf.post('/', data)
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    request.session[praefix] = session_data
    response = TestWizardView.as_view()(request)

    assert 'legal_advice_builder/form_wizard.html' in response.template_name
    assert response.context_data.get('form').fields['question'].initial == q2.id
    assert response._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert response._request.session.get(praefix).get('current_question') == q2.id
    assert response._request.session.get(praefix).get('answers') == [{
        'option': 'yes', 'question': '1'
    }]

    session_data = response._request.session.get(praefix)

    data = {
        'question': q2.id,
        'option': 'no'
    }

    request = rf.post('/', data)
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    request.session[praefix] = session_data
    response = TestWizardView.as_view()(request)

    assert 'legal_advice_builder/form_wizard.html' in response.template_name
    assert response.context_data.get('failure') is True
    assert response.context_data.get('form') is None


@pytest.mark.django_db
def test_form_wizard_initial_data(rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

        def get_initial_dict(self):
            return {
                'qn_1': {
                    'q1': {'initial': 'test test'}
                }
            }

    law_case = law_case_factory()

    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    qn_1.short_title = 'qn_1'
    qn_1.save()

    q1 = Question.add_root(
        **(get_text_question(
            questionaire=qn_1)))

    q1.short_title = 'q1'
    q1.save()

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)

    assert response.context_data.get('form').initial == {'text': 'test test'}


@pytest.mark.django_db
def test_form_wizard_initial_options(rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

        def get_initial_dict(self):
            return {
                'qn_1': {
                    'q1': {'options':
                           {'option1': 'option1',
                            'option2': 'option2'}}
                }
            }

    law_case = law_case_factory()

    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    qn_1.short_title = 'qn_1'
    qn_1.save()

    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))

    q1.short_title = 'q1'
    q1.save()

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    resp = TestWizardView.as_view()(request)
    choices = [('option1', 'option1'), ('option2', 'option2')]
    assert resp.context_data.get('form').fields['option'].choices == choices


@pytest.mark.django_db
def test_form_wizard_not_implemented_error(rf):

    class TestWizardView(FormWizardView):

        def get_initial_dict(self):
            return {
                'qn_1': {
                    'q1': {'options':
                           {'option1': 'option1',
                            'option2': 'option2'}}
                }
            }

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    with pytest.raises(Exception):
        TestWizardView.as_view()(request)


@pytest.mark.django_db
def test_document_preview_view(rf, document_type_factory, document_factory,
                               law_case_factory, document_field_type_factory,
                               document_field_factory, questionaire_factory):

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
        content='<p>{{ qn_q1 }}</p>'
    )

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='<p>{{ qn_q2 }}</p>'
    )

    law_case = law_case_factory(document=document)
    qn = questionaire_factory(law_case=law_case, short_title='qn')

    q1 = Question.add_root(**get_text_question(questionaire=qn, short_title='q1'))
    q2 = q1.add_child(**get_text_question(questionaire=qn, short_title='q2'))

    document.sample_answer = [{'question': q1.id, 'text': 'test'}]
    document.save()

    request = rf.get('/')
    response = DocumentPreviewView.as_view()(request, pk=law_case.id)
    assert response.context_data.get('document') == document
    assert response.context_data.get('lawcase') == law_case
    assert len(response.context_data.get('questions_formset').forms) == 2

    data = {
        'form-TOTAL_FORMS': 2,
        'form-INITIAL_FORMS': 0,
        'form-0-question': q1.id,
        'form-0-text': 'text',
        'form-1-question': q2.id,
        'form-1-text': 'text 2'
    }

    request = rf.post('/', data)
    DocumentPreviewView.as_view()(request, pk=law_case.id)
    assert len(Document.objects.get(id=document.id).sample_answers) == 2
    assert Document.objects.get(id=document.id).sample_answers[0].get('question') == str(q1.id)
    assert Document.objects.get(id=document.id).sample_answers[0].get('text') == 'text'
    assert Document.objects.get(id=document.id).sample_answers[1].get('question') == str(q2.id)
    assert Document.objects.get(id=document.id).sample_answers[1].get('text') == 'text 2'


@pytest.mark.django_db
def test_document_form_view(rf, document_type_factory, document_factory,
                            law_case_factory, document_field_type_factory,
                            document_field_factory):

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

    df1 = document_field_factory(
        document=document,
        field_type=field_type_1,
        content='<p>{{ qn_q1 }}</p>'
    )

    document_field_factory(
        document=document,
        field_type=field_type_2,
        content='<p>{{ qn_q2 }}</p>'
    )

    law_case = law_case_factory(document=document)
    data = {
        'content': '<p>{{ qn_q1 }} test</p>',
        'document': document.id,
        'fieldtypeid': field_type_1.id
    }

    request = rf.post('/', json.dumps(data), content_type='application/json')
    DocumentFormView.as_view()(request, pk=law_case.id)
    assert DocumentField.objects.get(id=df1.id).content == '<p>{{ qn_q1 }} test</p>'

    request = rf.get('/')
    response = DocumentFormView.as_view()(request, pk=law_case.id)
    assert 'document' in response.context_data
    assert 'document_form' in response.context_data

    class TestHTMLParser(HTMLParser):

        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.reset()
            self.NEWTAGS = []
            self.NEWATTRS = []

        def handle_starttag(self, tag, attrs):
            self.NEWTAGS.append(tag)
            if attrs:
                self.NEWATTRS.append(attrs)

    parser = TestHTMLParser()
    parser.feed(response.context_data.get('document_form'))
    assert parser.NEWTAGS.count('document-field') == 2
    content = DocumentField.objects.get(id=df1.id).content
    parser_content = dict(parser.NEWATTRS[0])
    assert parser_content.get('content') == content.replace(
        '{{', '[[').replace('}}', ']]')
    assert parser_content.get('document') == str(document.id)
    assert parser_content.get('name') == field_type_1.name


@pytest.mark.django_db
def test_pdf_download_view(rf, answer_factory):

    class TestPdfDownloadWithoutAnswerView(PdfDownloadView):
        pass

    class TestPdfDownloadView(PdfDownloadView):

        def get_answer(self):
            return Answer.objects.all().first()

    request = rf.get('/')
    with pytest.raises(Exception):
        TestPdfDownloadWithoutAnswerView.as_view()(request)

    answer_factory()
    pdf_response = TestPdfDownloadView.as_view()(request)
    assert pdf_response['content-type'] == 'application/pdf'


@pytest.mark.django_db
def test_law_case_list_view(rf, law_case_factory, document_type_factory):
    law_case_factory()
    law_case_factory()

    dt = document_type_factory()

    request = rf.get('/')
    view_response = LawCaseList.as_view()(request)
    assert len(view_response.context_data.get('update_forms')) == 2

    LawCase.objects.all().count() == 2

    data = {
        'document_type': dt.id,
        'title': 'New Lawcase'
    }

    request = rf.post('/', data)
    LawCaseList.as_view()(request)
    LawCase.objects.all().count() == 3


@pytest.mark.django_db
def test_law_case_preview_view(rf, law_case_factory, questionaire_factory):
    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()

    request = rf.get('/')
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    view_response = LawCasePreview.as_view()(request, pk=law_case.id)
    assert view_response.context_data.get('law_case') == law_case


@pytest.mark.django_db
def test_law_case_edit_view(rf, law_case_factory):
    law_case = law_case_factory()

    data = {
        'title': 'New Title'
    }

    request = rf.post('/', data)
    view_reponse = LawCaseEdit.as_view()(request, pk=law_case.id)
    assert view_reponse.status_code == 302


@pytest.mark.django_db
def test_law_case_delete_view(rf, law_case_factory):
    law_case_1 = law_case_factory()
    law_case_2 = law_case_factory()
    assert LawCase.objects.all().count() == 2
    request = rf.post('/', {})
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    view_reponse = LawCaseDelete.as_view()(request, pk=law_case_1.id)
    assert LawCase.objects.all().count() == 1
    assert view_reponse.status_code == 302

    request = rf.get('/')
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    view_reponse = LawCaseDelete.as_view()(request, pk=law_case_2.id)
    assert LawCase.objects.all().count() == 0
    assert view_reponse.status_code == 302


@pytest.mark.django_db
def test_questionaire_detail_view(rf, questionaire_factory):
    qn = questionaire_factory()

    request = rf.get('/')
    resp = QuestionaireDetail.as_view()(request, pk=qn.id)
    assert resp.context_data.get('current_step') == 0
    data = {
        'parent_question': '',
        'text': 'New Question',
        'field_type': Question.TEXT,
        'question_create': ''
    }
    Question.objects.all().count() == 0
    request = rf.post('/', data)
    QuestionaireDetail.as_view()(request, pk=qn.id)
    Question.objects.all().count() == 1

    data = {
        'title': 'New Title',
        'questionaire_update': ''
    }
    request = rf.post('/', data)
    QuestionaireDetail.as_view()(request, pk=qn.id)
    assert Questionaire.objects.get(id=qn.id).title == 'New Title'


@pytest.mark.django_db
def test_question_delete_view(rf, questionaire_factory):
    qn = questionaire_factory()
    q1 = Question.add_root(
        **get_text_question(questionaire=qn)
    )
    q2 = q1.add_child(**get_text_question(questionaire=qn))
    q3 = q2.add_child(**get_text_question(questionaire=qn))

    assert Question.objects.all().count() == 3

    request = rf.post('/', {})
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    resp = QuestionDelete.as_view()(request, pk=q2.id)
    assert resp.status_code == 302
    assert Question.objects.all().count() == 2
    assert q3.get_parent() == q2

    request = rf.get('/')
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    resp = QuestionDelete.as_view()(request, pk=qn.id)
    assert resp.status_code == 302


@pytest.mark.django_db
def test_question_update_view(rf, questionaire_factory):
    qn = questionaire_factory()
    q1 = Question.add_root(
        **get_single_option_question(questionaire=qn)
    )
    q2 = q1.add_child(
        **get_text_question(questionaire=qn)
    )
    conditions = [
        {'if_option': 'is',
         'if_value': 'no',
         'then_value': 'failure'}
    ]
    data = {
        'logic': '',
        'conditions': json.dumps(conditions)
    }
    assert Condition.objects.all().count() == 0
    request = rf.post('/', data)
    resp = QuestionUpdate.as_view()(request, pk=q1.id)
    assert resp.status_code == 302
    assert Condition.objects.all().count() == 1

    data = {
        'questionaire_update': '',
        'title': 'new title'
    }
    request = rf.post('/', data)
    resp = QuestionUpdate.as_view()(request, pk=q1.id)
    assert resp.status_code == 302
    assert Questionaire.objects.get(id=qn.id).title == 'new title'

    data = {
        'text': 'what is the answer?',
        'field_type': q1.field_type
    }
    request = rf.post('/', data)
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    resp = QuestionUpdate.as_view()(request, pk=q2.id)
    assert resp.status_code == 302
    assert Question.objects.get(id=q2.id).text == 'what is the answer?'

    request = rf.get('/')
    resp = QuestionUpdate.as_view()(request, pk=q2.id)
    assert resp.status_code == 200
    assert resp.context_data.get('questionaire') == qn
