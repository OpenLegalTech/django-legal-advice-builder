import json

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.forms import formset_factory
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic import ListView
from django.views.generic import TemplateView
from django.views.generic import UpdateView

from .forms import DocumentForm
from .forms import LawCaseCreateForm
from .forms import LawCaseUpdateForm
from .forms import PrepareDocumentForm
from .forms import QuestionaireCreateForm
from .forms import QuestionaireForm
from .forms import QuestionConditionForm
from .forms import QuestionCreateForm
from .forms import QuestionForm
from .forms import QuestionUpdateForm
from .models import Document
from .models import LawCase
from .models import Question
from .models import Questionaire
from .models import TextBlock
from .models import TextBlockCondition
from .views import FormWizardView

try:
    PermissionMixin = import_string(
        settings.LEGAL_ADVICE_BUILDER_PERMISSION_MIXIN)
except (AttributeError):
    from .permissions import DefaultAccessToAdminMixin as PermissionMixin


class LawCaseList(PermissionMixin, ListView, FormView):
    template_name = 'legal_advice_builder/admin/law_case_list.html'
    form_class = LawCaseCreateForm

    model = LawCase

    def form_valid(self, form):
        document = None
        title = form.cleaned_data.get('title')
        description = form.cleaned_data.get('description')
        law_case = LawCase.objects.create(
            title=title,
            document=document,
            description=description
        )
        if self.request.user.is_authenticated:
            law_case.creator = self.request.user
            law_case.save()
        law_case.generate_default_questionaires()
        return HttpResponseRedirect(reverse(
            'legal_advice_builder:questionaire-detail',
                                    args=[law_case.get_first_questionaire().id]))

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


class LawCaseEdit(PermissionMixin, UpdateView):
    model = LawCase
    form_class = LawCaseUpdateForm

    def get_success_url(self):
        return reverse('legal_advice_builder:law-case-list')


class LawCaseDelete(PermissionMixin, DeleteView):
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


class LawCasePreview(PermissionMixin, FormWizardView):
    template_name = 'legal_advice_builder/admin/form_wizard_preview.html'

    def get_lawcase(self):
        lawcase_id = self.kwargs.get('pk')
        return LawCase.objects.get(id=lawcase_id)


class DocumentCreateView(PermissionMixin, CreateView):
    model = Document
    form_class = DocumentForm

    def dispatch(self, request, *args, **kwargs):
        self.law_case = self.get_law_case()
        return super().dispatch(request, *args, **kwargs)

    def get_law_case(self):
        if 'pk' in self.kwargs:
            pk = self.kwargs.get('pk')
            return LawCase.objects.get(pk=pk)

    def form_valid(self, form):
        self.object = form.save()
        self.law_case.document = self.object
        self.law_case.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('legal_advice_builder:document-detail',
                       args=[self.law_case.id])


class DocumentPreviewView(PermissionMixin, TemplateView):
    template_name = 'legal_advice_builder/admin/document_preview.html'

    def dispatch(self, request, *args, **kwargs):
        self.document = self.get_document()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'document': self.document,
            'questions_formset': self.get_questions_formset(),
            'lawcase': self.document.lawcase,
            'questionaire_form': QuestionaireCreateForm()
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


class DocumentFormView(PermissionMixin, TemplateView):
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
        textblock = data.get('textblock')
        document = self.document
        question = data.get('question')
        if_value = data.get('if_value')

        if not textblock:
            textblock = TextBlock.objects.create(
                document=document,
                content=content,
                order=document.document_text_blocks.count() + 1
            )
        else:
            textblock = TextBlock.objects.get(id=textblock)
            if content:
                textblock.content = content
                textblock.save()
                textblock.text_block_conditions.all().delete()
            else:
                textblock.delete()
        if question and if_value:
            TextBlockCondition.objects.create(
                text_block=textblock,
                if_option='is',
                if_value=if_value,
                question=Question.objects.get(id=question)
            )

        return JsonResponse({'content': textblock.content, 'id': textblock.id})

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
            'questionaire_form': QuestionaireCreateForm()
        })
        return context


class QuestionaireDetail(PermissionMixin, DetailView):
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
            'lawcase': self.object.law_case,
            'document_form': DocumentForm(),
            'questionaire_form': QuestionaireCreateForm()
        })
        return context


class QuestionaireCreate(PermissionMixin, CreateView):
    model = Questionaire
    form_class = QuestionaireCreateForm

    def get_success_url(self):
        return reverse('legal_advice_builder:questionaire-detail',
                       args=[self.object.id])

    def get_object(self):
        pk = self.kwargs.get(self.pk_url_kwarg)
        return LawCase.objects.get(id=pk)

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.law_case = self.get_object()
        self.object.order = self.get_object().questionaire_count()
        self.object.save()
        return super().form_valid(form)


class QuestionaireDeleteView(PermissionMixin, DeleteView):
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


class QuestionDelete(PermissionMixin, DeleteView):
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


class QuestionUpdate(PermissionMixin, SuccessMessageMixin, UpdateView):
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
            'document_form': DocumentForm(),
            'questionaire_form': QuestionaireCreateForm()
        })
        return context
