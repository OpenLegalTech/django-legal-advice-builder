from django import forms
from django.forms import fields

from .models import Answer


class WizardForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.question = kwargs.pop('question')
        super().__init__(*args, **kwargs)

        if self.question:
            if self.question.field_type == self.question.SINGLE_OPTION:
                self.fields['option'] = fields.ChoiceField(
                    choices=self.question.options.items(),
                    widget=forms.RadioSelect,
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
                    help_text=self.question.help_text
                )
            self.fields['question'] = fields.CharField(
                initial=self.question.id,
                widget=forms.HiddenInput()
            )

    # def clean_date(self):
    #     return str(self.cleaned_data.get('date'))


class DocumentForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['rendered_document']
