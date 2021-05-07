from django.http import HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from .forms import WizardForm
from .mixins import GeneratePDFDownloadMixin
from .models import Question
from .storage import SessionStorage


class FormWizardView(TemplateView, GeneratePDFDownloadMixin):
    template_name = 'legal_advice_builder/form_wizard.html'
    form_class = WizardForm

    def dispatch(self, request, *args, **kwargs):
        self.prefix = self.get_prefix()
        self.storage = SessionStorage(
            self.prefix, request
        )
        self.law_case = self.get_lawcase()
        self.initial_dict = self.get_initial_dict()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.storage.reset()
        questionaire = self.get_lawcase().get_first_questionaire()
        question = questionaire.get_first_question()
        return self.render_next(question, [])

    def post(self, *args, **kwargs):
        answers = self.storage.get_data().get('answers')
        question = self.get_current_question()

        if self.request.POST.get('download'):
            answers = self.storage.get_data().get('answers')
            if answers and self.law_case.allow_download:
                html_string = self.get_html_string(answers)
                return super().generate_pdf_download(html_string)
            return HttpResponseNotAllowed(['POST'])

        if self.request.POST.get('next'):
            next_question = Question.objects.get(
                id=self.request.POST.get('next'))
            return self.render_next(next_question, answers)

        question_form = self.get_form(question=question,
                                      data=self.request.POST)

        if question_form.is_valid():
            cleaned_data = question_form.cleaned_data

            status = question.get_status(
                option=cleaned_data.get('option'),
                text=cleaned_data.get('text'),
                date=cleaned_data.get('date'))
            next_question = status.get('next')

            date = cleaned_data.get('date')
            if date:
                cleaned_data['date'] = str(date)
            answers = answers + [cleaned_data]

            if not status.get('ongoing'):
                return self.render_status(**status)
            elif next_question:
                return self.render_next(next_question, answers)
            else:
                return self.render_done(answers)
        else:
            return self.render_form(question_form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'law_case': self.get_lawcase(),
            'question': self.get_current_question()
        })
        return context

    def get_initial_data(self, question):
        questionaire = question.questionaire
        if questionaire.short_title and question.short_title:
            questionaire_dict = self.initial_dict.get(questionaire.short_title)
            if questionaire_dict:
                question_data = questionaire_dict.get(question.short_title)
                text_types = [question.TEXT, question.SINGLE_LINE]
                if question.field_type in text_types:
                    return {'text': question_data}
                elif question.field_type == question.SINGLE_OPTION:
                    return {'option': question_data}

    def get_current_question(self):
        question_id = self.storage.get_data().get('current_question')
        return Question.objects.get(id=question_id)

    def get_lawcase(self):
        raise NotImplementedError

    def get_prefix(self):
        return 'legal_advice_builder_{}'.format(self.get_lawcase().id)

    def get_initial_dict(self):
        return {}

    def get_form(self, question=None, data=None, initial_data=None):
        form_class = self.form_class
        form_kwargs = {
            'question': question,
            'data': data,
            'initial': initial_data
        }
        return form_class(**form_kwargs)

    def render_form(self, form=None, **kwargs):
        form = form or self.get_form()
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def render_status(self, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def render_next(self, question, answers):
        self.storage.set_data({
            'current_questionaire': question.questionaire.id,
            'current_question': question.id,
            'answers': answers
        })
        initial_data = self.get_initial_data(question)
        form = self.get_form(question=question, initial_data=initial_data)
        return self.render_form(form)

    def get_html_string(self, answers):
        context = self.get_template_with_context(answers)
        return render_to_string(self.template_name, context)

    def get_template_with_context(self, answers, **kwargs):
        template = self.get_lawcase().get_rendered_template(answers)
        return self.get_context_data(template=template, **kwargs)

    def render_done(self, answers=None, **kwargs):
        context = self.get_template_with_context(answers)
        return self.render_to_response(context)

    def render_download(self, answers=None, **kwargs):
        context = self.get_template_with_context(answers)
        return self.render_to_response(context)


class PdfDownloadView(TemplateView, GeneratePDFDownloadMixin):

    template_name = 'legal_advice_builder/pdf_download.html'

    def get_answer(self):
        raise NotImplementedError

    def get_html_string(self):
        ctx = self.get_context_data()
        ctx.update({
            'answer': self.get_answer()
        })
        return render_to_string(self.template_name, ctx)

    def get(self, request, *args, **kwargs):
        html_string = self.get_html_string()
        return self.generate_pdf_download(self, html_string)
