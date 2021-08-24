import json

from django import forms
from django.forms import fields
from django.forms.models import model_to_dict
from django.utils import dateformat
from django.utils.translation import gettext_lazy as _
from tinymce.widgets import TinyMCE

from .models import Answer
from .models import Condition
from .models import Document
from .models import LawCase
from .models import Question
from .models import Questionaire
from .widgets import ChoiceWidget
from .widgets import ConditionsWidget
from .widgets import CustomCheckboxSelect
from .widgets import CustomRadioSelect


class DispatchQuestionFieldTypeMixin:

    def get_field_for_question_type(self, question, options, form_fields, required=True):
        if question.field_type in [question.SINGLE_OPTION, question.YES_NO]:
            form_fields['option'] = fields.ChoiceField(
                choices=options.items(),
                widget=CustomRadioSelect,
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.MULTIPLE_OPTIONS:
            form_fields['option'] = fields.MultipleChoiceField(
                choices=options.items(),
                widget=CustomCheckboxSelect,
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.SINGLE_LINE:
            form_fields['text'] = fields.CharField(
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.TEXT:
            form_fields['text'] = fields.CharField(
                widget=forms.Textarea(attrs={'class': 'form-control'}),
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.DATE:
            form_fields['date'] = fields.DateField(
                required=required,
                label=question.text,
                help_text=question.help_text,
                widget=forms.DateTimeInput(attrs={'type': 'date',
                                                  'class': 'form-control'})
            )


class FormControllClassMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            widget = self.fields[field].widget
            if hasattr(widget, 'input_type') and widget.input_type == 'checkbox':
                self.fields[field].widget.attrs = {'class': 'form-check-input'}
            else:
                self.fields[field].widget.attrs = {'class': 'form-control'}


class WizardForm(forms.Form, DispatchQuestionFieldTypeMixin):

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.options = kwargs.pop('options') or {}
        super().__init__(*args, **kwargs)

        if self.question:
            self.get_field_for_question_type(self.question, self.options, self.fields)
            self.fields['question'] = fields.CharField(
                initial=self.question.id,
                widget=forms.HiddenInput()
            )


class RenderedDocumentForm(forms.ModelForm):
    answer_id = fields.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Answer
        fields = ['rendered_document', 'answer_id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if TinyMCE:
            self.fields['rendered_document'].widget = TinyMCE(
                attrs={'cols': 80, 'rows': 30})
        self.fields['answer_id'].initial = self.instance.id


class DocumentForm(FormControllClassMixin, forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name']


class PrepareDocumentForm(forms.Form):
    name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        super().__init__(*args, **kwargs)
        if self.document:
            self.initial = model_to_dict(self.document)

    def save(self):
        if not self.document:
            document = Document.objects.create(
                **self.cleaned_data
            )
            return document
        else:
            name = self.cleaned_data.get('name')
            self.document.name = name
            self.document.save()
            return self.document


class QuestionForm(forms.Form, DispatchQuestionFieldTypeMixin):
    question = fields.CharField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = Question.objects.get(id=self.initial.get('question'))
        self.get_field_for_question_type(self.question, self.question.options, self.fields, False)

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date:
            return dateformat.format(date, "m.d.Y")


class QuestionConditionForm(FormControllClassMixin, forms.ModelForm):
    conditions = forms.CharField(required=False)
    default_next = forms.ChoiceField()

    class Meta:
        model = Question
        fields = ('default_next', 'conditions')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['conditions'].widget = ConditionsWidget(
            question=self.instance)
        if not self.instance.is_option_question():
            self.fields['default_next'].choices = self.get_choices()
            self.fields['default_next'].initial = self.get_default_next_initial()
            self.fields['default_next'].label = _('After this Question always ...')
            self.fields['conditions'].label = _('except for ...')
        else:
            del self.fields['default_next']

    def get_default_next_initial(self):
        if self.instance.id:
            if self.instance.is_last:
                return 'next'
            elif self.instance.next_question:
                return self.instance.next_question.id
            else:
                return 'default'

    def get_next_questionaire_choice(self):
        questionaire = self.instance.questionaire
        if questionaire.next():
            return ('next', _('Jump to next questionaire'))
        else:
            if questionaire.law_case.document:
                return ('next', _('Show result document'))
            else:
                return ('next', _('Show success message'))

    def get_choices(self):
        options = []
        other_questions = self.instance.questionaire.questions
        default_next = self.instance.get_children().first()
        if default_next:
            other_questions = other_questions.exclude(id=default_next.id)
            options.append(('default', _('Go to: {}').format(default_next.text)))
        options = options + [(question.id, _('Jump to: {}').format(question.text)) for question in other_questions]
        options.append(self.get_next_questionaire_choice())
        return options

    def save_default_next(self):
        if 'default_next' in self.cleaned_data:
            default_next = self.cleaned_data.get('default_next')
            if default_next == 'next':
                self.instance.next_question = None
                self.instance.is_last = True
            elif default_next == 'default':
                self.instance.is_last = False
                self.instance.next_question = None
            else:
                self.instance.is_last = False
                next_question = Question.objects.get(id=default_next)
                self.instance.next_question = next_question
            self.instance.save()

    def save(self, commit=True):
        self.save_default_next()
        if self.cleaned_data['conditions']:
            self.instance.conditions.all().delete()
            conditions = json.loads(self.cleaned_data.pop('conditions'))
            for condition in conditions:
                if 'id' in condition:
                    condition.pop('id')
                condition['question'] = self.instance
                if condition.get('then_value'):
                    if 'question' in condition.get('then_value'):
                        question_id = condition.get('then_question')
                        question = Question.objects.filter(
                            id=question_id).first()
                        if question:
                            condition['then_value'] = 'question'
                            condition['then_question'] = question
                    else:
                        if 'then_question' in condition:
                            condition.pop('then_question')
                    condition = Condition.objects.create(**condition)
        return self.instance


class QuestionUpdateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = Question
        fields = ('text', 'field_type', 'options', 'information')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['options'].widget = ChoiceWidget()
        question = self.instance
        if question.field_type not in [Question.SINGLE_OPTION,
                                       Question.YES_NO,
                                       Question.MULTIPLE_OPTIONS]:
            del self.fields['options']

    def save(self, commit=True):
        question = super().save(commit=commit)
        if 'options' in self.cleaned_data:
            options = self.cleaned_data.get('options').keys()
            question.clean_up_conditions(options)
        return question


class QuestionCreateForm(FormControllClassMixin, forms.ModelForm):
    parent_question = fields.CharField(required=False,
                                       widget=forms.HiddenInput)

    class Meta:
        model = Question
        fields = ('text', 'field_type')

    def __init__(self, **kwargs):
        if 'parent_question' in kwargs:
            self.parent_question = kwargs.pop('parent_question')
        super().__init__(**kwargs)
        if hasattr(self, 'parent_question') and self.parent_question:
            self.fields['parent_question'].initial = self.parent_question


class LawCaseCreateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = LawCase
        fields = ('title', 'description')


class LawCaseUpdateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = LawCase
        fields = ('title', 'description')


class QuestionaireForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = Questionaire
        fields = ('title', 'success_message')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.instance.law_case.questionaire_count() <= 1:
            del self.fields['title']


class QuestionaireCreateForm(FormControllClassMixin, forms.ModelForm):

    class Meta:
        model = Questionaire
        fields = ('title',)
