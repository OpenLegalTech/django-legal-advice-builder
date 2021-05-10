import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Question
from legal_advice_builder.views import FormWizardView

from .helpers import get_single_option_question
from .helpers import get_text_question


@pytest.mark.django_db
def test_form_wizard_returns_first_question_form(rf, law_case_factory, questionaire_factory):

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
    middleware = SessionMiddleware()
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
           questionaire=qn_1,
           parent_option='yes')))

    request = rf.get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()

    data = {
        'question': q1.id,
        'option': 'yes'
    }

    request = rf.get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)

    praefix = 'legal_advice_builder_{}'.format(law_case.id)
    request = rf.post('/', data)
    middleware = SessionMiddleware()
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
           questionaire=qn_1,
           parent_option='yes')))

    q2.failure_conditions = [{'options': ['no']}]
    q2.save()

    request = rf.get('/')
    middleware = SessionMiddleware()
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
    middleware = SessionMiddleware()
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
    middleware = SessionMiddleware()
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
                    'q1': 'test test'
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
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)

    assert response.context_data.get('form').initial == {'text': 'test test'}
