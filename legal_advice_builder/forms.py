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
from .models import DocumentField
from .models import DocumentFieldType
from .models import DocumentType
from .models import LawCase
from .models import Question
from .models import Questionaire
from .widgets import ChoiceWidget
from .widgets import ConditionsWidget


class DispatchQuestionFieldTypeMixin:

    def get_field_for_question_type(self, question, options, form_fields, required=True):
        if question.field_type in [question.SINGLE_OPTION, question.YES_NO]:
            form_fields['option'] = fields.ChoiceField(
                choices=options.items(),
                widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                required=required,
                label=question.text,
                help_text=question.help_text
            )
        elif question.field_type == question.MULTIPLE_OPTIONS:
            form_fields['option'] = fields.MultipleChoiceField(
                choices=options.items(),
                widget=forms.CheckboxSelectMultiple,
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


class DocumentFieldForm(forms.Form):
    field_type = fields.CharField(widget=forms.HiddenInput)
    document = fields.CharField(widget=forms.HiddenInput)
    content = fields.CharField(widget=TinyMCE(mce_attrs={
        'menubar': '',
        'force_br_newlines': False,
        'force_p_newlines': False,
        'forced_root_block': ''}),
        required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field_type_id = self.initial.get('field_type')
        if field_type_id:
            field_type = DocumentFieldType.objects.get(id=field_type_id)
            self.fields['content'].label = field_type.name
            self.fields['content'].help_text = field_type.help_text

    def save(self):
        data = self.cleaned_data
        content = data.pop('content')
        document_id = data.pop('document')
        field_type_id = data.pop('field_type')

        document = Document.objects.get(id=document_id)
        field_type = DocumentFieldType.objects.get(id=field_type_id)

        field, created = DocumentField.objects.get_or_create(
            field_type=field_type,
            document=document
        )
        field.content = content
        field.save()
        return field


class PrepareDocumentForm(forms.Form):
    name = forms.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop('document')
        super().__init__(*args, **kwargs)
        if not self.document:
            self.fields['document_type'] = forms.ModelChoiceField(
                queryset=DocumentType.objects.all())
        else:
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


class QuestionConditionForm(forms.ModelForm):
    conditions = forms.CharField(required=False)

    class Meta:
        model = Question
        fields = ('conditions', 'failure_message')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['conditions'].widget = ConditionsWidget(question=self.instance)
        question = self.instance
        if not question.condition_set.filter(then_value='failure'):
            del self.fields['failure_message']

    def save(self, commit=True):
        if self.cleaned_data['conditions']:
            self.instance.condition_set.all().delete()
            conditions = json.loads(self.cleaned_data.pop('conditions'))
            for condition in conditions:
                if 'id' in condition:
                    condition.pop('id')
                condition['question'] = self.instance
                if condition.get('then_value'):
                    condition = Condition.objects.create(**condition)
        if 'failure_message' in self.cleaned_data:
            self.instance.failure_message = self.cleaned_data['failure_message']
            self.instance.save()
        return self.instance


class QuestionUpdateForm(forms.ModelForm):

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


class QuestionCreateForm(forms.ModelForm):
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


class LawCaseCreateForm(forms.ModelForm):
    document_type = forms.ModelChoiceField(queryset=DocumentType.objects.all())

    class Meta:
        model = LawCase
        fields = ('title', 'document_type', 'description')


class LawCaseUpdateForm(forms.ModelForm):

    class Meta:
        model = LawCase
        fields = ('title', 'description')


class QuestionaireForm(forms.ModelForm):

    class Meta:
        model = Questionaire
        fields = ('title', 'success_message')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['success_message'].help_text = _('This message is '
                                                     'shown if the user has '
                                                     'reached the end '
                                                     'of this questionaire '
                                                     'successfully.')
