import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from legal_advice_builder.models import Condition

from legal_advice_builder.models import LawCase
from legal_advice_builder.models import Question
from legal_advice_builder.views import FormWizardView

from .helpers import get_single_option_question
from .helpers import get_question


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
def test_form_wizard_return_next_question_by_option(rf, law_case_factory,
                                                    questionaire_factory):

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
    resp = TestWizardView.as_view()(request)

    praefix = 'legal_advice_builder_{}'.format(law_case.id)
    request = rf.post('/', data)
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    request.session.save()
    session_data = resp._request.session.get(praefix)
    request.session[praefix] = session_data
    resp = TestWizardView.as_view()(request)

    assert resp.context_data.get('form').fields['question'].initial == q2.id
    assert resp._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert resp._request.session.get(praefix).get('current_question') == q2.id
    assert resp._request.session.get(praefix).get('answers') == [{
        'option': 'yes', 'question': '1'
    }]


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
                    'q1': {'initial': 'yes'}
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
        **(get_question(
            questionaire=qn_1)))

    q1.short_title = 'q1'
    q1.save()

    for field_type in Question.FIELD_TYPES:
        q1.field_type = field_type[0]
        q1.save()
        request = rf.get('/')
        middleware = SessionMiddleware(dummy_get_response)
        middleware.process_request(request)
        request.session.save()
        response = TestWizardView.as_view()(request)
        initial = response.context_data.get('form').initial
        assert not initial == {}
        initial_key = list(initial.keys())[0]
        assert initial_key in ['option', 'text', 'date']
        if 'option' in initial:
            assert initial.get('option') == 'yes'
        elif 'text' in initial:
            assert initial.get('text') == 'yes'
        elif 'date' in initial:
            assert initial.get('date') == 'yes'


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
def test_form_wizard_update_answwer_for_download(rf, law_case_factory,
                                                 questionaire_factory,
                                                 answer_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

    lc = law_case_factory(
        allow_download=True
    )
    qn1 = questionaire_factory(
        success_message='Success qn1',
        law_case=lc)
    qn2 = questionaire_factory(
        success_message='Success qn2',
        law_case=lc)
    q1 = Question.add_root(**get_single_option_question(
        questionaire=qn1
    ))
    q2 = q1.add_child(**get_single_option_question(
        questionaire=qn1
    ))
    Condition.objects.create(
        question=q2,
        if_option='is',
        if_value='yes',
        then_value='success'
    )
    Condition.objects.create(
        question=q2,
        if_option='is',
        if_value='no',
        then_value='failure'
    )
    q3 = Question.add_root(**get_single_option_question(
        questionaire=qn2
    ))

    answer = answer_factory()
    answers = [{'question': q1.id, 'option': 'yes'},
               {'question': q2.id, 'option': 'yes'},
               {'question': q3.id, 'option': 'yes'}
               ]
    answer.answers = answers
    answer.save()

    data = {'answer_id': answer.id, 'download': 'download'}
    request = rf.post('/', data)
    middleware = SessionMiddleware(dummy_get_response)
    middleware.process_request(request)
    praefix = 'legal_advice_builder_{}'.format(lc.id)
    request.session[praefix] = {
        'current_question': q3.id,
        'answers': answers
    }
    request.session.save()
    resp = TestWizardView.as_view()(request)
