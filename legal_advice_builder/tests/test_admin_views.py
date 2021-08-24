import json

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware

from legal_advice_builder.admin_views import DocumentFormView
from legal_advice_builder.admin_views import DocumentPreviewView
from legal_advice_builder.admin_views import LawCaseDelete
from legal_advice_builder.admin_views import LawCaseEdit
from legal_advice_builder.admin_views import LawCaseList
from legal_advice_builder.admin_views import LawCasePreview
from legal_advice_builder.admin_views import QuestionaireDeleteView
from legal_advice_builder.admin_views import QuestionaireDetail
from legal_advice_builder.admin_views import QuestionDelete
from legal_advice_builder.admin_views import QuestionUpdate
from legal_advice_builder.models import Answer
from legal_advice_builder.models import Condition
from legal_advice_builder.models import Document
from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Question
from legal_advice_builder.models import Questionaire
from legal_advice_builder.models import TextBlock
from legal_advice_builder.views import PdfDownloadView

from .helpers import get_single_option_question
from .helpers import get_text_question


def dummy_get_response(request):
    return None


@pytest.mark.django_db
def test_document_preview_view(rf, document_factory, law_case_factory,
                               text_block_factory, questionaire_factory):

    document = document_factory()

    text_block_factory(
        document=document,
        content='<p>{{ qn_q1 }}</p>'
    )

    text_block_factory(
        document=document,
        content='<p>{{ qn_q2 }}</p>'
    )

    law_case = law_case_factory(document=document)
    qn = questionaire_factory(law_case=law_case, short_title='qn')

    q1 = Question.add_root(**get_text_question(questionaire=qn, short_title='q1'))
    q2 = q1.add_child(**get_text_question(questionaire=qn, short_title='q2'))

    document.sample_answer = [{'question': q1.id, 'text': 'test'}]
    document.save()

    request = rf.get('/')
    resp = DocumentPreviewView.as_view()(request, pk=law_case.id)
    assert resp.context_data.get('document') == document
    assert resp.context_data.get('lawcase') == law_case
    assert len(resp.context_data.get('questions_formset').forms) == 2

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
def test_document_form_view(rf, document_factory,
                            law_case_factory, text_block_factory):

    document = document_factory()

    tb1 = text_block_factory(
        document=document,
        content='<p>{{ qn_q1 }}</p>'
    )

    text_block_factory(
        document=document,
        content='<p>{{ qn_q2 }}</p>'
    )

    law_case = law_case_factory(document=document)
    data = {
        'content': '<p>{{ qn_q1 }} test</p>',
        'document': document.id,
        'textblock': tb1.id
    }

    request = rf.post('/', json.dumps(data), content_type='application/json')
    DocumentFormView.as_view()(request, pk=law_case.id)
    assert TextBlock.objects.get(id=tb1.id).content == '<p>{{ qn_q1 }} test</p>'

    request = rf.get('/')
    response = DocumentFormView.as_view()(request, pk=law_case.id)
    assert 'document' in response.context_data


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
def test_law_case_list_view(rf, law_case_factory):
    law_case_factory()
    law_case_factory()

    request = rf.get('/')
    view_response = LawCaseList.as_view()(request)
    assert len(view_response.context_data.get('update_forms')) == 2

    LawCase.objects.all().count() == 2

    data = {
        'title': 'New Lawcase'
    }

    request = rf.post('/', data)
    request.user = AnonymousUser()
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
    qn = questionaire_factory(order=0)
    questionaire_factory(order=1, law_case=qn.law_case)

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
    questionaire_factory(law_case=qn.law_case)
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


@pytest.mark.django_db
def test_questionaire_delete_view(rf, questionaire_factory,
                                  law_case_factory):
    lc = law_case_factory()
    qn = questionaire_factory(
        law_case=lc,
        order=1
    )
    questionaire_factory(
        law_case=lc,
        order=2
    )
    questionaire_factory(
        law_case=lc,
        order=3
    )

    assert Questionaire.objects.all().count() == 3

    request = rf.post('/', {})
    setattr(request, 'session', 'session')
    messages = FallbackStorage(request)
    setattr(request, '_messages', messages)
    resp = QuestionaireDeleteView.as_view()(request, pk=qn.id)
    assert resp.status_code == 302
    assert Questionaire.objects.all().count() == 2
