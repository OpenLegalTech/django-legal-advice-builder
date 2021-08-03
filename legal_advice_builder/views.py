import json

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.template import Context
from django.template import Template
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from .forms import LawCaseCreateForm
from .forms import LawCaseUpdateForm
from .forms import PrepareDocumentForm
from .forms import QuestionaireForm
from .forms import QuestionConditionForm
from .forms import QuestionCreateForm
from .forms import QuestionForm
from .forms import QuestionUpdateForm
from .forms import RenderedDocumentForm
from .forms import WizardForm
from .mixins import GenerateEditableDocumentMixin
from .mixins import GeneratePDFDownloadMixin
from .mixins import GenrateFormWizardMixin
from .models import Answer
from .models import Document
from .models import DocumentField
from .models import DocumentFieldType
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
                return self.render_download_response(
                    answers, answer=self.answer)
            else:
                return HttpResponseNotAllowed(['POST'])

        elif self.answer:
            return self.render_document_form(
                self.request.POST, self.answer, **kwargs)

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
    template_name = 'legal_advice_builder/admin/document_preview.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document': self.document,
            'questions_formset': self.get_questions_formset(),
            'lawcase': self.document.lawcase
        })
        return context

    def get_document(self):
        if 'pk' in self.kwargs:
            pk = self.kwargs.get('pk')
            return LawCase.objects.get(pk=pk).document

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
    template_name = 'legal_advice_builder/admin/document_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        return super().dispatch(request, *args, **kwargs)

    def get_document(self):
        if 'pk' in self.kwargs:
            pk = self.kwargs.get('pk')
            return LawCase.objects.get(pk=pk).document

    def post(self, *args, **kwargs):
        data = json.loads(self.request.body)
        content = data.get('content')
        document = data.get('document')
        field_type_id = data.get('fieldtypeid')

        document = self.document
        field_type = DocumentFieldType.objects.get(id=field_type_id)

        field, created = DocumentField.objects.get_or_create(
            field_type=field_type,
            document=document
        )
        field.content = content
        field.save()

        return JsonResponse({'content': field.content})

    def document_fields_templates(self):
        document_fields = self.document.get_initial_fields_dict()
        res = {}
        for field in document_fields:
            key = field.get('field_slug')
            document = field.get('document')
            field_type_id = field.get('field_type')
            field_name = field.get('field_name')
            content = field.get('content').replace('{{', '[[').replace('}}', ']]')
            vue_template = Template("<document-field content='{{ content }}' name='{{ field_name }}' "
                                    "fieldtypeid='{{ field_type_id }}' document='{{ document }}'>"
                                    "</document-field>")
            context = {'content': content,
                       'document': document,
                       'field_name': field_name,
                       'field_type_id': field_type_id}
            res[key] = vue_template.render(Context(context))
        return res

    def document_fields(self):
        document_form = Template(self.get_document().document_type.document_template)
        context = self.document_fields_templates()
        return document_form.render(Context(
            context
        ))

    def get_form(self, data=None):
        return PrepareDocumentForm(document=self.document, data=data)

    def get_placeholders(self):
        if self.document:
            return self.document.lawcase.placeholders_for_template

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'form': self.get_form(),
            'placeholders': self.get_placeholders(),
            'document': self.document,
            'lawcase': self.document.lawcase,
            'document_form': self.document_fields()
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


class LawCaseList(ListView, FormView):
    template_name = 'legal_advice_builder/admin/law_case_list.html'
    form_class = LawCaseCreateForm

    model = LawCase

    def form_valid(self, form):
        document = None
        document_type = form.cleaned_data.pop('document_type')
        title = form.cleaned_data.get('title')
        description = form.cleaned_data.get('description')
        if document_type:
            document = Document.objects.create(
                document_type=document_type,
                name=title,
            )
        law_case = LawCase.objects.create(
            title=title,
            document=document,
            description=description
        )
        law_case.generate_default_questionaires()
        return HttpResponseRedirect(reverse(
            'legal_advice_builder:questionaire-detail',
                                    args=[law_case.first_questionaire.id]))

    def get_update_forms(self):
        update_forms = []
        for law_case in self.get_queryset():
            update_forms.append(
                (law_case.id, LawCaseUpdateForm(instance=law_case))
            )
        return update_forms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'update_forms': self.get_update_forms()
        })
        return context


