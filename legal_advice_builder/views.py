from django.forms import formset_factory
from django.http import HttpResponseNotAllowed
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from .forms import DocumentFieldForm
from .forms import PrepareDocumentForm
from .forms import QuestionForm
from .forms import QuestionUpdateForm
from .forms import RenderedDocumentForm
from .forms import WizardForm
from .mixins import GenerateEditableDocumentMixin
from .mixins import GeneratePDFDownloadMixin
from .mixins import GenrateFormWizardMixin
from .models import Answer
from .models import LawCase
from .models import Question
from .models import Questionaire
from .storage import SessionStorage


class FormWizardView(TemplateView,
                     GenrateFormWizardMixin,
                     GenerateEditableDocumentMixin,
                     GeneratePDFDownloadMixin):
    template_name = 'legal_advice_builder/form_wizard.html'
    download_template_name = 'legal_advice_builder/pdf_download.html'
    wizard_form_class = WizardForm
    document_form_class = RenderedDocumentForm

    def get_lawcase(self):
        raise NotImplementedError

    def get_prefix(self):
        return 'legal_advice_builder_{}'.format(self.get_lawcase().id)

    def dispatch(self, request, *args, **kwargs):
        self.prefix = self.get_prefix()
        self.storage = SessionStorage(
            self.prefix, request
        )
        self.law_case = self.get_lawcase()
        self.allow_download = self.law_case.allow_download
        self.save_answers_enabled = self.law_case.save_answers
        self.initial_dict = self.get_initial_dict()
        self.answer = None
        if request.POST.get('answer_id'):
            self.answer = Answer.objects.get(id=request.POST.get('answer_id'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.storage.reset()
        questionaire = self.get_lawcase().get_first_questionaire()
        question = questionaire.get_first_question()
        return self.render_next(question, [])

    def post(self, *args, **kwargs):
        answers = self.storage.get_data().get('answers')
        question = self.get_current_question()
        download = self.request.POST.get('download')
        next_question = self.request.POST.get('next')

        if next_question:
            next_question = Question.objects.get(id=next_question)
            return self.render_next(next_question, answers)

        elif download:
            if self.allow_download:
                if self.answer:
                    self.save_document_form(self.request.POST, self.answer)
                return self.render_download_response(answers, answer=self.answer)
            else:
                return HttpResponseNotAllowed(['POST'])

        elif self.answer:
            return self.render_document_form(self.request.POST, self.answer, **kwargs)

        else:
            return self.validate_form_and_get_next(question=question,
                                                   answers=answers,
                                                   data=self.request.POST)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'allow_download': self.allow_download,
            'save_answers_enabled': self.save_answers,
            'law_case': self.get_lawcase(),
            'question': self.get_current_question(),
            'current_step': self.law_case.get_index_of_questionaire(
                self.get_current_question().questionaire),
            'step_count': self.law_case.questionaire_count()
        })
        return context


class DocumentPreviewView(TemplateView):
    template_name = 'legal_advice_builder/document_preview.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document': self.document,
            'questions_formset': self.get_questions_formset()
        })
        return context

    def get_document(self):
        return

    def get_questions_formset(self, data=None):
        if self.document:
            QuestionFormset = formset_factory(QuestionForm, extra=0)
            formset = QuestionFormset(data=data,
                                      initial=self.document.get_initial_questions_dict())
            return formset

    def post(self, *args, **kwargs):
        data = self.request.POST
        question_form_set = self.get_questions_formset(data=data)
        if question_form_set and question_form_set.is_valid():
            self.document.sample_answers = question_form_set.cleaned_data
            self.document.save()
        context = self.get_context_data()
        return self.render_to_response(context)


class DocumentFormView(TemplateView):
    template_name = 'legal_advice_builder/document_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        return super().dispatch(request, *args, **kwargs)

    def get_document(self):
        return

    def post(self, *args, **kwargs):
        data = self.request.POST
        document_form = self.get_form(data=data)
        document_form_set = self.get_document_field_formset(data=data)
        if document_form.is_valid():
            self.document = document_form.save()
        if document_form_set and document_form_set.is_valid():
            for form in document_form_set:
                form.save()
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_document_field_formset(self, data=None):
        if self.document:
            DocumentFieldFormset = formset_factory(DocumentFieldForm, extra=0)
            formset = DocumentFieldFormset(data=data,
                                           initial=self.document.get_initial_fields_dict())
            return formset

    def get_questions_formset(self, data=None):
        if self.document:
            QuestionFormset = formset_factory(QuestionForm, extra=0)
            formset = QuestionFormset(data=data,
                                      initial=self.document.get_initial_questions_dict())
            return formset

    def get_form(self, data=None):
        return PrepareDocumentForm(document=self.document, data=data)

    def get_variables(self):
        if self.document:
            return self.document.lawcase.variables_for_template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': self.get_form(),
            'document_field_formset': self.get_document_field_formset(),
            'variables': self.get_variables(),
            'document': self.document
        })
        return context


class PdfDownloadView(TemplateView, GeneratePDFDownloadMixin):

    template_name = 'legal_advice_builder/pdf_download.html'
    download_template_name = 'legal_advice_builder/pdf_download.html'

    def get_answer(self):
        raise NotImplementedError

    def get_html_string(self):
        ctx = self.get_context_data()
        ctx.update({
            'answer': self.get_answer().rendered_document
        })
        return render_to_string(self.download_template_name, ctx)

    def get(self, request, *args, **kwargs):
        html_string = self.get_html_string()
        return self.generate_pdf_download(html_string)


class LawCaseList(ListView):
    template_name = 'legal_advice_builder/admin/law_case_list.html'

    model = LawCase


class LawCaseDetail(DetailView):
    template_name = 'legal_advice_builder/admin/law_case_detail.html'

    model = LawCase


class QuestionaireDetail(DetailView):
    template_name = 'legal_advice_builder/admin/questionaire_detail.html'

    model = Questionaire

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'lawcase': self.object.law_case
        })
        return context


class QuestionUpdate(UpdateView):
    template_name = 'legal_advice_builder/admin/question_update.html'
    model = Question
    form_class = QuestionUpdateForm

    def get_success_url(self):
        return reverse('legal_advice_builder:question-update', args=[self.object.id])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'lawcase': self.object.questionaire.law_case,
            'questionaire': self.object.questionaire
        })
        return context
