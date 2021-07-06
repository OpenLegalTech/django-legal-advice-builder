import json

from django import forms
from django.forms.models import model_to_dict
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

    def get_other_questions(self):
        questions = self.question.questionaire.questions.exclude(
            id=self.question.id)
        return [{'id': question.id,
                 'text': question.text} for question in questions]

    def create_conditions_dict(self):
        conditions = [
            model_to_dict(condition) for condition in self.question.condition_set.all()
        ]
        return conditions

    def get_then_options(self):
        return {
            'success': str(_('success: Jump to next questionaire.')),
            'failure': str(_('failure: show failure message')),
            'question': str(_('jump to question:'))
        }

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({
            'conditions': json.dumps(self.create_conditions_dict()),
            'questions': json.dumps(self.get_other_questions()),
            'question_id': str(self.question.id),
            'options': self.question.options,
            'then_options': json.dumps(self.get_then_options()),
            'text': {
                'if': _('If the answer to this question is:'),
                'then': _('then')
            }
        })
        return context
