import json

from django import forms
from django.utils.translation import gettext_lazy as _


class ChoiceWidget(forms.TextInput):
    template_name = 'legal_advice_builder/admin/choices_widget_template.html'

    class Media:
        js = ('choice_field.js',)


class ConditionsWidget(forms.TextInput):
    template_name = 'legal_advice_builder/admin/conditions_widget_template.html'

    class Media:
        js = ('conditions_field.js',)

    def __init__(self, attrs=None, question=None):
        self.question = question
        return super().__init__(attrs=attrs)

    def create_conditions_dict(self):
        return {
            'success': self.question.success_conditions,
            'failure': self.question.failure_conditions
        }

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({
            'conditions': json.dumps(self.create_conditions_dict()),
            'options': self.question.options,
            'text': {
                'if': _('If the answer to this question is:'),
                'then': _('then')
            }
        })
        return context
