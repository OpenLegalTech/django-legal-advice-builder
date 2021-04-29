import pytest
from django.contrib.sessions.middleware import SessionMiddleware

from legal_advice_builder.models import LawCase, Question
from legal_advice_builder.views import FormWizardView

from .helpers import get_single_option_question, get_text_question


@pytest.mark.django_db
def test_form_wizard_view(rf, law_case_factory, questionaire_factory):

    class TestWizardView(FormWizardView):

        def get_lawcase(self):
            return LawCase.objects.all().first()

    law_case = law_case_factory()
    qn_1 = questionaire_factory(
        law_case=law_case,
        order=1
    )
    qn_2 = questionaire_factory(
        law_case=law_case,
        order=2
    )
    q1 = Question.add_root(
        **(get_single_option_question(
            questionaire=qn_1)))
    q1.success_options = ['unsure']
    q1.add_child(
        **(get_single_option_question(
            questionaire=qn_1,
            parent_option='yes')))
    q1.add_child(
        **(get_single_option_question(
            questionaire=qn_1,
            parent_option='no')))
    Question.add_root(
        **(get_text_question(
            questionaire=qn_2
        )))

    request = rf.get('/')
    middleware = SessionMiddleware()
    middleware.process_request(request)
    request.session.save()
    response = TestWizardView.as_view()(request)
    assert 'legal_advice_builder/form_wizard.html' in response.template_name
    assert response.context_data.get('form').fields['question'].initial == q1.id
    dict_as_choices = [(k, v) for k, v in q1.options.items()]
    praefix = 'legal_advice_builder_{}'.format(law_case.id)
    assert response.context_data.get('form').fields['option'].choices == dict_as_choices
    assert response._request.session.get(praefix).get('current_questionaire') == qn_1.id
    assert response._request.session.get(praefix).get('current_question') == q1.id
    assert response._request.session.get(praefix).get('answers') == []
