from django import forms
from django.forms import fields
from django.forms.models import model_to_dict
from tinymce.widgets import TinyMCE

from .models import Answer
from .models import Document
from .models import DocumentField
from .models import DocumentFieldType
from .models import DocumentType


class WizardForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.options = kwargs.pop('options') or {}
        super().__init__(*args, **kwargs)

        if self.question:
            if self.question.field_type == self.question.SINGLE_OPTION:
                self.fields['option'] = fields.ChoiceField(
                    choices=self.options.items(),
                    widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.MULTIPLE_OPTIONS:
                self.fields['option'] = fields.MultipleChoiceField(
                    choices=self.options.items(),
                    widget=forms.CheckboxSelectMultiple,
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.SINGLE_LINE:
                self.fields['text'] = fields.CharField(
                    widget=forms.TextInput(attrs={'class': 'form-control'}),
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.TEXT:
                self.fields['text'] = fields.CharField(
                    widget=forms.Textarea(attrs={'class': 'form-control'}),
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.DATE:
                self.fields['date'] = fields.DateField(
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text,
                    widget=forms.DateTimeInput(attrs={'type': 'date',
                                                      'class': 'form-control'})
                )
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
    content = fields.CharField(widget=forms.Textarea, required=False)

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