class LawCasePreview(FormWizardView):
    template_name = 'legal_advice_builder/admin/form_wizard_preview.html'

    def get_lawcase(self):
        lawcase_id = self.kwargs.get('pk')
        return LawCase.objects.get(id=lawcase_id)


class LawCaseEdit(UpdateView):
    model = LawCase
    form_class = LawCaseUpdateForm

    def get_success_url(self):
        return reverse('legal_advice_builder:law-case-list')


class LawCaseDelete(DeleteView):
    model = LawCase
    success_message = _('Lawcase "%(title)s" was removed successfully')

    def get_success_url(self):
        return reverse('legal_advice_builder:law-case-list')

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, self.success_message % obj.__dict__)
        return super().delete(request, *args, **kwargs)


class QuestionaireDetail(DetailView):
    template_name = 'legal_advice_builder/admin/questionaire_detail.html'
    model = Questionaire

    def post(self, *args, **kwargs):
        if 'question_create' in self.request.POST:
            form = QuestionCreateForm(data=self.request.POST)
            if form.is_valid():
                data = form.cleaned_data
                parent_question = data.pop('parent_question')
                questionaire = self.get_object()
                data['questionaire'] = questionaire
                new_question = questionaire.add_new_after_question(
                    data, parent_question=parent_question)
                return HttpResponseRedirect(reverse(
                    'legal_advice_builder:question-update',
                    args=[new_question.id]))
        elif 'questionaire_update' in self.request.POST:
            form = QuestionaireForm(instance=self.get_object(),
                                    data=self.request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse(
                    'legal_advice_builder:questionaire-detail',
                    args=[self.get_object().id]))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        question = self.get_object().get_last_question()
        context.update({
            'current_step': self.object.law_case.get_index_of_questionaire(self.object),
            'question_create_form': QuestionCreateForm(
                parent_question=question.id if question else None),
            'questionaire_update_form': QuestionaireForm(instance=self.get_object()),
            'lawcase': self.object.law_case
        })
        return context


class QuestionaireDeleteView(DeleteView):
    model = Questionaire
    success_message = _('Questionaire {} was removed successfully')

    def get_success_url(self):
        qn = self.get_object().law_case.questionaire_set.exclude(id=self.get_object().id).first()
        return reverse('legal_advice_builder:questionaire-detail',
                       args=[qn.id])

    def delete(self, request, *args, **kwargs):
        questionaire = self.get_object()
        messages.success(self.request,
                         self.success_message.format(questionaire.title))
        return super().delete(request, *args, **kwargs)


class QuestionDelete(DeleteView):
    model = Question
    success_message = _('Question {} was removed successfully')

    def get_success_url(self):
        return reverse('legal_advice_builder:questionaire-detail',
                       args=[self.questionaire.id])

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        question = self.get_object()
        self.questionaire = question.questionaire
        question.prepare_for_delete()
        messages.success(self.request,
                         self.success_message.format(question.text))
        return super().delete(request, *args, **kwargs)


class QuestionUpdate(SuccessMessageMixin, UpdateView):
    template_name = 'legal_advice_builder/admin/question_update.html'
    model = Question
    form_class = QuestionUpdateForm
    success_message = _('Question geupdated')

    def get_success_url(self):
        return reverse(
            'legal_advice_builder:question-update',
            args=[self.get_object().id])

    def post(self, request, *args, **kwargs):
        if 'logic' in request.POST:
            condition_form = QuestionConditionForm(instance=self.get_object(),
                                                   data=request.POST)
            if condition_form.is_valid():
                self.object = condition_form.save()
                return HttpResponseRedirect(self.get_success_url())
        elif 'questionaire_update' in self.request.POST:
            form = QuestionaireForm(instance=self.get_object().questionaire,
                                    data=self.request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse(
                    'legal_advice_builder:questionaire-detail',
                    args=[self.get_object().questionaire.id]))
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        questionaire = self.object.questionaire
        context.update({
            'lawcase': questionaire.law_case,
            'questionaire': questionaire,
            'current_step': questionaire.law_case.get_index_of_questionaire(
                questionaire),
            'condition_form': QuestionConditionForm(instance=self.object),
            'question_create_form': QuestionCreateForm(
                parent_question=self.get_object().id),
            'question_preview_form': QuestionForm(
                initial={'question': self.get_object().id}),
            'questionaire_update_form': QuestionaireForm(
                instance=self.get_object().questionaire),
        })
        return context
