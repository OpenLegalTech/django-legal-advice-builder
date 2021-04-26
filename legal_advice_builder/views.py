import weasyprint as wp
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from .forms import WizardForm
from .models import Answer, Question
from .storage import SessionStorage


class FormWizardView(TemplateView):
    template_name = 'legal_advice_builder/form_wizard.html'
    form_class = WizardForm

    def dispatch(self, request, *args, **kwargs):
        self.prefix = self.get_prefix()
        self.storage = SessionStorage(
            self.prefix, request
        )
        self.initial_dict = self.get_initial_dict()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.storage.reset()
        questionaire = self.get_lawcase().get_first_questionaire()
        question = questionaire.get_first_question()
        self.storage.set_data({
            'current_questionaire': questionaire.id,
            'current_question': question.id,
            'answers': []
        })
        initial_data = self.get_initial_data(question)
        form = self.get_form(question=question, initial_data=initial_data)
        return self.render_form(form)

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

    def post(self, *args, **kwargs):
        answers = self.storage.get_data().get('answers')
        question = self.get_current_question()

        if self.request.POST.get('next'):
            next_question = Question.objects.get(id=self.request.POST.get('next'))
            self.storage.set_data({
                'current_questionaire': next_question.questionaire.id,
                'current_question': next_question.id,
                'answers': answers
            })
            initial_data = self.get_initial_data(next_question)
            form = self.get_form(question=next_question, initial_data=initial_data)
            return self.render_form(form)

        question_form = self.get_form(question=question, data=self.request.POST)
        if question_form.is_valid():
            cleaned_data = question_form.cleaned_data
            option = cleaned_data.get('option')
            text = cleaned_data.get('text')
            answers = answers + [cleaned_data]
            next_question = question.next(option=option, text=text)
            if question.is_success(option=option, text=text):
                message = question.get_success_message()
                return self.render_success(message, next_question)
            if question.is_failure(option=option, text=text):
                message = question.get_failure_message()
                return self.render_failure(message)
            elif question.is_unsure(option=option, text=text):
                message = question.get_unsure_message()
                return self.render_failure(message)
            elif next_question:
                self.storage.set_data({
                    'current_questionaire': next_question.questionaire.id,
                    'current_question': next_question.id,
                    'answers': answers
                })
                initial_data = self.get_initial_data(next_question)
                form = self.get_form(question=next_question, initial_data=initial_data)
                return self.render_form(form)
            else:
                return self.render_done(answers)
        else:
            return self.render_form(question_form)

    def get_lawcase(self):
        raise NotImplementedError

    def get_prefix(self):
        return 'legal_advice_builder_{}'.format(self.get_lawcase().id)

    def get_form_kwargs(self, question=None, data=None, initial=None):
        return {
            'question': question,
            'data': data,
            'initial': initial
        }

    def get_form_class(self):
        return self.form_class

    def get_initial_dict(self):
        return {}

    def get_form(self, question=None, data=None, initial_data=None):
        form_class = self.get_form_class()
        form_kwargs = self.get_form_kwargs(question=question,
                                           data=data,
                                           initial=initial_data)
        return form_class(**form_kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'law_case': self.get_lawcase(),
            'question': self.get_current_question()
        })
        return context

    def render_form(self, form=None, **kwargs):
        form = form or self.get_form()
        context = self.get_context_data(form=form, **kwargs)
        return self.render_to_response(context)

    def render_failure(self, message=None, **kwargs):
        context = self.get_context_data(failure=True,
                                        failure_message=message,
                                        **kwargs)
        return self.render_to_response(context)

    def render_success(self, message=None, next=None, **kwargs):
        context = self.get_context_data(success=True,
                                        next=next,
                                        success_message=message, **kwargs)
        return self.render_to_response(context)

    def save_answers(self, answers):
        answer = Answer.objects.create(
            law_case=self.get_lawcase(),
            answers=answers
        )
        if self.request.user.is_authenticated:
            answer.creator = self.request.user
            answer.save()
        return answer

    def render_done(self, answers=None, **kwargs):
        answer = self.save_answers(answers)
        context = self.get_context_data(answer=answer, **kwargs)
        return self.render_to_response(context)


class PdfDownloadView(TemplateView):

    model = Answer
    template_name = 'law_advice_builder/pdf_download.html'

    def get_answer(self):
        raise NotImplementedError

    def get_pdf_bytes(self):
        html = self.get_html_string()
        doc = wp.HTML(string=html)
        return doc.write_pdf()

    def get_html_string(self):
        ctx = self.get_context_data()
        ctx.update({
            'answer': self.get_answer()
        })
        return render_to_string(self.template_name, ctx)

    def get(self, request, *args, **kwargs):
        self.object = self.get_answer()
        response = HttpResponse(
            self.get_pdf_bytes(),
            content_type='application/pdf'
        )
        filename = 'download.pdf'
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
        return response
