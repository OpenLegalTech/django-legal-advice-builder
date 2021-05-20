from django import forms
from django.forms import fields

try:
    from tinymce.widgets import TinyMCE
except ModuleNotFoundError:
    pass

from .models import Answer


class WizardForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        self.options = kwargs.pop('options') or {}
        super().__init__(*args, **kwargs)

        if self.question:
            if self.question.field_type == self.question.SINGLE_OPTION:
                self.fields['option'] = fields.ChoiceField(
                    choices=self.options.items(),
                    widget=forms.RadioSelect,
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
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.TEXT:
                self.fields['text'] = fields.CharField(
                    widget=forms.Textarea,
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text
                )
            elif self.question.field_type == self.question.DATE:
                self.fields['date'] = fields.DateField(
                    required=True,
                    label=self.question.text,
                    help_text=self.question.help_text,
                    widget=forms.DateTimeInput(attrs={'type': 'date'})
                )
            self.fields['question'] = fields.CharField(
                initial=self.question.id,
                widget=forms.HiddenInput()
            )


class DocumentForm(forms.ModelForm):
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
