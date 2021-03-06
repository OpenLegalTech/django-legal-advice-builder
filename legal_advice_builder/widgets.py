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
            model_to_dict(condition) for condition in self.question.conditions.all()
        ]
        return conditions

    def get_if_options(self):
        return self.question.get_options_by_type()

    def get_then_options(self):
        res = {
            'failure': str(_('failure: show failure message')),
        }
        if self.get_other_questions():
            res['question'] = str(_('jump to question:'))

        questionaire = self.question.questionaire
        if questionaire.next():
            res['success'] = str(_('Jump to next questionaire'))
        else:
            if questionaire.law_case.document:
                res['success'] = str(_('Show result document'))
            else:
                res['success'] = str(_('Show success message'))
        return res

    def get_period_options(self):
        return {
            'days': str(_('Days')),
            'months': str(_('Months')),
            'years': str(_('years'))
        }

    def get_default_next(self):
        children = self.question.get_children()
        if children:
            return children.first().id
        return ''

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update({
            'initial': json.dumps(self.create_conditions_dict()),
            'questions': json.dumps(self.get_other_questions()),
            'default_next': self.get_default_next(),
            'question_id': str(self.question.id),
            'if_options': json.dumps(self.get_if_options()),
            'options': json.dumps(self.question.options),
            'then_options': json.dumps(self.get_then_options()),
            'period_options': json.dumps(self.get_period_options()),
            'question_type': self.question.field_type,
            'text': json.dumps({
                'if': str(self.question.get_if_text_by_type()),
                'then': str(_('then'))
            })
        })
        return context


class CustomRadioSelect(forms.RadioSelect):
    template_name = 'legal_advice_builder/admin/custom_select.html'


class CustomCheckboxSelect(forms.CheckboxSelectMultiple):
    template_name = 'legal_advice_builder/admin/custom_select.html'
